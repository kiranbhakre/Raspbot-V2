
print("DEBUG: Script Start (Pre-imports)")
import time
import sys
import signal

# Flush stdout to force print visibility
sys.stdout.flush()

try:
    print("DEBUG: Importing car_driver...")
    from car_driver import CarDriver
    print("DEBUG: car_driver imported.")
except Exception as e:
    print(f"CRITICAL ERROR importing car_driver: {e}")
    sys.exit(1)

try:
    print("DEBUG: Importing ir_decoder...")
    from ir_decoder import IRRemote
    print("DEBUG: ir_decoder imported.")
except Exception as e:
    print(f"CRITICAL ERROR importing ir_decoder: {e}")
    sys.exit(1)

try:
    print("DEBUG: Importing auto_driver...")
    from auto_driver import ObstacleAvoidance
    print("DEBUG: auto_driver imported.")
except Exception as e:
    print(f"CRITICAL ERROR importing auto_driver: {e}")
    sys.exit(1)

def main():
    print("DEBUG: Entering main()...")
    sys.stdout.flush()
    
    # Initialize Car Driver
    try:
        car = CarDriver()
        print("DEBUG: CarDriver initialized.")
    except Exception as e:
        print(f"ERROR: CarDriver init failed: {e}")
        return

    # Initialize IR Remote
    try:
        # Pass the bot instance
        ir = IRRemote(car.get_bot_instance())
        print("DEBUG: IRRemote initialized.")
    except Exception as e:
        print(f"ERROR: IRRemote init failed: {e}")
        return
    
    # Initialize Autopilot
    try:
        avoidance = ObstacleAvoidance(car)
        print("DEBUG: ObstacleAvoidance initialized.")
    except Exception as e:
        print(f"ERROR: ObstacleAvoidance init failed: {e}")
        return
    
    print("Ready! Press buttons on the remote.")
    
    running = True
    mode = 'MANUAL'
    loop_count = 0

    try:
        while running:
            # Heartbeat to prove it's alive
            loop_count += 1
            if loop_count % 100 == 0:
                # print(".", end="", flush=True) 
                pass

            # Read IR Code
            try:
                code = ir.read_code()
            except Exception as e:
                print(f"ERROR reading IR: {e}")
                code = None
            
            # --- IR Handling ---
            if code is not None:
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
                        
                        time.sleep(0.3)
                        continue

                    if mode == 'MANUAL':
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
                    pass
            
            # --- Autonomous Loop ---
            if mode == 'AUTO':
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
