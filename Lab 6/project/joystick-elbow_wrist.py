from __future__ import print_function
import qwiic_joystick
import time
import sys
import paho.mqtt.client as mqtt
import json
import math # Added for angle calculations

# --- ADDED: Display Imports ---
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
# ---

# --- MQTT Configuration ---
MQTT_BROKER = "farlab.infosci.cornell.edu"
MQTT_PORT = 1883
MQTT_TOPIC = "IDD/robotarm" 
MQTT_USER = "idd"
MQTT_PASSWORD = "device@theFarm"

# --- Servo Configuration ---
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180

# --- Joystick Configuration ---
JOYSTICK_MIN = 0
JOYSTICK_MAX = 1023
JOYSTICK_CENTER = 512 # Assumes a 10-bit joystick (0-1023)
JOYSTICK_DEADZONE = 25 # +/- this value from center is treated as 0
SENSITIVITY = 0.5    # How fast the angle changes. Higher = faster.
LOOP_DELAY = 0.05    # Loop speed in seconds (20 Hz). Faster loop = smoother control.

# --- State Variables ---
# Store the current angle, starting at the middle position.
current_joint1_angle = (SERVO_MIN_ANGLE + SERVO_MAX_ANGLE) / 2
current_joint2_angle = (SERVO_MIN_ANGLE + SERVO_MAX_ANGLE) / 2

last_sent_joint1 = None
last_sent_joint2 = None
last_sent_button = None

# --- MQTT Setup ---
def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print(f"Connected to MQTT Broker: {MQTT_BROKER}")
	else:
		print("Failed to connect, return code %d\n" % rc)

try:
	client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
except AttributeError:
	print("Using legacy MQTT Client initialization.")
	client = mqtt.Client()

client.on_connect = on_connect

client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

try:
	client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
	print(f"Could not connect to MQTT broker: {e}", file=sys.stderr)
	sys.exit(1)

client.loop_start()

# --- Display Setup (Copied/Adapted from second file) ---

# Configuration for CS and DC pins (FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5) 
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate:
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
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

# Create blank image for drawing.
height = disp.width  # swap height/width for landscape
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load font
try:
	# Use the same font path from the second file
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except IOError:
	print("Default font not found, using a basic bitmap font.")
	font = ImageFont.load_default()

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# --- Visual Arm Parameters ---
ARM_SEGMENT_LENGTH = 50 # Length of each arm segment
BASE_X, BASE_Y = width // 2, height - 10 # Base of the arm on the screen
JOINT_THICKNESS = 3
JOINT_COLOR = (0, 255, 0) # Green for the arm
WHITE = (255, 255, 255)

