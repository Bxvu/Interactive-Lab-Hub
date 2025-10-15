from __future__ import print_function
import board
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_apds9960.apds9960 import APDS9960
import qwiic_joystick
import time
import sys

# For use with the STEMMA connector on QT Py RP2040
# import busio
# i2c = busio.I2C(board.SCL1, board.SDA1)
# seesaw = seesaw.Seesaw(i2c, 0x36)

myJoystick = qwiic_joystick.QwiicJoystick()

if myJoystick.connected == False:
	print("The Qwiic Joystick device isn't connected to the system. Please check your connection", \
		file=sys.stderr)
	myJoystick.begin()

i2c = board.I2C()

apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True

seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
	print("Wrong firmware loaded?  Expected 4991")

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)
button_held = False

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

while True:

	# negate the position to make clockwise rotation positive
	position = -encoder.position

	if position != last_position:
		last_position = position
		print("Position: {}".format(position))

	if not button.value and not button_held:
		button_held = True
		print("Button pressed")

	if button.value and button_held:
		button_held = False
		print("Button released")


	gesture = apds.gesture()

	if gesture == 0x01:
		print("up")
	elif gesture == 0x02:
		print("down")
	elif gesture == 0x03:
		print("left")
	elif gesture == 0x04:
		print("right")


	print("X: %d, Y: %d, Button: %d" % ( \
					myJoystick.horizontal, \
					myJoystick.vertical, \
					myJoystick.button))


