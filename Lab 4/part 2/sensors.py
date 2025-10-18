import board
import time
import sys
import threading
import random
from types import SimpleNamespace

# I2C Libraries
try:
    import adafruit_pcf8574
    import qwiic_joystick
    from adafruit_apds9960.apds9960 import APDS9960
    from adafruit_seesaw import seesaw, rotaryio
except ImportError:
    print("Warning: Hardware libraries not found. Using dummy sensors.")

# ----------------------------------------------------------------------
# I2C Address Constants
# We assume the Qwiic Joystick is at 0x20 and the PCF8574 is jumpered to 0x21
# GESTURE_UP constant for use in bowling_game.py
# ----------------------------------------------------------------------
PCF_I2C_ADDR_A = 0x21 
PCF_I2C_ADDR_B = 0x20 
GESTURE_UP = 0x01


# ----------------------------------------------------------------------
# DUMMY CLASSES for Robustness
# ----------------------------------------------------------------------

# Dummy for PCF8574 Pin
class DummyPin:
    def __init__(self, index):
        self.index = index
    def switch_to_output(self, value=True): pass
    @property
    def value(self): return True
    @value.setter
    def value(self, val): pass

# Dummy for PCF8574
class DummyPCF:
    def __init__(self):
        self.leds = [DummyPin(i) for i in range(8)]
    def get_pin(self, index):
        return self.leds[index]

# Dummy for Joystick
class DummyJoystick:
    @property
    def connected(self): return False
    def begin(self): pass
    @property
    def horizontal(self): return 512
    @property
    def vertical(self): return 512
    @property
    def button(self): return 1

# Dummy for Gesture Sensor
class DummyAPDS:
    def enable_proximity(self, value): pass
    def enable_gesture(self, value): pass
    def gesture(self): return 0

# Dummy for Seesaw Encoder
class DummyEncoder:
    def __init__(self):
        self._position = 0
    def update(self):
        # Simulate gentle, centering drift when using dummy
        if random.random() < 0.1:
            self._position += random.choice([-1, 0, 1])
        return self._position
    @property
    def position(self): return self._position
    @position.setter
    def position(self, val): 
        # Setter implemented to prevent AttributeError in reset_game()
        self._position = val 

class DummySeesaw:
    def __init__(self):
        self.encoder = DummyEncoder()
        self.last_position = 0
    def get_version(self): return 4991 << 16 # Mock version
    def pin_mode(self, pin, mode): pass
    def update(self): 
        # Update logic needed by bowling_game
        position = self.encoder.position
        if position != self.last_position:
            # Restrict position to be within -20 to +20 for game use
            if position < -20:
                position = -20
                self.encoder.position = -position  # Update encoder to reflect clamped value
            elif position > 20:
                position = 20
                self.encoder.position = -position
        return position

# ----------------------------------------------------------------------
# SHARED STATE CONTAINER
# ----------------------------------------------------------------------

class HardwareState(SimpleNamespace):
    """Container for shared sensor data and control flags."""
    def __init__(self):
        super().__init__(
            running=True,
            joystick_x=512,
            encoder_pos=0,
            gesture=0,
            win_flag=False,
            # LED Control
            pcf_leds=None,
            pcf_initialized=False,
            led_pattern_state=0 # 0 or 1 for alternating pattern
        )

# ----------------------------------------------------------------------
# BACKGROUND POLLING THREAD
# ----------------------------------------------------------------------

class SensorPollingThread(threading.Thread):
    def __init__(self, state, joystick, apds, encoder_container, pcf):
        super().__init__()
        self.state = state
        self.joystick = joystick
        self.apds = apds
        self.encoder_container = encoder_container
        self.pcf = pcf
        
    def run(self):
        """Main loop for polling hardware and updating shared state."""
        print("Sensor Polling Thread started...")
        last_led_update = time.monotonic()
        
        while self.state.running:
            try:
                # 1. Joystick (X-axis)
                self.state.joystick_x = self.joystick.horizontal
                
                # 2. Rotary Encoder
                self.state.encoder_pos = self.encoder_container.update()

                # 3. Gesture Sensor (Non-blocking as much as possible)
                gesture = self.apds.gesture()
                if gesture != 0:
                    self.state.gesture = gesture

                # 4. LED Control (only if initialized)
                if self.state.pcf_initialized:
                    current_time = time.monotonic()
                    
                    if self.state.win_flag:
                         # Flash while winning
                         if current_time - last_led_update > 0.1: # Flash speed (100ms)
                            self.update_leds_flashing()
                            self.state.led_pattern_state = 1 - self.state.led_pattern_state # Toggle state
                            last_led_update = current_time
                    else:
                        # Ensure OFF state if not winning
                        self.update_leds_off()
                        # Reset pattern state when not winning
                        self.state.led_pattern_state = 0 
                        last_led_update = current_time # Reset time check

            except Exception as e:
                pass
            
            # Control polling rate
            time.sleep(0.005)

    def update_leds_flashing(self):
        """Toggles the LED pattern between odd/even pins."""
        
        # LEDs are LOW-active (False = ON, True = OFF)
        
        if self.state.led_pattern_state == 0:
            # Pattern 0: Even pins (0, 2, 4, 6) ON, Odd pins (1, 3, 5, 7) OFF
            for i in range(8):
                if i % 2 == 0:
                    self.pcf.leds[i].value = False # ON
                else:
                    self.pcf.leds[i].value = True  # OFF
        else:
            # Pattern 1: Odd pins (1, 3, 5, 7) ON, Even pins (0, 2, 4, 6) OFF
            for i in range(8):
                if i % 2 != 0:
                    self.pcf.leds[i].value = False # ON
                else:
                    self.pcf.leds[i].value = True  # OFF
        
    def update_leds_off(self):
        """Ensures all LEDs are OFF."""
        # --- FIX: Iterate and force all LEDs OFF (HIGH) ---
        for ld in self.pcf.leds:
             ld.value = True # Turn OFF (HIGH)
        # ----------------------------------------------------


