import board
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_apds9960.apds9960 import APDS9960
import qwiic_joystick
import sys

# Container class to hold the rotary encoder object and its state
class EncoderContainer:
    def __init__(self, encoder):
        self.encoder = encoder
        self.last_position = 0
        self.encoder.position = 0 # Ensure the starting position is 0

    def update(self):
        """Returns the current accumulated encoder position."""
        # Negate the position to make clockwise rotation positive
        position = -self.encoder.position
        
        # We only care about the absolute position for the game angle, 
        # so no need for button logic or printing here.
        self.last_position = position
        return position

def initialize_real_sensors():
    """
    Initializes and connects all physical sensors.
    
    Returns: joystick (QwiicJoystick), apds (APDS9960), encoder_container (EncoderContainer)
    """
    # --- Qwiic Joystick Setup ---
    myJoystick = qwiic_joystick.QwiicJoystick()

    if myJoystick.connected == False:
        print("Error: Qwiic Joystick not connected. Game may not function.")
        # Attempt to begin even if connection status is initially False, 
        # in case it connects later or is a soft failure.
    myJoystick.begin()

    # --- APDS-9960 Gesture Sensor Setup ---
    i2c = board.I2C()
    apds = APDS9960(i2c)
    apds.enable_proximity = True
    apds.enable_gesture = True

    # --- Seesaw Rotary Encoder Setup ---
    try:
        seesaw_device = seesaw.Seesaw(board.I2C(), addr=0x36)
        
        seesaw_product = (seesaw_device.get_version() >> 16) & 0xFFFF
        if seesaw_product != 4991:
            print(f"Warning: Rotary Encoder found product {seesaw_product}, expected 4991.")

        # Set up encoder and container
        encoder = rotaryio.IncrementalEncoder(seesaw_device)
        encoder_container = EncoderContainer(encoder)
        
        # You can ignore the button logic (pin 24) for now, as the game uses the gesture sensor for throwing.
    
    except Exception as e:
        print(f"Error initializing Seesaw Encoder: {e}. Game will use mock encoder behavior.")
        
        # Fallback Mock Encoder if the real one fails (so game doesn't crash)
        class MockEncoder:
            def __init__(self): self.position = 0
            def update(self): 
                self.position += 0.5 # Slow mock drift
                return self.position
        encoder_container = EncoderContainer(MockEncoder())

    return myJoystick, apds, encoder_container
