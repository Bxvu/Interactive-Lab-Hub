import time
import subprocess
import digitalio
import board
import math
import random
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5) 
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
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
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

buttonA = digitalio.DigitalInOut(board.D23)    # GPIO23 (PIN 16)
buttonB = digitalio.DigitalInOut(board.D24)    # GPIO24 (PIN 18)
# Use internal pull-ups; buttons then read LOW when pressed.
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)

angle = 0
rotation_speed = 0.5

ORBIT_RADIUS = 75
SUN_RADIUS = 15
MOON_RADIUS = 10
CENTER_X, CENTER_Y = width // 2, height

DAY_BG = (135, 206, 235)
NIGHT_BG = (15, 15, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
LIGHT_GRAY = (200, 200, 200)

clouds = []
cloud_image = Image.open("cloud.webp").convert("RGBA")
cloud_image = cloud_image.resize((30, 20))

while True:
    angle_rad = math.radians(angle)
    sun_y = CENTER_Y + ORBIT_RADIUS * math.sin(angle_rad)

    a_pressed = (buttonA.value == False)
    b_pressed = (buttonB.value == False)

    if a_pressed and b_pressed:
        rotation_speed = 5.0
    else:
        rotation_speed = 0.5

    if a_pressed and not b_pressed:
        if sun_y < CENTER_Y:
            draw.rectangle((0, 0, width, height), fill=NIGHT_BG)
        else:
            draw.rectangle((0, 0, width, height), fill=DAY_BG)
        moon_x = CENTER_X + ORBIT_RADIUS * math.cos(angle_rad)
        moon_y = CENTER_Y + ORBIT_RADIUS * math.sin(angle_rad)

        sun_x = CENTER_X + ORBIT_RADIUS * math.cos(angle_rad + math.pi)
        sun_y = CENTER_Y + ORBIT_RADIUS * math.sin(angle_rad + math.pi)
    else:
        if sun_y < CENTER_Y:
            draw.rectangle((0, 0, width, height), fill=DAY_BG)
        else:
            draw.rectangle((0, 0, width, height), fill=NIGHT_BG)
        sun_x = CENTER_X + ORBIT_RADIUS * math.cos(angle_rad)
        sun_y = CENTER_Y + ORBIT_RADIUS * math.sin(angle_rad)

        moon_x = CENTER_X + ORBIT_RADIUS * math.cos(angle_rad + math.pi)
        moon_y = CENTER_Y + ORBIT_RADIUS * math.sin(angle_rad + math.pi)

    if b_pressed and not a_pressed:
        direction = random.choice([-1, 1])
        start_y = random.randint(50, height - 50)
        new_cloud = {
            'x': 0 if direction == 1 else width,
            'y': random.randint(0, height // 4),
            'speed': random.uniform(0.5, 1.5),
            'direction': direction,
            'image': cloud_image
        }
        clouds.append(new_cloud)

    for cloud in clouds:
        cloud['x'] += cloud['speed'] * cloud['direction']
        draw.bitmap((cloud['x'], cloud['y']), cloud['image'], fill=WHITE)

    clouds = [cloud for cloud in clouds if 0 < cloud['x'] < width]

    draw.ellipse(
        (CENTER_X - ORBIT_RADIUS, CENTER_Y - ORBIT_RADIUS, 
         CENTER_X + ORBIT_RADIUS, CENTER_Y + ORBIT_RADIUS),
        outline=WHITE, width=1
    )
    draw.ellipse(
        (sun_x - SUN_RADIUS, sun_y - SUN_RADIUS,
         sun_x + SUN_RADIUS, sun_y + SUN_RADIUS),
        fill=YELLOW
    )
    draw.ellipse(
        (moon_x - MOON_RADIUS, moon_y - MOON_RADIUS,
         moon_x + MOON_RADIUS, moon_y + MOON_RADIUS),
        fill=LIGHT_GRAY
    )
    

    # Draw the time text
    # x = CENTER_X - 40
    # y = 0
    # draw.text((x, y), time.strftime("%m/%d/%y"), font=font, fill="#FFFFFF")
    # draw.text((x, y + 20), time.strftime("%I:%M %p"), font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)
    
    angle += rotation_speed
    if random.random() < 0.02:
        direction = random.choice([-1, 1])
        new_cloud = {
            'x': 0 if direction == 1 else width,
            'y': random.randint(0, height // 4),
            'speed': random.uniform(0.5, 1.5),
            'direction': direction,
            'image': cloud_image
        }
        clouds.append(new_cloud)
    time.sleep(0.01)