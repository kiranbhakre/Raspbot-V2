
import time
import sys
import signal

from car_driver import CarDriver
from ir_decoder import IRRemote
from auto_driver import ObstacleAvoidance

def main():
    print("DEBUG: Initializing Raspbot Remote Control...")
    
    # Initialize Car Driver
    try:
        car = CarDriver()
        print("DEBUG: CarDriver initialized.")
    except Exception as e:
        print(f"ERROR: CarDriver init failed: {e}")

    # Initialize IR Remote
    try:
        # Pass the bot instance
        ir = IRRemote(car.get_bot_instance())
        print("DEBUG: IRRemote initialized.")
    except Exception as e:
        print(f"ERROR: IRRemote init failed: {e}")
    
    # Initialize Autopilot
    avoidance = ObstacleAvoidance(car)
    
    print("Ready! Press buttons on the remote.")
    print("Press 'Sound' (0x05) to toggle Obstacle Avoidance Mode.")
    print("Press Ctrl+C to exit.")
    
    running = True
    mode = 'MANUAL'
    
    # Debug counters
    loop_count = 0
    start_time = time.time()

    try:
        while running:
            loop_count += 1
            if loop_count % 100 == 0:
                # Print heartbeat every 100 loops (~1 sec)
                # print(f"DEBUG: Heartbeat (Mode: {mode})")
                pass

            # Read IR Code
            try:
                code = ir.read_code()
            except Exception as e:
                print(f"ERROR reading IR: {e}")
                code = None
            
            # --- IR Handling ---
            if code is not None:
                # print(f"DEBUG: Raw IR Code: {code}")
                key = ir.get_key_name(code)
                if key:
                    print(f"IR Key: {key} (Hex: {hex(code)})")
                    
                    if key == 'Sound':
                        print(f"DEBUG: Toggling Mode from {mode}...")
                        if mode == 'MANUAL':
                            mode = 'AUTO'
                            avoidance.start()
                        else:
                            mode = 'MANUAL'
                            avoidance.stop()
                        
                        # Debounce
                        time.sleep(0.3)
                        print(f"DEBUG: Mode is now {mode}")
                        continue

                    if mode == 'MANUAL':
                        # print(f"DEBUG: Executing Manual Command: {key}")
                        if key == 'Up': car.move_forward()
                        elif key == 'Down': car.move_backward()
                        elif key == 'Left': car.slide_left()
                        elif key == 'Right': car.slide_right()
                        elif key == 'Turn_Left': car.rotate_left()
                        elif key == 'Turn_Right': car.rotate_right()
                        elif key == 'Power' or key == 'Five' or key == 'Zero': car.stop()
                        elif key == 'Light': car.cycle_lights()
                        elif key == 'Plus': car.change_speed(20)
                        elif key == 'Minus': car.change_speed(-20)
                        
                        time.sleep(0.15)
                    else:
                        print(f"DEBUG: Ignored manual key {key} in AUTO mode")
                        
                else:
                    # print(f"DEBUG: Unknown key code {hex(code)}")
                    pass
            
            # --- Autonomous Loop ---
            if mode == 'AUTO':
                # print("DEBUG: Calling avoidance.step()")
                avoidance.step()
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        print("DEBUG: Cleanup...")
        avoidance.stop()
        car.stop()
        car.lights_off()
        ir.disable()
        print("Goodbye.")

if __name__ == '__main__':
    main()
