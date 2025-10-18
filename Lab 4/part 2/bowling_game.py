import math
import random
import time
import sys # Added for cleanup

from direct.showbase.ShowBase import ShowBase
# Added CardMaker and LPoint3 for custom geometry
from panda3d.core import Vec3, AmbientLight, DirectionalLight, TextNode, LColor, WindowProperties, CardMaker, LPoint3, NodePath
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from direct.actor.Actor import Actor

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape, BulletRigidBodyNode
from panda3d.bullet import BulletSphereShape, BulletBoxShape
from panda3d.bullet import BulletDebugNode # Kept for potential use, but disabled

# Import the REAL sensors file and constants
from sensors import initialize_real_sensors, GESTURE_UP 

class BowlingGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set up the camera and scene basics
        self.setup_scene()
        
        # Game State
        self.AIMING = 0
        self.THROWN = 1
        self.SCORING = 2
        self.WIN = 3
        self.game_state = self.AIMING
        
        # Sensor Initialization (using real hardware imports from sensors.py)
        # FIX: Now returns the shared state object and the thread manager
        self.hardware_state, self.sensor_thread, self.encoder_container = initialize_real_sensors()

        # Game properties
        self.throw_angle = 0  # Aiming angle controlled by encoder (in degrees)
        self.lane_position = 0 # Horizontal position controlled by joystick
        self.pins_fallen = 0
        self.pins = []
        
        # New constant for movement speed
        self.JOYSTICK_SENSITIVITY = 0.05 # Max change in position per update cycle

        # Start the game setup
        self.reset_game()
        
        # Add the main game loop tasks
        self.taskMgr.add(self.update_game, "updateGameTask")
        self.taskMgr.add(self.update_sensors, "updateSensorTask")
        
        # Add a cleanup hook to stop the sensor thread on exit
        self.exitFunc = self.cleanup_game


    def cleanup_game(self):
        """Called when the game window is closed to safely shut down the sensor thread."""
        print("Cleaning up threads and exiting...")
        if self.sensor_thread and self.sensor_thread.is_alive():
            self.hardware_state.running = False
            self.sensor_thread.join(timeout=2.0) # Wait for thread to finish
        sys.exit(0)
    
    # ----------------------------------------------------------------------
    # NEW: Custom Geometry Helper
    # ----------------------------------------------------------------------
    def create_box_visual(self, color=(1, 1, 1, 1)):
        """
        Creates a visible 6-sided cube using CardMaker planes.
        Returns a NodePath that acts as the visual root for the box.
        The resulting object has an origin point at its geometric center.
        """
        box_root = NodePath('box-root')
        cm = CardMaker('face')
        
        # Define the half-size for convenience (since we will scale it later)
        s = 0.5 
        
        # Faces: Define the 6 planes that make up the cube
        
        # Top (+Z) Face
        cm.setFrame(-s, s, -s, s)
        top = box_root.attachNewNode(cm.generate())
        top.setPos(0, -s, 0)
        
        # # Bottom (-Z) Face
        bottom = box_root.attachNewNode(cm.generate())
        bottom.setPos(0, s, 0)
        bottom.setHpr(0, 180, 0)
        
        # Front (+Y) Face
        cm.setFrame(-s, s, -s, s)
        front = box_root.attachNewNode(cm.generate())
        front.setPos(0, 0, s)
        front.setP(-90)
        
        # # Back (-Y) Face
        back = box_root.attachNewNode(cm.generate())
        back.setPos(0, 0, -s)
        back.setP(90)
        
        # Right (+X) Face
        cm.setFrame(-s, s, -s, s)
        right = box_root.attachNewNode(cm.generate())
        right.setPos(s, 0, 0)
        right.setH(90)
        # right.setP(-90)

        # Left (-X) Face
        left = box_root.attachNewNode(cm.generate())
        left.setPos(-s, 0, 0)
        left.setH(-90)
        # left.setP(-90)

        # Set color on the root node
        box_root.setColor(*color)
        
        return box_root
    # ----------------------------------------------------------------------

    def setup_scene(self):
        """Configures the camera, lighting, and physics world."""
        
        # Set window size
        props = WindowProperties()
        props.setSize(1280, 720) 
        self.win.requestProperties(props)
        
        self.set_background_color(0.2, 0.2, 0.2)

        # Set camera position (overhead view of the lane)
        self.disable_mouse()
        self.camera.setPos(0, -20, 5) 
        self.camera.lookAt(0, 2, 0)    
        
        # Lighting
        alight = AmbientLight('alight')
        alight.setColor(LColor(0.8, 0.8, 0.8, 1))
        alight_node = self.render.attachNewNode(alight)
        self.render.setLight(alight_node)

        dlight = DirectionalLight('dlight')
        dlight.setDirection(Vec3(0, 5, -8))
        dlight.setColor(LColor(0.8, 0.8, 0.8, 1))
        dlight_node = self.render.attachNewNode(dlight)
        self.render.setLight(dlight_node)

        # Physics World Setup
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81)) 

        self.background = self.loader.loadModel("models/environment")
        self.background.reparentTo(self.render)
        self.background.setScale(0.25, 0.75, 0.25)
        self.background.setPos(-8, 120, -0.1)

        # test box creation
        test_box = self.create_box_visual(color=(1, 0, 0, 1))
        test_box.setScale(1, 1, 1)
        test_box.setPos(-5, 0, 2)
        test_box.reparentTo(self.render)
        # keep a reference and start a rotation task so you can inspect every face
        self.test_box = test_box
        self.taskMgr.add(self.rotate_test_box, "rotateTestBoxTask")


        # --- IMPORTANT: Debug visuals enabled for hitbox visibility ---
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugRender = self.render.attachNewNode(debugNode)
        self.world.setDebugNode(debugRender.node())
        debugRender.show() 
        # --------------------------------------------------------------------

    def rotate_test_box(self, task):
        """Rotate the test box through all angles for visual inspection."""
        # task.time gives elapsed seconds since the task started; use it to compute HPR
        t = task.time
        heading = (t * 45) % 360   # 45 deg/sec
        pitch   = (t * 30) % 360   # 30 deg/sec
        roll    = (t * 15) % 360   # 15 deg/sec
        # apply the combined rotation
        if hasattr(self, 'test_box') and not self.test_box.isEmpty():
            self.test_box.setHpr(heading, pitch, roll)
        return Task.cont

    def setup_lane(self):
        """Creates the 3D lane and walls."""
        
        # LANE DIMENSIONS
        lane_width = 4.0
        lane_length = 40.0 # From Y=-10 to Y=30
        wall_thickness = 0.5
        wall_height = 1.0
        wall_length = 35.0 # From Y=-10 to Y=25 (Covers play area)
        
        # WALL PLACEMENT CALCULATIONS
        wall_center_y = (-10.0 + 25.0) / 2.0  # Center of the 35-unit long wall area (Y=7.5)
        wall_x_pos = (lane_width / 2.0) + (wall_thickness / 2.0) # 2.0 + 0.25 = 2.25

        
        # 1. Lane (Ground Plane Physics)
        ground_plane_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        ground_node = BulletRigidBodyNode('Ground')
        ground_node.addShape(ground_plane_shape)
        
        ground_np = self.render.attachNewNode(ground_node)
        self.world.attachRigidBody(ground_node)

        # 2. Visual Lane (CardMaker for a textured quad)
        cm = CardMaker('lane_card')
        cm.setFrame(-lane_width / 2, lane_width / 2, 0, lane_length) 
        lane_visual = self.render.attachNewNode(cm.generate())
        
        lane_visual.setP(-90)
        lane_visual.setPos(0, -10, 0.0)
        lane_visual.setColor(0.6, 0.4, 0.2, 1)

        # 3. Side Walls
        
        # Physics shape uses half dimensions
        wall_shape_half = Vec3(wall_thickness/2, wall_length/2, wall_height/2) 
        wall_visual_scale = (wall_thickness, wall_length, wall_height)

        # Left Wall
        # NEW VISUAL: Custom CardMaker Box
        left_visual = self.create_box_visual(color=(0.4, 0.4, 0.4, 1))
        left_visual.setScale(*wall_visual_scale) 
        
        shape = BulletBoxShape(wall_shape_half)
        node = BulletRigidBodyNode('LeftWall')
        node.addShape(shape)
        np_left = self.render.attachNewNode(node)
        left_visual.reparentTo(np_left)
        # Position NodePath (Physics Center)
        np_left.setPos(-wall_x_pos, wall_center_y, wall_height / 2) 
        self.world.attachRigidBody(node)

        # Right Wall
        # NEW VISUAL: Custom CardMaker Box
        right_visual = self.create_box_visual(color=(0.4, 0.4, 0.4, 1))
        right_visual.setScale(*wall_visual_scale)
        
        shape = BulletBoxShape(wall_shape_half)
        node = BulletRigidBodyNode('RightWall')
        node.addShape(shape)
        np_right = self.render.attachNewNode(node)
        right_visual.reparentTo(np_right)
        # Position NodePath (Physics Center)
        np_right.setPos(wall_x_pos, wall_center_y, wall_height / 2)
        self.world.attachRigidBody(node)


    def setup_pins(self):
        """Creates the 10 bowling pins at the end of the lane."""
        self.pins_fallen = 0
        pin_row_config = [
            (0, 20),           # Row 1 (1 pin)
            (-0.5, 21), (0.5, 21), # Row 2 (2 pins)
            (-1.0, 22), (0.0, 22), (1.0, 22), # Row 3 (3 pins)
            (-1.5, 23), (-0.5, 23), (0.5, 23), (1.5, 23) # Row 4 (4 pins)
        ]
        
        # Pin is a vertically stretched rectangle (box)
        pin_half_size = Vec3(0.1 / 2, 0.1 / 2, 0.5 / 2)
        pin_visual_scale = (0.1, 0.1, 0.5)
        
        for i, (x, y) in enumerate(pin_row_config):
            # 1. Physics setup (Bullet Box)
            pin_shape = BulletBoxShape(pin_half_size)
            pin_node = BulletRigidBodyNode(f'Pin-{i}')
            pin_node.setMass(0.5) 
            pin_node.addShape(pin_shape)
            
            # 2. NEW Visual setup (Custom CardMaker Box)
            pin_visual = self.create_box_visual(color=(1, 1, 1, 1)) # White
            pin_visual.setScale(*pin_visual_scale)
            
            # 3. Attach and position
            pin_np = self.render.attachNewNode(pin_node)
            pin_visual.reparentTo(pin_np)
            pin_np.setPos(x, y, pin_half_size.z) # Z pos is half height
            self.world.attachRigidBody(pin_node)
            self.pins.append(pin_np)
            
        self.update_score_display()


    def setup_ball(self):
        """Creates the bowling ball."""
        ball_radius = 0.3
        self.ball_thrown = False
        
        # Check if ball already exists
        if hasattr(self, 'ball_np'):
            self.ball_np.removeNode()

        # 1. Physics Node (Bullet Sphere)
        ball_shape = BulletSphereShape(ball_radius)
        ball_node = BulletRigidBodyNode('Ball')
        ball_node.setMass(5.0) 
        ball_node.addShape(ball_shape)
        
        # 2. Visual Node (Primitive Sphere) - Keeping this, as it looks better than a box
        ball_visual = self.loader.loadModel('misc/sphere')
        ball_visual.setScale(ball_radius)
        
        # 3. Attach and position
        self.ball_np = self.render.attachNewNode(ball_node)
        ball_visual.reparentTo(self.ball_np)
        
        self.ball_np.setColor(0.1, 0.1, 0.1, 1) # Dark color for bowling ball
        self.world.attachRigidBody(ball_node)
        
        # Set starting position (controlled by joystick)
        self.ball_np.setPos(self.lane_position, -8, ball_radius) 


    def update_sensors(self, task):
        """
        Reads and maps REAL sensor data from the non-blocking hardware state object.
        """
        
        # 1. Joystick for Left/Right Positioning (X-axis)
        # Read from shared state (Non-blocking)
        joystick_val = self.hardware_state.joystick_x
        
        # NEW LOGIC: Joystick controls the CHANGE in position (velocity/delta)
        center_val = 512.0
        dead_zone = 50 
        
        difference = joystick_val - center_val
        
        # Calculate movement delta
        if abs(difference) < dead_zone:
            normalized_delta = 0.0
        else:
            # Normalize the difference to a value between -1.0 and 1.0 (for max movement)
            normalized_delta = difference / (512.0 - dead_zone) 
        
        # Apply the delta to the current position
        self.lane_position += normalized_delta * self.JOYSTICK_SENSITIVITY
        
        # Clamp the position to ensure the ball stays within the lane bounds (-1.5 to 1.5)
        self.lane_position = max(-1.5, min(1.5, self.lane_position))

        
        # 2. Rotary Encoder for Aiming Angle (Z-rotation)
        # Read from shared state (Non-blocking)
        encoder_pos = self.hardware_state.encoder_pos
        
        # --- FIX: Invert the angle mapping to correct mirroring ---
        self.throw_angle = encoder_pos * -2.0 # Invert direction
        
        # Map encoder position to an angle (-20 to +20 degrees)
        self.throw_angle = max(-20, min(20, self.throw_angle)) # Clamp angle
        
        # 3. Gesture Sensor for Throw Action (UP = 0x01)
        # Read from shared state (Non-blocking)
        gesture = self.hardware_state.gesture
        
        if gesture == GESTURE_UP and self.game_state == self.AIMING:
            self.throw_ball()
            # Reset gesture state immediately after use
            self.hardware_state.gesture = 0 

        return Task.cont


    def update_game(self, task):
        """The main game loop, runs physics and updates game logic."""
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 0.008)

        if self.game_state == self.AIMING:
            # Update ball position and rotation based on sensors
            ball_radius = 0.3
            self.ball_np.setPos(self.lane_position, -8, ball_radius) 
            self.ball_np.setHpr(self.throw_angle, 0, 0) 
            
            self.update_aim_display()
            
        elif self.game_state == self.THROWN:
            # Check if ball has moved far down the lane (arbitrary point)
            if self.ball_np.getY() > 25:
                self.game_state = self.SCORING
                self.throw_end_time = time.time()
        
        elif self.game_state == self.SCORING:
            # Wait a few seconds for all pins to settle
            if time.time() - self.throw_end_time > 3.0:
                self.check_pins()
                
        return Task.cont


    def throw_ball(self):
        """Applies velocity to the ball based on current aiming angle."""
        if self.ball_thrown: return
        
        ball_body = self.ball_np.node()
        
        # --- FIX: Explicitly check for valid body and activate it for immediate throw ---
        if not isinstance(ball_body, BulletRigidBodyNode):
             print("Error: Node attached to ball_np is not a valid BulletRigidBodyNode.")
             return
             
        # Explicitly activate the body (wake it up)
        ball_body.setActive(True)

        self.game_state = self.THROWN
        self.ball_thrown = True

        # Calculate force vector (constant speed, angle from encoder)
        speed = 20.0 # Constant forward speed
        angle_rad = -math.radians(self.throw_angle)
        
        # X-velocity is based on the sine of the angle
        vx = speed * math.sin(angle_rad)
        # Y-velocity (forward) is based on the cosine of the angle
        vy = speed * math.cos(angle_rad)
        
        # Apply impulse to the physics body of the SAME sphere object
        ball_body.setLinearVelocity(Vec3(vx, vy, 0))
        
        # Hide aim indicators
        self.aim_text.destroy()


    def check_pins(self):
        """Checks how many pins have fallen and determines game over."""
        pins_knocked = 0
        for pin_np in self.pins:
            # A pin has fallen if it is rotated significantly (tilted)
            # or if its Z position is very low.
            if pin_np.getR() > 30 or pin_np.getZ() < 0.2:
                pins_knocked += 1
                
        self.pins_fallen = pins_knocked
        self.update_score_display()

        if self.pins_fallen >= 1:
            self.show_win_screen()
        else:
            # --- MODIFICATION: If not a strike, allow another throw at remaining pins ---
            # Wait 0.1 seconds to view the pin positions, then reset ONLY the ball.
            self.taskMgr.doMethodLater(0.1, self.reset_ball_only, "ResetBallForNextThrow")
            self.game_state = self.SCORING 
            
            
    # --- NEW METHOD: Resets only the ball and returns to AIMING state ---
    def reset_ball_only(self, task=None):
        """Resets the bowling ball and returns the game to the aiming state."""
        
        # 1. Clean up old ball (both physics and visual node)
        if hasattr(self, 'ball_np'):
             self.world.removeRigidBody(self.ball_np.node())
             self.ball_np.removeNode()

        # 2. Reset position and recreate ball
        self.lane_position = 0 # Reset lane position to center for new throw
        self.setup_ball()
        
        # 3. Reset state
        self.game_state = self.AIMING
        self.throw_angle = 0
        
        # Reset encoder position in the container and the hardware state
        if hasattr(self.encoder_container.encoder, 'position'):
             self.encoder_container.encoder.position = 0
        self.encoder_container.last_position = 0 
        self.hardware_state.encoder_pos = 0 # Important: reset the shared state too!
        
        # Ensure aim display updates immediately
        if hasattr(self, 'aim_text'): 
            self.aim_text.destroy()

        self.hardware_state.win_flag = False
            
        return Task.done


    def reset_game(self, task=None):
        """Resets the entire scene (full game reset: pins, ball, and score)."""
        
        # --- FIX: Correctly remove physics bodies for old pins ---
        for pin in self.pins:
            self.world.removeRigidBody(pin.node())
            pin.removeNode()
        
        # Clean up ball and text
        if hasattr(self, 'ball_np'):
             self.world.removeRigidBody(self.ball_np.node())
             self.ball_np.removeNode()

        if hasattr(self, 'win_text'):
            self.win_text.destroy()
            
        self.pins = []
        
        self.setup_lane()
        self.setup_pins()
        self.lane_position = 0 # Reset lane position to center for new game
        self.setup_ball()
        self.game_state = self.AIMING
        self.throw_angle = 0
        
        # Reset encoder position in the container and the hardware state
        if hasattr(self.encoder_container.encoder, 'position'):
             self.encoder_container.encoder.position = 0
        self.encoder_container.last_position = 0 
        self.hardware_state.encoder_pos = 0 # Important: reset the shared state too!
        
        self.pins_fallen = 0

        self.hardware_state.win_flag = False
        # Ensure any pending reset task is cleared if we are resetting manually
        self.taskMgr.remove("GameResetAfterThrow")


    def update_score_display(self):
        """Updates the pin count on screen."""
        if hasattr(self, 'score_text'):
            self.score_text.destroy()
            
        self.score_text = OnscreenText(
            text=f"Pins Standing: {10 - self.pins_fallen}",
            pos=(0.0, 0.8),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=True
        )

    
    def update_aim_display(self):
        """Shows aiming instructions and angle."""
        if hasattr(self, 'aim_text'):
            self.aim_text.destroy()

        # We must read the joystick value again here to show it live
        # Use the shared state for display
        aim_pos_display = self.lane_position 
        
        self.aim_text = OnscreenText(
            text=f"Aim Angle: {self.throw_angle:.1f} deg (Encoder)\nPos: {aim_pos_display:.2f} (Joystick)\nSwipe UP to Throw!",
            pos=(0.0, -0.8),
            scale=0.06,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter,
            mayChange=True
        )

    
    def show_win_screen(self):
        """Displays the win message."""
        self.game_state = self.WIN
        
        # --- NEW: Set win flag in background thread state ---
        self.hardware_state.win_flag = True
        # ----------------------------------------------------
        
        self.win_text = OnscreenText(
            text="YOU WIN! All Pins Knocked Down!",
            pos=(0.0, 0.0),
            scale=0.15,
            fg=(0, 1, 0, 1),
            bg=(0.2, 0.2, 0.2, 0.8),
            align=TextNode.ACenter,
            mayChange=True
        )
        # Set a task to reset the game after 5 seconds
        self.taskMgr.doMethodLater(5.0, self.reset_game, "ResetGameTask")

game = BowlingGame()
game.run()