# --- Main Program Logic ---
def runExample():
	global current_joint1_angle, current_joint2_angle
	global last_sent_joint1, last_sent_joint2, last_sent_button
	
	# Get display variables from the global scope for use in loop
	global image, draw, disp, rotation, width, height, font, BASE_X, BASE_Y

	myJoystick = qwiic_joystick.QwiicJoystick()

	if myJoystick.connected == False:
		print("The Qwiic Joystick device isn't connected...", file=sys.stderr)
		# Do not return here to allow the display to still run if joystick isn't essential
		pass 

	myJoystick.begin()

	while True:
		# Read raw joystick values
		x_val = myJoystick.horizontal
		y_val = myJoystick.vertical
		button_val = myJoystick.button

		# 1. Calculate "speed" by subtracting the center
		x_speed = x_val - JOYSTICK_CENTER
		y_speed = y_val - JOYSTICK_CENTER
		
		# 2. Apply the dead zone
		if abs(x_speed) < JOYSTICK_DEADZONE:
			x_speed = 0
		if abs(y_speed) < JOYSTICK_DEADZONE:
			y_speed = 0

		# 3. Calculate the change (delta) based on speed and sensitivity
		if x_speed != 0:
			delta_joint1 = x_speed * SENSITIVITY * LOOP_DELAY
			current_joint1_angle += delta_joint1

		if y_speed != 0:
			delta_joint2 = y_speed * SENSITIVITY * LOOP_DELAY
			current_joint2_angle += delta_joint2
			
		# 4. Clamp the angles to stay within servo limits
		current_joint1_angle = max(SERVO_MIN_ANGLE, min(current_joint1_angle, SERVO_MAX_ANGLE))
		current_joint2_angle = max(SERVO_MIN_ANGLE, min(current_joint2_angle, SERVO_MAX_ANGLE))

		# Get the integer values for comparison and MQTT
		int_joint1 = int(current_joint1_angle)
		int_joint2 = int(current_joint2_angle)
		
		# --- MQTT Logic (Send if any state changed) ---
		if (int_joint1 != last_sent_joint1) or \
		   (int_joint2 != last_sent_joint2) or \
		   (button_val != last_sent_button):
			
			# 5. Create JSON payload
			payload_data = {
				"elbow": int_joint1,
				"wrist": int_joint2,
				"button": button_val
			}
			json_payload = json.dumps(payload_data)
			
			# 6. Publish the message
			client.publish(MQTT_TOPIC, json_payload)

			print(f"Sending: Elbow: {int_joint1}, Wrist: {int_joint2}")

			# 7. Update the last sent state
			last_sent_joint1 = int_joint1
			last_sent_joint2 = int_joint2
			last_sent_button = button_val
		
		# --- ADDED: Display Logic with Visual Arm ---
		# Draw a black filled box to clear the image.
		draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

		# --- Calculate Arm Segment Endpoints ---
		# Joint 1 (Elbow) Angle: Convert to radians, adjust for screen orientation
		# 0 degrees usually points right, 90 up. We want 0-180 to sweep from left-up-right.
		# Start from straight up (90 degrees or math.pi/2), then add/subtract.
		# The servo angle is 0-180. We can map this directly.
		# A 0-degree servo angle might mean the arm is down/left, 90 straight up, 180 down/right.
		# Let's assume 90 degrees is straight up for visual ease.
		
		# For visualization, 0 might be left, 90 up, 180 right.
		# Screen Y increases downwards.
		# A simple mapping for a horizontal sweep for joint1:
		# Map 0-180 to an angle from 180 to 0 degrees in standard math (or pi to 0 radians)
		# This makes 0 degrees point left, 90 degrees up, 180 degrees right on screen
		elbow_angle_rad = math.radians(180 - int_joint1) 

		elbow_end_x = BASE_X + ARM_SEGMENT_LENGTH * math.cos(elbow_angle_rad)
		elbow_end_y = BASE_Y - ARM_SEGMENT_LENGTH * math.sin(elbow_angle_rad) # Subtract for screen Y

		# Joint 2 (Wrist) Angle: Relative to the elbow's angle.
		# If the wrist servo angle is 0, it means it's straight relative to the elbow.
		# If it's 90, it's bent at 90 degrees *from the elbow's orientation*.
		# Let's try to make it bend "forward" from the elbow.
		# We can use the joint2 angle directly as an offset from the elbow's direction.
		# A common robot arm convention is that each joint's angle is relative to the previous link.
		# So, total angle for wrist segment = elbow_angle_rad + (wrist_angle_from_straight_ahead)
		# A 0-180 range for wrist servo. Let's make 90 degrees 'straight out' from elbow.
		# So, (int_joint2 - 90) will give -90 to +90 deviation from straight.
		
		wrist_relative_angle_rad = math.radians(int_joint2 - 90) # -90 to +90 degrees relative to elbow link
		wrist_absolute_angle_rad = elbow_angle_rad + wrist_relative_angle_rad

		wrist_end_x = elbow_end_x + ARM_SEGMENT_LENGTH * math.cos(wrist_absolute_angle_rad)
		wrist_end_y = elbow_end_y - ARM_SEGMENT_LENGTH * math.sin(wrist_absolute_angle_rad) # Subtract for screen Y

		# Draw the arm segments
		# Base to Elbow
		draw.line((BASE_X, BASE_Y, elbow_end_x, elbow_end_y), fill=JOINT_COLOR, width=JOINT_THICKNESS)
		# Elbow to Wrist
		draw.line((elbow_end_x, elbow_end_y, wrist_end_x, wrist_end_y), fill=JOINT_COLOR, width=JOINT_THICKNESS)

		# Draw circles for the joints
		JOINT_DOT_RADIUS = 4
		draw.ellipse((BASE_X - JOINT_DOT_RADIUS, BASE_Y - JOINT_DOT_RADIUS,
					  BASE_X + JOINT_DOT_RADIUS, BASE_Y + JOINT_DOT_RADIUS), fill=WHITE)
		draw.ellipse((elbow_end_x - JOINT_DOT_RADIUS, elbow_end_y - JOINT_DOT_RADIUS,
					  elbow_end_x + JOINT_DOT_RADIUS, elbow_end_y + JOINT_DOT_RADIUS), fill=WHITE)
		draw.ellipse((wrist_end_x - JOINT_DOT_RADIUS, wrist_end_y - JOINT_DOT_RADIUS,
					  wrist_end_x + JOINT_DOT_RADIUS, wrist_end_y + JOINT_DOT_RADIUS), fill=WHITE)

		# Define the text to display
		text_joint1 = f"Elbow: {int_joint1}°"
		text_joint2 = f"Wrist: {int_joint2}°"
		# text_button = f"Btn: {'P' if button_val == 0 else 'R'}" # Qwiic Button is active LOW

		# Set coordinates for text (top-left adjusted)
		padding = 5
		text_x = padding
		text_y = padding

		# Draw the text
		draw.text((text_x, text_y), text_joint1, font=font, fill=WHITE)
		draw.text((text_x, text_y + 20), text_joint2, font=font, fill=WHITE)
		# draw.text((text_x, text_y + 40), text_button, font=font, fill=WHITE)


		# Display image.
		disp.image(image, rotation)
		# --- End Display Logic ---

		# Sleep for a short time
		time.sleep(LOOP_DELAY)

if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Program")
		client.loop_stop()
		client.disconnect()
		sys.exit(0)