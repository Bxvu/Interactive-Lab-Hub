import time
import subprocess
import digitalio
import board
import math
import random
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from datetime import datetime
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from struct import pack, unpack

# --- I2C Button Setup ---
DEVICE_ADDRESS = 0x6f  # device address of our button
STATUS = 0x03 # register for button status
# Bitmasks for button status
AVAILIBLE = 0x01
BEEN_CLICKED = 0x02
IS_PRESSED = 0x04

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

# Clear out the I2C button's LED settings to start
write_register(device, 0x1A, 1)      # Set LED mode to manual
write_register(device, 0x1B, 0, 2)   # Set brightness to 0
write_register(device, 0x19, 0)      # Turn off LED color

# --- Display Setup ---
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000
spi = board.SPI()
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)
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

# --- App State and Configuration ---
FOCUS_STATE = "FOCUS"
BREAK_STATE = "BREAK"
current_state = FOCUS_STATE

# Default durations in seconds
default_focus_seconds = 25 * 60  # 25 minutes
default_break_seconds = 5 * 60   # 5 minutes

# Timer variables
remaining_seconds = default_focus_seconds
is_paused = True 
last_tick_time = time.monotonic()

# UI/UX variables
FOCUS_BG = "#db4f4f" # A red-ish color for focus
BREAK_BG = "#4fdb7b" # A green-ish color for break
TEXT_COLOR = "#FFFFFF"
NOTIFICATION_DURATION = 3 # seconds
notification_text = "Press any button to start"
notification_end_time = time.monotonic() + 9999

def display_notification(message):
    """Sets a message to be displayed for a short duration."""
    global notification_text, notification_end_time
    notification_text = message
    notification_end_time = time.monotonic() + NOTIFICATION_DURATION

# --- Main Application Loop ---
while True:
    a_pressed = not buttonA.value
    b_pressed = not buttonB.value
    
    btn_status = read_register(device, STATUS)
    c_clicked = (btn_status & BEEN_CLICKED) != 0
    if c_clicked:
        write_register(device, STATUS, 0)

    if notification_end_time < time.monotonic(): 
        notification_text = ""

    a_pressed = not buttonA.value
    b_pressed = not buttonB.value

    if a_pressed and b_pressed:
        if current_state == FOCUS_STATE:
            default_focus_seconds = remaining_seconds
            display_notification(f"Next Focus: {int(remaining_seconds // 60):02}:{int(remaining_seconds % 60):02}")
        else: # BREAK_STATE
            default_break_seconds = remaining_seconds
            display_notification(f"Next Break: {int(remaining_seconds // 60):02}:{int(remaining_seconds % 60):02}")
        time.sleep(0.5)

    # If only button A is pressed, wait briefly to see if B will also be pressed
    elif a_pressed:
        time.sleep(0.075)
        # Re-check the other button's state
        if not buttonB.value:
            # B was pressed too, so this is a "both" press. Do nothing and let the next loop handle it.
            pass
        else:
            # It was a genuine single press.
            remaining_seconds += 60
            notification_text = ""
            time.sleep(0.2) # Debounce for the single press

    elif b_pressed:
        time.sleep(0.075)
        # Re-check the other button's state
        if not buttonA.value:
            # A was pressed too, so this is a "both" press. Do nothing.
            pass
        else:
            # It was a genuine single press.
            remaining_seconds = max(0, remaining_seconds - 60)
            notification_text = ""
            time.sleep(0.2)

    if c_clicked:
        is_paused = not is_paused
        notification_text = ""
        
    if not is_paused:
        # Turn on the I2C button's LED to indicate the timer is running
        write_register(device, 0x19, 100)
        
        current_time = time.monotonic()
        delta_time = current_time - last_tick_time
        last_tick_time = current_time
        remaining_seconds -= delta_time
    else:
        # Turn off the LED when paused
        write_register(device, 0x19, 0)
        last_tick_time = time.monotonic()

    if remaining_seconds <= 0:
        if current_state == FOCUS_STATE:
            current_state = BREAK_STATE
            remaining_seconds = default_break_seconds
            display_notification("Break Time!")
        else:
            current_state = FOCUS_STATE
            remaining_seconds = default_focus_seconds
            display_notification("Focus Time!")
        is_paused = False

    bg_color = FOCUS_BG if current_state == FOCUS_STATE else BREAK_BG
    draw.rectangle((0, 0, width, height), fill=bg_color)
    
    minutes, seconds = divmod(int(remaining_seconds), 60)
    time_str = f"{minutes:02d}:{seconds:02d}"

    # Draw State Title
    state_bbox = draw.textbbox((0, 0), current_state, font=font)
    state_w = state_bbox[2] - state_bbox[0]
    # state_h = state_bbox[3] - state_bbox[1]
    draw.text(
        (width // 2 - state_w // 2, 10),
        current_state,
        font=font,
        fill=TEXT_COLOR,
    )

    # Draw Countdown Timer
    time_bbox = draw.textbbox((0, 0), time_str, font=large_font)
    time_w = time_bbox[2] - time_bbox[0]
    time_h = time_bbox[3] - time_bbox[1]
    draw.text(
        (width // 2 - time_w // 2, height // 2 - time_h // 2),
        time_str,
        font=large_font,
        fill=TEXT_COLOR,
    )
    
    # Draw Pause Indicator
    if is_paused and notification_text == "":
        pause_str = "PAUSED"
        pause_bbox = draw.textbbox((0,0), pause_str, font=font)
        pause_w = pause_bbox[2] - pause_bbox[0]
        draw.text(
            (width // 2 - pause_w // 2, height - 30),
            pause_str,
            font=font,
            fill=TEXT_COLOR,
        )

    # Draw Notification
    if notification_text:
        notif_bbox = draw.textbbox((0,0), notification_text, font=font)
        notif_w = notif_bbox[2] - notif_bbox[0]
        draw.text(
            (width // 2 - notif_w // 2, height - 30),
            notification_text,
            font=font,
            fill=TEXT_COLOR,
        )

    disp.image(image, rotation)