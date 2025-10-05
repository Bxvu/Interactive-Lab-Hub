from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
import time
import board
import math
import subprocess

# For earlier years:
# from adafruit_msa3xx import MSA311
# import adafruit_mpu6050

i2c = board.I2C()  # Pi 5 compatible
# i2c = busio.I2C(board.SCL, board.SDA)  # Alternative for older setups

# Initialize sensor - uncomment the one you're using
sensor = LSM6DS3(i2c)  # Fall 2025+

# Initialize variables for petting detection
rolling_window = []
window_size = 10  # Number of recent acceleration magnitudes to track
petting_threshold = 5.0  # Adjust this value based on your setup
last_petting_time = 0
petting_cooldown = 1.0  # Minimum time (in seconds) between petting detections

while True:
    accel_x, accel_y, accel_z = sensor.acceleration
    gyro_x, gyro_y, gyro_z = sensor.gyro

    # Calculate the magnitude of acceleration
    magnitude = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

    # Add the magnitude to the rolling window
    rolling_window.append(magnitude)
    if len(rolling_window) > window_size:
        rolling_window.pop(0)

    # Calculate the average magnitude in the rolling window
    if len(rolling_window) == window_size:
        avg_magnitude = sum(rolling_window) / window_size
        change = abs(magnitude - avg_magnitude)

        # Check if the change exceeds the petting threshold
        current_time = time.monotonic()
        if change > petting_threshold and (current_time - last_petting_time > petting_cooldown):
            print("Petting detected! Quack quack!")
            # Play a quack noise (replace with your quack-playing logic)
            subprocess.run(["aplay", "quack_noises/quack1.wav"], check=False)
            last_petting_time = current_time

    print(f"Acceleration (m/s^2): X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f}")
    print(f"Gyro (rad/s): X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")
    print("-----")
    time.sleep(0.1)