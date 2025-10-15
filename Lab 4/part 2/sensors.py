import random
import board
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_apds9960.apds9960 import APDS9960
import qwiic_joystick

joystick = qwiic_joystick.QwiicJoystick()
i2c = board.I2C()

apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True
gesture = apds  

seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
# button = digitalio.DigitalIO(seesaw, 24)
# button_held = False

encoder = rotaryio.IncrementalEncoder(seesaw)
# last_position = None

# --- MOCK HARDWARE CLASSES ---

class MockAPDS9960:
    """Mocks the APDS9960 gesture sensor."""
    def __init__(self):
        # Initialize with dummy values
        self.i2c = None
        self.enable_proximity = True
        self.enable_gesture = True
        self._throw_event = 0
        
    def gesture(self):
        """Returns 0x01 (UP) once every 100 calls to simulate a random throw."""
        self._throw_event = (self._throw_event + 1) % 100
        if self._throw_event == 1:
            return 0x01 # Simulate UP swipe
        return 0x00

class MockQwiicJoystick:
    """Mocks the Qwiic Joystick."""
    def __init__(self):
        self.connected = True
        self.version = "1.0"
        self._x = 512 # Start centered
        
    def begin(self):
        pass # No initialization needed for mock
        
    @property
    def horizontal(self):
        """Simulates left/right stick movement (0 to 1023)."""
        # Introduce slow, random drift to simulate natural movement/noise
        drift = random.randint(-5, 5)
        self._x = max(0, min(1023, self._x + drift))
        return self._x

    @property
    def vertical(self):
        return 512 # Center Y

    @property
    def button(self):
        return 1 # Button unpressed

class MockRotaryEncoder:
    """Mocks the rotary encoder."""
    def __init__(self):
        self.position = 0
        self._change_event = 0
        
    def update(self):
        """Simulates a slow, random rotation change."""
        self._change_event = (self._change_event + 1) % 30
        if self._change_event == 0:
            self.position += random.choice([-1, 0, 0, 1])
        return self.position
    
# Helper function to initialize mock sensors
def initialize_mock_sensors():
    """Initializes and connects the mock sensor objects."""
    joystick = MockQwiicJoystick()

    gesture = MockAPDS9960()

    # We use a simple class for the encoder mock to handle position updates easily
    class MockEncoderContainer:
        def __init__(self):
            self.encoder = MockRotaryEncoder()
            # self.encoder = encoder

            self.last_position = 0
            
    encoder_container = MockEncoderContainer()
   

    return joystick, gesture, encoder_container
