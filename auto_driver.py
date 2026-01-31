
import time

class ObstacleAvoidance:
    def __init__(self, car_driver):
        self.car = car_driver
        self.running = False
        
        # Tuning for better safety
        self.NEAR_DISTANCE = 300 # Back up if closer than 30cm
        self.FAR_DISTANCE = 500  # Turn if closer than 50cm
        self.DEFAULT_SPEED = 40  # Slower speed for safety
        
        # State Machine
        self.state = 'IDLE' # IDLE, FORWARD, BACKING_UP, TURNING
        self.state_start_time = 0

    def start(self):
        self.car.enable_ultrasonic(True)
        self.car.set_speed(self.DEFAULT_SPEED)
        self.running = True
        self.state = 'FORWARD'
        self.car.move_forward()
        print(f"Obstacle Avoidance Started")

    def stop(self):
        self.running = False
        self.car.enable_ultrasonic(False)
        self.car.stop()
        self.state = 'IDLE'
        print("Obstacle Avoidance Mode Stopped")

    def step(self):
        """
        Non-blocking step function.
        """
        if not self.running:
            return

        current_time = time.time()
        
        # --- State Machine Logic ---
        
        if self.state == 'BACKING_UP':
            # Check if we are done backing up (0.5s duration)
            if current_time - self.state_start_time > 0.5:
                self.car.stop()
                self.state = 'FORWARD' # Try moving forward/checking again
                # Small pause to stabilize?
                # We can add a 'WAIT' state if needed, but let's try direct transition
            return # Don't check sensors while backing up

        elif self.state == 'TURNING':
            # Check if we are done turning (0.4s duration)
            if current_time - self.state_start_time > 0.4:
                self.car.stop()
                self.state = 'FORWARD'
            return # Don't check sensors while turning
            
        elif self.state == 'FORWARD':
            # We are moving forward (or just finished an action), check sensors
            
            dis = self.car.get_distance()
            
            # Safety checks for bad readings
            if dis == 0 or dis > 4500:
                # self.car.stop()
                # Stop momentarily or just ignore?
                # If we stop here, we need a way to resume.
                # Let's just return and keep current momentum, unless it persists?
                # Safer: Stop.
                self.car.stop()
                return

            if dis < self.NEAR_DISTANCE:
                print(f"OBSTACLE ({dis}mm)! Backing up...")
                self.car.stop()
                self.car.move_backward()
                self.state = 'BACKING_UP'
                self.state_start_time = current_time
                
            elif dis <= self.FAR_DISTANCE:
                print(f"Object detected ({dis}mm). Turning...")
                self.car.stop()
                self.car.rotate_left()
                self.state = 'TURNING'
                self.state_start_time = current_time
                
            else:
                # Path Clear, ensure moving forward
                # Only send command if not already moving to avoid I2C flooding?
                # CarDriver doesn't cache state, so we just send it.
                # Maybe only every X intervals?
                # For now, just send it, but maybe throttle?
                self.car.move_forward()
                
