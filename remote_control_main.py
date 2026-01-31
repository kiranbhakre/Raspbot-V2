
import time
import sys
import signal

from car_driver import CarDriver
from ir_decoder import IRRemote

def main():
    print("Initializing Raspbot Remote Control...")
    
    # Initialize Car Driver
    car = CarDriver()
    
    # Initialize IR Remote (passing the bot instance to share I2C)
    ir = IRRemote(car.get_bot_instance())
    
    print("Ready! Press buttons on the remote.")
    print("Press Ctrl+C to exit.")
    
    running = True

    try:
        while running:
            # Read IR Code
            code = ir.read_code()
            
            if code is not None:
                key = ir.get_key_name(code)
                if key:
                    print(f"IR Key: {key} (Hex: {hex(code)})")
                    
                    # --- Mapping Logic ---
                    
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
                    # Unknown key
                    # print(f"Unknown Code: {hex(code)}")
                    pass
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        # Cleanup
        car.stop()
        car.lights_off()
        ir.disable()
        print("Goodbye.")

if __name__ == '__main__':
    main()
