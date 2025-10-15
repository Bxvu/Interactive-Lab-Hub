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

# Import the REAL sensors file
from sensors import initialize_real_sensors 

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
        # The return values match the objects used in your provided code
        self.joystick, self.gesture, self.encoder_container = initialize_real_sensors()

        # Game properties
        self.throw_angle = 0  # Aiming angle controlled by encoder (in degrees)
        self.lane_position = 0 # Horizontal position controlled by joystick
        self.pins_fallen = 0
        self.pins = []
        
        # NEW: List to hold the preview dots
        self.aim_previews = [] 

        # New constant for movement speed
        self.JOYSTICK_SENSITIVITY = 0.05 # Max change in position per update cycle

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
        self.camera.setPos(0, -15, 10) # Moved back to Y=-15 and up to Z=10
        self.camera.lookAt(0, 5, 0)    # Look further down the lane
        
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

        # --- FIX: Enable Bullet Debug Node to show physics shapes ---
        # We rely on the debug renderer to visualize the pin/ball/lane shapes as wireframes.
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugRender = self.render.attachNewNode(debugNode)
        self.world.setDebugNode(debugRender.node())
        # The user's necessary fix to show the debug render:
        debugRender.show() 
        # -----------------------------------------------------------


    def setup_lane(self):
        """Creates the 3D lane and walls."""
        
        # 1. Lane (Ground Plane Physics)
        # Note: We use the plane shape for infinite, non-moving ground physics
        ground_plane_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        ground_node = BulletRigidBodyNode('Ground')
        ground_node.addShape(ground_plane_shape)
        # Attach the ground plane to the render. This will appear as a grid line in debug mode.
        self.render.attachNewNode(ground_node).setPos(0, 0, 0)
        self.world.attachRigidBody(ground_node)
        
        # 3. Simple Side Walls (long, thin boxes)
        wall_height, wall_thickness = 1, 0.5
        wall_length = 30
        
        # Left Wall Physics
        shape = BulletBoxShape(Vec3(wall_thickness, wall_length, wall_height))
        node = BulletRigidBodyNode('LeftWall')
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(-2.5, wall_length / 2, wall_height) # Positioned to leave a lane width
        self.world.attachRigidBody(node)
        np.setColor(0.4, 0.4, 0.4, 1)

        # Right Wall Physics
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
        
        # Pin is now a vertically stretched rectangle (box) as requested
        pin_size = Vec3(0.1, 0.1, 0.5) 
        
        for i, (x, y) in enumerate(pin_row_config):
            pin_shape = BulletBoxShape(pin_size)
            pin_node = BulletRigidBodyNode(f'Pin-{i}')
            pin_node.setMass(0.5) # Pins are light
            pin_node.addShape(pin_shape)
            pin_np = self.render.attachNewNode(pin_node)
            pin_np.setPos(x, y, pin_size.z) # Place on ground (Z position must be pin height/2)
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

        # Physics Node (Sphere as requested)
        ball_shape = BulletSphereShape(ball_radius)
        ball_node = BulletRigidBodyNode('Ball')
        ball_node.setMass(5.0) # Ball is heavy
        ball_node.addShape(ball_shape)
        
        # Visual Node (NodePath attached directly to the render)
        self.ball_np = self.render.attachNewNode(ball_node)
        
        # Set scale and color. The Debug Node will draw the sphere shape.
        self.ball_np.setScale(ball_radius)
        self.ball_np.setColor(0.1, 0.1, 0.1, 1) # Dark color for bowling ball
        
        self.world.attachRigidBody(ball_node)
        
        # Set starting position (controlled by joystick)
        self.ball_np.setPos(self.lane_position, -8, ball_radius) # Start far back


    def draw_aim_preview(self):
        """Draws temporary spheres ahead of the ball indicating the throw angle."""
        
        # Cleanup any existing previews
        for preview in self.aim_previews:
            preview.removeNode()
        self.aim_previews = []
        
        if self.game_state != self.AIMING:
            return

        # Starting position of the ball
        start_pos = self.ball_np.getPos()
        
        # Convert angle to radians
        angle_rad = math.radians(self.throw_angle)
        
        # Vector components for movement (normalized path direction)
        dx = math.sin(angle_rad)
        dy = math.cos(angle_rad)

        # Preview dot properties
        preview_radius = 0.1
        preview_color = (1, 1, 0, 0.5) # Yellowish with low alpha (transparency not easy with debug mode)
        preview_distance = 3.0 # Distance between preview dots
        
        for i in range(1, 6): # Draw 5 preview dots
            # Calculate next position along the projected path
            x_offset = dx * preview_distance * i
            y_offset = dy * preview_distance * i
            
            preview_pos = start_pos + Vec3(x_offset, y_offset, 0)
            
            # Create a simple box/sphere visual (using a small Box for simplicity)
            preview_shape = BulletBoxShape(Vec3(preview_radius, preview_radius, preview_radius))
            preview_node = BulletRigidBodyNode('Preview')
            preview_node.addShape(preview_shape)
            
            preview_np = self.render.attachNewNode(preview_node)
            preview_np.setPos(preview_pos)
            preview_np.setColor(*preview_color)
            
            # Make the preview non-collidable and fixed in space (not part of the physics)
            preview_node.setKinematic(True)
            
            self.aim_previews.append(preview_np)


    def update_sensors(self, task):
        """
        Reads and maps REAL sensor data to game variables.
        
        The objects self.joystick, self.gesture, and self.encoder_container 
        are now the live hardware objects from sensors.py.
        """
        
        # 1. Joystick for Left/Right Positioning (X-axis)
        joystick_val = self.joystick.horizontal
        
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
        # Uses the EncoderContainer update method to get the current position
        encoder_pos = self.encoder_container.update()
        # Map encoder position to an angle (-20 to +20 degrees)
        self.throw_angle = encoder_pos * 2.0 # 1 unit of turn = 2 degrees of angle
        self.throw_angle = max(-20, min(20, self.throw_angle)) # Clamp angle
        
        # 3. Gesture Sensor for Throw Action (UP = 0x01)
        # Uses the APDS9960 object directly
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
            self.draw_aim_preview() # NEW: Draw the aim preview path
            
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
        
        # Hide aim indicators and preview dots
        self.aim_text.destroy()
        self.clear_previews() # NEW: Clear preview dots


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
            # --- MODIFICATION: If not a strike, allow another throw at remaining pins ---
            # Wait 5 seconds to view the pin positions, then reset ONLY the ball.
            self.taskMgr.doMethodLater(5.0, self.reset_ball_only, "ResetBallForNextThrow")
            self.game_state = self.SCORING 
            
    # --- NEW METHOD: Clears all preview spheres ---
    def clear_previews(self):
        for preview in self.aim_previews:
            preview.removeNode()
        self.aim_previews = []

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
        
        # Reset encoder to zero (important for aiming on next throw)
        if hasattr(self.encoder_container.encoder, 'position'):
             self.encoder_container.encoder.position = 0
        self.encoder_container.last_position = 0 
        
        # Ensure aim display updates immediately
        if hasattr(self, 'aim_text'): 
            self.aim_text.destroy()
            
        # Ensure previews are clear
        self.clear_previews() 
            
        return Task.done


    def reset_game(self):
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
        
        # Reset encoder to zero
        if hasattr(self.encoder_container.encoder, 'position'):
             self.encoder_container.encoder.position = 0
        self.encoder_container.last_position = 0 
        
        self.pins_fallen = 0
        # Ensure any pending reset task is cleared if we are resetting manually
        self.taskMgr.remove("GameResetAfterThrow")
        self.clear_previews()


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
        joystick_val = self.joystick.horizontal
        aim_pos_display = self.lane_position # Use the actual lane_position variable for display
        
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
