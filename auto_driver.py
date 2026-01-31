
import time

class ObstacleAvoidance:
    def __init__(self, car_driver):
        self.car = car_driver
        self.running = False
        
        # Tuning for better safety
        self.NEAR_DISTANCE = 300 # Increased from 200 to 300 mm (30cm) for earlier braking
        self.FAR_DISTANCE = 500  # Increased to 500 mm (50cm)
        self.DEFAULT_SPEED = 40  # Slower speed for better reaction time

    def start(self):
        self.car.enable_ultrasonic(True)
        self.car.set_speed(self.DEFAULT_SPEED)
        self.running = True
        print(f"Obstacle Avoidance Started (Safe Distance: {self.NEAR_DISTANCE}mm)")

    def stop(self):
        self.running = False
        self.car.enable_ultrasonic(False)
        self.car.stop()
        print("Obstacle Avoidance Mode Stopped")

    def step(self):
        """
        Execute one step of the avoidance logic.
        """
        if not self.running:
            return

        dis = self.car.get_distance()
        
        # Valid range check
        if dis == 0:
            # 0 sometimes means "Out of Range" (> 4m), but can be a glitch.
            # To be safe, if we see 0, we can just keep doing what we were doing or stop.
            # Let's print it to debug.
            # print("Sensor read 0")
            return

        if dis < self.NEAR_DISTANCE:
            # Emergency Stop & Back up
            print(f"OBSTACLE ({dis}mm)! Backing up...")
            self.car.stop() # Ensure forward momentum breaks
            time.sleep(0.05)
            self.car.move_backward()
            time.sleep(0.3) # Back up for longer
            
        elif dis <= self.FAR_DISTANCE:
            # Too close to proceed, turn away
            print(f"Object detected ({dis}mm). Turning...")
            self.car.stop()
            time.sleep(0.1)
            self.car.rotate_left()
            time.sleep(0.25)
            
        else:
            # Clear path
            # print(f"Path Clear ({dis}mm)")
            self.car.move_forward()
            
        # Pacing
        time.sleep(0.05)
