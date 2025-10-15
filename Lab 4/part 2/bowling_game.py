# add hat to encoder for visual info

import math
import random
import time

from direct.showbase.ShowBase import ShowBase
# Added WindowProperties to the import list
from panda3d.core import Vec3, AmbientLight, DirectionalLight, TextNode, LColor, WindowProperties 
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from direct.actor.Actor import Actor

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape, BulletRigidBodyNode
from panda3d.bullet import BulletSphereShape, BulletBoxShape
from panda3d.bullet import BulletDebugNode

# Import the mock sensors file
# NOTE: WHEN RUNNING ON RASPBERRY PI WITH REAL HARDWARE,
#       REPLACE THIS WITH YOUR ACTUAL HARDWARE IMPORTS.
from sensors import initialize_mock_sensors 

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
        
        # Sensor Initialization (using mocks for testing)
        self.joystick, self.gesture, self.encoder_container = initialize_mock_sensors()

        # Game properties
        self.throw_angle = 0  # Aiming angle controlled by encoder (in degrees)
        self.lane_position = 0 # Horizontal position controlled by joystick
        self.pins_fallen = 0
        self.pins = []

        # Start the game setup
        self.reset_game()
        
        # Add the main game loop tasks
        self.taskMgr.add(self.update_game, "updateGameTask")
        self.taskMgr.add(self.update_sensors, "updateSensorTask")


    def setup_scene(self):
        """Configures the camera, lighting, and physics world."""
        
        # --- FIX: Robust way to set window size using WindowProperties ---
        props = WindowProperties()
        props.setSize(1280, 720) # Request 720p resolution
        self.win.requestProperties(props)
        # -------------------------------------------------------------------
        
        self.set_background_color(0.2, 0.2, 0.2)

        # Set camera position (overhead view of the lane)
        self.disable_mouse()
        self.camera.setPos(0, -10, 8) 
        self.camera.lookAt(0, 0, 5)
        
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
        self.world.setGravity(Vec3(0, 0, -9.81)) # Standard gravity

        # Debug overlay (optional, uncomment to see physics shapes)
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        debugRender = self.render.attachNewNode(debugNode)
        self.world.setDebugNode(debugRender.node())


    def setup_lane(self):
        """Creates the 3D lane and walls."""
        # 1. Lane (Ground Plane)
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('Ground')
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(0, 0, 0)
        self.world.attachRigidBody(node)

        # 2. Visual Plane (a simple flat surface)
        # Note: Panda3D built-in models like 'models/plane' require the
        # runtime environment to find them, which is usually fine if Panda3D 
        # is installed correctly.
        self.lane = self.loader.loadModel("models/environment")
        self.lane.reparentTo(self.render)
        self.lane.setScale(0.25, 0.25, 0.25)
        self.lane.setPos(-8, 42, 0)
        # self.lane.setScale(20, 40, 1)
        # self.lane.setPos(0, 0, 0)
        self.lane.setColor(0.5, 0.3, 0.1, 1) # Brown wood color

        # 3. Simple Side Walls (long, thin boxes)
        wall_height, wall_thickness = 1, 0.5
        wall_length = 30
        
        # Left Wall
        shape = BulletBoxShape(Vec3(wall_thickness, wall_length, wall_height))
        node = BulletRigidBodyNode('LeftWall')
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(-2.5, wall_length / 2, wall_height) # Positioned to leave a lane width
        self.world.attachRigidBody(node)
        np.setColor(0.4, 0.4, 0.4, 1)

        # Right Wall
        shape = BulletBoxShape(Vec3(wall_thickness, wall_length, wall_height))
        node = BulletRigidBodyNode('RightWall')
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(2.5, wall_length / 2, wall_height)
        self.world.attachRigidBody(node)
        np.setColor(0.4, 0.4, 0.4, 1)


    def setup_pins(self):
        """Creates the 10 bowling pins at the end of the lane."""
        self.pins_fallen = 0
        pin_row_config = [
            (0, 20),           # Row 1 (1 pin)
            (-0.5, 21), (0.5, 21), # Row 2 (2 pins)
            (-1.0, 22), (0.0, 22), (1.0, 22), # Row 3 (3 pins)
            (-1.5, 23), (-0.5, 23), (0.5, 23), (1.5, 23) # Row 4 (4 pins)
        ]
        
        pin_size = Vec3(0.1, 0.1, 0.5) # Thin box for simplicity
        
        for i, (x, y) in enumerate(pin_row_config):
            pin_shape = BulletBoxShape(pin_size)
            pin_node = BulletRigidBodyNode(f'Pin-{i}')
            pin_node.setMass(0.5) # Pins are light
            pin_node.addShape(pin_shape)
            pin_np = self.render.attachNewNode(pin_node)
            pin_np.setPos(x, y, pin_size.z / 2) # Place on ground
            pin_np.setColor(1, 1, 1, 1) # White pins
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

        # Physics Node
        ball_shape = BulletSphereShape(ball_radius)
        ball_node = BulletRigidBodyNode('Ball')
        ball_node.setMass(5.0) # Ball is heavy
        ball_node.addShape(ball_shape)
        
        # Visual Node
        self.ball_np = self.render.attachNewNode(ball_node)
        # Note: 'models/sphere' is a default Panda3D model
        self.ball_model = self.loader.loadModel("models/misc/sphere") 
        self.ball_model.reparentTo(self.ball_np)
        self.ball_model.setScale(ball_radius)
        self.ball_np.setColor(0, 0, 0, 1) # Black ball
        
        self.world.attachRigidBody(ball_node)
        
        # Set starting position (controlled by joystick)
        self.ball_np.setPos(self.lane_position, -8, ball_radius) # Start far back


    def update_sensors(self, task):
        """Reads and maps sensor data to game variables."""
        # 1. Joystick for Left/Right Positioning (X-axis)
        joystick_val = self.joystick.horizontal
        # Map joystick range (0-1023) to lane position range (-1.5 to 1.5)
        self.lane_position = ((joystick_val / 1023.0) * 3.0) - 1.5
        
        # 2. Rotary Encoder for Aiming Angle (Z-rotation)
        encoder_pos = self.encoder_container.encoder.update()
        # Map encoder position to an angle (-20 to +20 degrees)
        self.throw_angle = encoder_pos * 2.0 # 1 unit of turn = 2 degrees of angle
        self.throw_angle = max(-20, min(20, self.throw_angle)) # Clamp angle
        
        # 3. Gesture Sensor for Throw Action (UP = 0x01)
        gesture = self.gesture.gesture()
        if gesture == 0x01 and self.game_state == self.AIMING:
            self.throw_ball()

        return Task.cont


    def update_game(self, task):
        """The main game loop, runs physics and updates game logic."""
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 0.008)

        if self.game_state == self.AIMING:
            # Update ball position and rotation based on sensors
            ball_radius = 0.3
            self.ball_np.setPos(self.lane_position, -8, ball_radius)
            self.ball_np.setHpr(self.throw_angle, 0, 0) # Rotate for aiming visual
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
        
        self.game_state = self.THROWN
        self.ball_thrown = True

        # Calculate force vector (constant speed, angle from encoder)
        speed = 20.0 # Constant forward speed
        angle_rad = math.radians(self.throw_angle)
        
        # X-velocity is based on the sine of the angle
        vx = speed * math.sin(angle_rad)
        # Y-velocity (forward) is based on the cosine of the angle
        vy = speed * math.cos(angle_rad)
        
        # Apply impulse to the physics body
        ball_body = self.ball_np.node()
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

        if self.pins_fallen >= 10:
            self.show_win_screen()
        else:
            # For simplicity, if not all pins fell, we reset immediately for the next throw
            self.reset_game()


    def reset_game(self):
        """Resets the scene for a new throw or a new game."""
        # Clean up old pins and ball
        for pin in self.pins:
            pin.removeNode()
        self.pins = []
        
        if hasattr(self, 'ball_np'):
             self.ball_np.removeNode()

        if hasattr(self, 'win_text'):
            self.win_text.destroy()
            
        self.setup_lane()
        self.setup_pins()
        self.setup_ball()
        self.game_state = self.AIMING
        self.throw_angle = 0
        self.joystick._x = 512 # Reset mock joystick state
        self.encoder_container.encoder.position = 0
        self.pins_fallen = 0


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

        aim_pos = ((self.joystick.horizontal / 1023.0) * 0.8) - 0.4
        
        self.aim_text = OnscreenText(
            text=f"Aim Angle: {self.throw_angle:.1f} deg\nPos: {aim_pos:.2f} (Joystick/Encoder)\nSwipe UP to Throw!",
            pos=(0.0, -0.8),
            scale=0.06,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter,
            mayChange=True
        )

    
    def show_win_screen(self):
        """Displays the win message."""
        self.game_state = self.WIN
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
