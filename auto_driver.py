
import time

class ObstacleAvoidance:
    def __init__(self, car_driver):
        self.car = car_driver
        self.running = False
        
        # Tuning per user request (closer approach)
        self.NEAR_DISTANCE = 150 # Back up if closer than 15cm
        self.FAR_DISTANCE = 300  # Turn if closer than 30cm
        self.DEFAULT_SPEED = 60  # Slightly faster but safe
        
        # State Machine
        self.state = 'IDLE' 
        self.state_start_time = 0
        self.last_check_time = 0
        self.distance_history = [] # For filtering jitter

    def start(self):
        print("DEBUG: AutoDriver START requested")
        self.car.enable_ultrasonic(True)
        self.car.set_speed(self.DEFAULT_SPEED)
        self.running = True
        self.state = 'FORWARD'
        self.car.move_forward()
        self.last_check_time = time.time()
        print(f"Obstacle Avoidance Started")

    def stop(self):
        print("DEBUG: AutoDriver STOP requested")
        self.running = False
        self.car.enable_ultrasonic(False)
        self.car.stop()
        self.state = 'IDLE'
        print("Obstacle Avoidance Mode Stopped")

    def step(self):
        if not self.running:
            return

        current_time = time.time()
        
        if self.state == 'BACKING_UP':
            if current_time - self.state_start_time > 0.5:
                print("DEBUG: Finished Backing Up -> Moving Forward")
                self.car.stop()
                self.state = 'FORWARD' 
            return

        elif self.state == 'TURNING':
            if current_time - self.state_start_time > 0.4:
                print("DEBUG: Finished Turning -> Moving Forward")
                self.car.stop()
                self.state = 'FORWARD'
            return
            
        elif self.state == 'FORWARD':
            # Throttling
            if current_time - self.last_check_time < 0.1:
                return 
            
            self.last_check_time = current_time
            
            dis = self.car.get_distance()
            
            if dis == 0:
                # Ignore transient 0 readings to avoid jerky stopping
                return

            # Keep short history for filtering
            self.distance_history.append(dis)
            if len(self.distance_history) > 3:
                self.distance_history.pop(0)
            
            # Use average of last 3 samples
            avg_dis = sum(self.distance_history) / len(self.distance_history)
            
            if avg_dis < self.NEAR_DISTANCE:
                print(f"OBSTACLE ({avg_dis:.1f}mm)! Backing up...")
                self.car.stop()
                self.car.move_backward()
                self.state = 'BACKING_UP'
                self.state_start_time = current_time
                self.distance_history = [] # Reset history on state change
                
            elif avg_dis <= self.FAR_DISTANCE:
                print(f"Object detected ({avg_dis:.1f}mm). Turning...")
                self.car.stop()
                self.car.rotate_left()
                self.state = 'TURNING'
                self.state_start_time = current_time
                self.distance_history = [] # Reset history on state change
                
            else:
                self.car.move_forward()
