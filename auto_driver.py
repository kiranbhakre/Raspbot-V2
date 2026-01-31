
import time

class ObstacleAvoidance:
    def __init__(self, car_driver):
        self.car = car_driver
        self.running = False
        
        # Constants from reference code
        self.NEAR_DISTANCE = 200 # mm
        self.FAR_DISTANCE = 425  # mm
        self.DEFAULT_SPEED = 50  # Slower speed for autonomous mode

    def start(self):
        self.car.enable_ultrasonic(True)
        # Store previous speed to restore later? 
        # For now, just set a safe speed
        self.car.set_speed(self.DEFAULT_SPEED)
        self.running = True
        print("Obstacle Avoidance Mode Started")

    def stop(self):
        self.running = False
        self.car.enable_ultrasonic(False)
        self.car.stop()
        print("Obstacle Avoidance Mode Stopped")

    def step(self):
        """
        Execute one step of the avoidance logic.
        Should be called in the main loop.
        """
        if not self.running:
            return

        dis = self.car.get_distance()
        # print(f"Distance: {dis} mm")

        if dis < self.NEAR_DISTANCE:
            print(f"Obstacle Very Close ({dis}mm): Backing Up")
            self.car.move_backward()
            time.sleep(0.1) 
            
        elif self.NEAR_DISTANCE <= dis <= self.FAR_DISTANCE:
            print(f"Obstacle Detected ({dis}mm): Turning Left")
            self.car.stop()
            time.sleep(0.1)
            self.car.rotate_left()
            time.sleep(0.15)
            
        elif dis > self.FAR_DISTANCE:
            # Clear path
            self.car.move_forward()
            
        else:
            # Unknown/Error (e.g. 0 reading?)
            self.car.stop()
            
        # Small delay to prevent I2C flooding
        time.sleep(0.1) 
