
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
        self.last_check_time = 0

    def start(self):
        self.car.enable_ultrasonic(True)
        self.car.set_speed(self.DEFAULT_SPEED)
        self.running = True
        self.state = 'FORWARD'
        self.car.move_forward()
        self.last_check_time = time.time()
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
            return

        elif self.state == 'TURNING':
            # Check if we are done turning (0.4s duration)
            if current_time - self.state_start_time > 0.4:
                self.car.stop()
                self.state = 'FORWARD'
            return
            
        elif self.state == 'FORWARD':
            # We are moving forward Use throttling to avoid I2C flooding
            # Only check sensors every 100ms (0.1s)
            
            if current_time - self.last_check_time < 0.1:
                return # Skip checking this loop iteration
            
            self.last_check_time = current_time
            
            # Now we check
            dis = self.car.get_distance()
            
            # Safety checks for bad readings
            if dis == 0 or dis > 4500:
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
                # Repeating this command might flood I2C too if not careful
                # But since we are throttled to 10hz, it should be fine.
                self.car.move_forward()