# ----------------------------------------------------------------------
# INITIALIZATION FUNCTION
# ----------------------------------------------------------------------

def initialize_real_sensors():
    """Initializes all hardware and starts the polling thread."""
    hardware_state = HardwareState()
    
    # Initialize I2C Bus once
    try:
        i2c_bus = board.I2C()
        print("I2C Bus initialized.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize I2C bus: {e}")
        i2c_bus = None 

    # --- 1. Initialize Qwiic Joystick ---
    try:
        myJoystick = qwiic_joystick.QwiicJoystick()
        if myJoystick.connected:
            myJoystick.begin()
            print("Qwiic Joystick initialized.")
        else:
            raise ValueError("Joystick not connected.")
    except Exception as e:
        myJoystick = DummyJoystick()
        print(f"WARNING: Qwiic Joystick failed to initialize: {e}. Using dummy.")
        
    # --- 2. Initialize PCF8574 for LEDs ---
    pcf = DummyPCF()
    try:
        # Try preferred jumpered address 0x21 first
        pcf = adafruit_pcf8574.PCF8574(i2c_bus, address=PCF_I2C_ADDR_A)
        pcf_addr = PCF_I2C_ADDR_A
        print(f"PCF8574 (LED Extender) initialized at 0x{pcf_addr:x}.")
    except Exception:
        try:
            # Fallback to default address 0x20
            pcf = adafruit_pcf8574.PCF8574(i2c_bus, address=PCF_I2C_ADDR_B)
            pcf_addr = PCF_I2C_ADDR_B
            print(f"PCF8574 (LED Extender) initialized at 0x{pcf_addr:x} (default).")
        except Exception as e:
            pcf = DummyPCF()
            print(f"WARNING: PCF8574 (LED Extender) failed to initialize: {e}. Using dummy.")

    # Configure LED pins if initialization succeeded
    if not isinstance(pcf, DummyPCF):
        pcf.leds = [pcf.get_pin(i) for i in range(8)]
        for ld in pcf.leds:
            # Configure as outputs (HIGH = off, LOW = LED on)
            try:
                ld.switch_to_output(value=True)
            except:
                pass # Ignore if pin initialization fails
        hardware_state.pcf_initialized = True

    # --- 3. Initialize APDS9960 (Gesture Sensor) ---
    apds = DummyAPDS()
    try:
        apds = APDS9960(i2c_bus)
        apds.enable_proximity = True
        apds.enable_gesture = True
        print("APDS9960 (Gesture Sensor) initialized.")
    except Exception as e:
        print(f"WARNING: APDS9960 (Gesture Sensor) failed to initialize: {e}. Using dummy.")

    # --- 4. Initialize Seesaw Encoder ---
    encoder_container = DummySeesaw()
    try:
        # Re-initialize I2C bus to clear potential prior state (common fix for Seesaw)
        i2c_bus = board.I2C() 
        ss = seesaw.Seesaw(i2c_bus, addr=0x36)
        encoder_container.encoder = rotaryio.IncrementalEncoder(ss)
        
        ss_product = (ss.get_version() >> 16) & 0xFFFF
        print(f"Seesaw Encoder found (Product {ss_product}).")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Seesaw Encoder failed to initialize: {e}. Using dummy.")

    # --- Start Polling Thread ---
    sensor_thread = SensorPollingThread(hardware_state, myJoystick, apds, encoder_container, pcf)
    sensor_thread.daemon = True # Allows thread to exit when main program exits
    sensor_thread.start()
    
    return hardware_state, sensor_thread, encoder_container
