
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
        self.state = 'IDLE' 
        self.state_start_time = 0
        self.last_check_time = 0

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
            
            # print("DEBUG: Reading Sensor...")
            dis = self.car.get_distance()
            # print(f"DEBUG: Distance = {dis}mm")
            
            if dis == 0 or dis > 4500:
                # print("DEBUG: Invalid sensor read")
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
                self.car.move_forward()
