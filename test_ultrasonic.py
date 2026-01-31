
import time
from car_driver import CarDriver

def main():
    print("Initializing Ultrasonic Sensor Test...")
    car = CarDriver()
    
    # Enable sensor
    car.enable_ultrasonic(True)
    time.sleep(1) # Give it time to start up
    
    print("Testing... Press Ctrl+C to stop.")
    
    try:
        while True:
            # Read distance
            dist = car.get_distance()
            
            print(f"Distance: {dist} mm")
            
            if dist == 0:
                print("Warning: Reading 0mm (Check wirings or sensor position)")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopping Test...")
    
    finally:
        car.enable_ultrasonic(False)
        car.stop()

if __name__ == "__main__":
    main()
