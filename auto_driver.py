
import time

class ObstacleAvoidance:
    def __init__(self, car_driver):
        self.car = car_driver
        self.running = False
        
        # Tuning for better safety
        self.NEAR_DISTANCE = 300 # Back up if closer than 30cm
        self.FAR_DISTANCE = 500  # Turn if closer than 50cm
        self.DEFAULT_SPEED = 40  # Slower speed for safety

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
        
        # SAFETY CHECK: 0 usually means error/timeout.
        # If we ignore it, the car keeps its previous state (moving).
        # We MUST stop if we don't know where we are.
        if dis == 0 or dis > 4500:
            # print("Sensor Invalid (0mm). Stopping for safety.")
            self.car.stop()
            return

        # print(f"Auto Distance: {dis}mm")

        if dis < self.NEAR_DISTANCE:
            # Emergency Stop & Back up
            print(f"OBSTACLE ({dis}mm)! Backing up...")
            self.car.stop() 
            self.car.move_backward()
            time.sleep(0.4) # Commit to backing up for 0.4s
            self.car.stop() # Then stop before reassessing
            
        elif dis <= self.FAR_DISTANCE:
            # Too close to proceed, turn away
            print(f"Object detected ({dis}mm). Turning...")
            self.car.stop()
            self.car.rotate_left()
            time.sleep(0.3) # Commit to turning
            self.car.stop()
            
        else:
            # Clear path
            self.car.move_forward()
            
        # Pacing
        time.sleep(0.05)
