
import time
import sys
import signal

from car_driver import CarDriver
from ir_decoder import IRRemote
from auto_driver import ObstacleAvoidance

def main():
    print("Initializing Raspbot Remote Control...")
    
    # Initialize Car Driver
    car = CarDriver()
    
    # Initialize IR Remote (passing the bot instance to share I2C)
    ir = IRRemote(car.get_bot_instance())
    
    # Initialize Obstacle Avoidance
    avoidance = ObstacleAvoidance(car)
    
    print("Ready! Press buttons on the remote.")
    print("Press 'Sound' (0x05) to toggle Obstacle Avoidance Mode.")
    print("Press Ctrl+C to exit.")
    
    running = True
    mode = 'MANUAL' # MANUAL or AUTO

    try:
        while running:
            # Read IR Code
            code = ir.read_code()
            
            # --- IR Handling ---
            if code is not None:
                key = ir.get_key_name(code)
                if key:
                    print(f"IR Key: {key} (Hex: {hex(code)})")
                    
                    # Global Controls (Always Active)
                    if key == 'Sound':
                        # Toggle Mode
                        if mode == 'MANUAL':
                            mode = 'AUTO'
                            avoidance.start()
                        else:
                            mode = 'MANUAL'
                            avoidance.stop()
                        
                        # Debounce
                        time.sleep(0.3)
                        continue

                    # Manual Controls (Only in MANUAL mode)
                    if mode == 'MANUAL':
                        # Movement
                        if key == 'Up':
                            car.move_forward()
                        elif key == 'Down':
                            car.move_backward()
                        elif key == 'Left':
                            car.slide_left()
                        elif key == 'Right':
                            car.slide_right()
                        elif key == 'Turn_Left':
                            car.rotate_left()
                        elif key == 'Turn_Right':
                            car.rotate_right()
                            
                        # Stop
                        elif key == 'Power' or key == 'Five' or key == 'Zero':
                            car.stop()
                            
                        # Lights
                        elif key == 'Light':
                            car.cycle_lights()
                            
                        # Speed
                        elif key == 'Plus':
                            car.change_speed(20)
                        elif key == 'Minus':
                            car.change_speed(-20)
                            
                        # Debounce / Input pacing
                        time.sleep(0.15)
                    else:
                        print("Ignored manual command in AUTO mode (Press Sound to exit)")
                        
                else:
                    # Unknown key
                    pass
            
            # --- Autonomous Loop ---
            if mode == 'AUTO':
                avoidance.step()
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        # Cleanup
        avoidance.stop()
        car.stop()
        car.lights_off()
        ir.disable()
        print("Goodbye.")

if __name__ == '__main__':
    main()
