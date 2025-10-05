# desk_buddy.py

import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import qwiic_proximity
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
import subprocess

# --- I2C Button Setup ---
DEVICE_ADDRESS = 0x6f
STATUS = 0x03
BEEN_CLICKED = 0x02
i2c = busio.I2C(board.SCL, board.SDA)
device = I2CDevice(i2c, DEVICE_ADDRESS)
def write_register(dev, register, value, n_bytes=1):
    buf = bytearray(1 + n_bytes)
    buf[0] = register
    buf[1:] = value.to_bytes(n_bytes, 'little')
    with dev:
        dev.write(buf)
def read_register(dev, register, n_bytes=1):
    reg = register.to_bytes(1, 'little')
    buf = bytearray(n_bytes)
    with dev:
        dev.write_then_readinto(reg, buf)
    return int.from_bytes(buf, 'little')
write_register(device, 0x1A, 1)
write_register(device, 0x1B, 0, 2)
write_register(device, 0x19, 0)
# --- Display Setup ---
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000
spi = board.SPI()
disp = st7789.ST7789(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, width=135, height=240, x_offset=53, y_offset=40)
height = disp.width
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
# --- Backlight and GPIO Button Setup ---
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)

class FocusTimer:
    def __init__(self, command_queue, audio_queue):
        self.command_queue = command_queue
        self.audio_queue = audio_queue
        # --- App State and Configuration ---
        self.FOCUS_STATE = "FOCUS"
        self.BREAK_STATE = "BREAK"
        self.current_state = self.FOCUS_STATE
        self.default_focus_seconds = 25 * 60
        self.default_break_seconds = 5 * 60
        self.remaining_seconds = self.default_focus_seconds
        self.is_paused = True
        self.last_tick_time = time.monotonic()
        # --- UI/UX variables ---
        self.FOCUS_BG = "#db4f4f"
        self.BREAK_BG = "#4fdb7b"
        self.TEXT_COLOR = "#FFFFFF"
        self.NOTIFICATION_DURATION = 3
        self.notification_text = "Press any button to start"
        self.notification_end_time = time.monotonic() + 9999

        # --- Proximity Sensor Setup ---
        self.proximity_sensor = qwiic_proximity.QwiicProximity()
        if not self.proximity_sensor.connected:
            print("Proximity sensor not connected. Please check the connection.")
        else:
            self.proximity_sensor.begin()
        self.proximity_threshold = 500  # Adjust this value based on your setup
        self.last_proximity_alert_time = 0  # Track the last time a reminder was sent
        self.proximity_alert_interval = 60  # Minimum interval between reminders (in seconds)

        # --- Accelerometer Setup ---
        i2c = board.I2C()
        self.accelerometer = LSM6DS3(i2c)
        self.pet_threshold = 15  # Adjust this value based on your setup
        self.last_pet_time = 0  # Track the last time a petting action was detected
        self.pet_cooldown = 5  # Minimum interval between pet detections (in seconds)

    def display_notification(self, message):
        self.notification_text = message
        self.notification_end_time = time.monotonic() + self.NOTIFICATION_DURATION

    def process_voice_command(self, command):
        """Parses and acts on commands from the voice assistant."""
        print(f"Timer received command: {command}")
        if command == 'PAUSE':
            self.is_paused = True
        elif command == 'RESUME':
            self.is_paused = False
        elif command == 'SAVE':
            if self.current_state == self.FOCUS_STATE:
                self.default_focus_seconds = self.remaining_seconds
                self.display_notification(f"Next Focus: {int(self.remaining_seconds // 60):02}:{int(self.remaining_seconds % 60):02}")
            else:
                self.default_break_seconds = self.remaining_seconds
                self.display_notification(f"Next Break: {int(self.remaining_seconds // 60):02}:{int(self.remaining_seconds % 60):02}")
        elif command.startswith('+'):
            minutes = int(command[1:])
            self.remaining_seconds += minutes * 60
        elif command.startswith('-'):
            minutes = int(command[1:])
            self.remaining_seconds = max(0, self.remaining_seconds - (minutes * 60))

    def monitor_proximity(self):
        """Check the proximity sensor during break time."""
        if self.current_state == self.BREAK_STATE and not self.is_paused:
            current_time = time.monotonic()
            if current_time - self.last_proximity_alert_time >= self.proximity_alert_interval:
                prox_value = self.proximity_sensor.get_proximity()
                print(f"Proximity Value: {prox_value}")
                if prox_value > self.proximity_threshold:
                    self.audio_queue.put("REMIND_MOVE")
                    self.last_proximity_alert_time = current_time

    def detect_petting(self):
        """Detect petting action using the accelerometer."""
        try:
            accel_x, accel_y, accel_z = self.accelerometer.acceleration
            magnitude = (accel_x**2 + accel_y**2 + accel_z**2)**0.5
            current_time = time.monotonic()

            # Check if the magnitude exceeds the threshold and cooldown has passed
            if magnitude > self.pet_threshold and (current_time - self.last_pet_time) > self.pet_cooldown:
                self.audio_queue.put("PET_DETECTED")
                self.last_pet_time = current_time
        except Exception as e:
            print(f"Error reading accelerometer: {e}")

    def run(self):
        while True:
            # Check for commands from the voice assistant
            if not self.command_queue.empty():
                command = self.command_queue.get()
                self.process_voice_command(command)

            # Monitor proximity sensor during break time
            self.monitor_proximity()

            # Detect petting action
            self.detect_petting()

            # 2. Update State based on Inputs
            if self.notification_end_time < time.monotonic(): # Clear notification once expired
                self.notification_text = ""
            # Read button states at the start of the logic block
            a_pressed = not buttonA.value
            b_pressed = not buttonB.value
            btn_status = read_register(device, STATUS)
            c_clicked = (btn_status & BEEN_CLICKED) != 0
            if c_clicked:
                write_register(device, STATUS, 0) # Clear the click status
            # First, handle the simultaneous press case
            if a_pressed and b_pressed:
                if self.current_state == self.FOCUS_STATE:
                    self.default_focus_seconds = self.remaining_seconds
                    self.display_notification(f"Next Focus: {int(self.remaining_seconds // 60):02}:{int(self.remaining_seconds % 60):02}")
                else: # BREAK_STATE
                    self.default_break_seconds = self.remaining_seconds
                    self.display_notification(f"Next Break: {int(self.remaining_seconds // 60):02}:{int(self.remaining_seconds % 60):02}")
                time.sleep(0.5)
            # If only button A is pressed, wait briefly to see if B will also be pressed
            elif a_pressed:
                time.sleep(0.075) # Wait 75ms
                if not buttonB.value:
                    pass
                else:
                    self.remaining_seconds += 60
                    self.notification_text = ""
                    time.sleep(0.2) # Debounce for the single press
            # Symmetrical logic for button B
            elif b_pressed:
                time.sleep(0.075) # Wait 75ms
                if not buttonA.value:
                    pass
                else:
                    self.remaining_seconds = max(0, self.remaining_seconds - 60)
                    self.notification_text = ""
                    time.sleep(0.2)
            # Handle pause/unpause from button C
            if c_clicked:
                self.is_paused = not self.is_paused
                self.notification_text = ""
            
            # 3. Update Timer Countdown
            if not self.is_paused:
                write_register(device, 0x19, 100)
                current_time = time.monotonic()
                delta_time = current_time - self.last_tick_time
                self.last_tick_time = current_time
                self.remaining_seconds -= delta_time
            else:
                write_register(device, 0x19, 0)
                self.last_tick_time = time.monotonic()
            # 4. Handle State Transitions
            if self.remaining_seconds <= 0:
                if self.current_state == self.FOCUS_STATE:
                    self.current_state = self.BREAK_STATE
                    self.remaining_seconds = self.default_break_seconds
                    self.display_notification("Break Time!")
                    self.audio_queue.put("START_BREAK")
                else:
                    self.current_state = self.FOCUS_STATE
                    self.remaining_seconds = self.default_focus_seconds
                    self.display_notification("Focus Time!")
                    self.audio_queue.put("START_FOCUS")
                self.is_paused = False
            # 5. Draw Everything
            bg_color = self.FOCUS_BG if self.current_state == self.FOCUS_STATE else self.BREAK_BG
            draw.rectangle((0, 0, width, height), fill=bg_color)
            minutes, seconds = divmod(int(self.remaining_seconds), 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            state_bbox = draw.textbbox((0, 0), self.current_state, font=font)
            state_w = state_bbox[2] - state_bbox[0]
            draw.text((width // 2 - state_w // 2, 10), self.current_state, font=font, fill=self.TEXT_COLOR)
            time_bbox = draw.textbbox((0, 0), time_str, font=large_font)
            time_w = time_bbox[2] - time_bbox[0]
            time_h = time_bbox[3] - time_bbox[1]
            draw.text((width // 2 - time_w // 2, height // 2 - time_h // 2), time_str, font=large_font, fill=self.TEXT_COLOR)
            if self.is_paused and self.notification_text == "":
                pause_str = "PAUSED"
                pause_bbox = draw.textbbox((0,0), pause_str, font=font)
                pause_w = pause_bbox[2] - pause_bbox[0]
                draw.text((width // 2 - pause_w // 2, height - 30), pause_str, font=font, fill=self.TEXT_COLOR)
            if self.notification_text:
                notif_bbox = draw.textbbox((0,0), self.notification_text, font=font)
                notif_w = notif_bbox[2] - notif_bbox[0]
                draw.text((width // 2 - notif_w // 2, height - 30), self.notification_text, font=font, fill=self.TEXT_COLOR)
            disp.image(image, rotation)