
import time
from car_driver import CarDriver
from ir_decoder import IRRemote

def main():
    print("Initializing Modular IR Test...")
    
    # 1. Init Driver
    try:
        car = CarDriver()
        print("CarDriver initialized.")
    except Exception as e:
        print(f"CarDriver init failed: {e}")
        return

    # 2. Init IR
    try:
        ir = IRRemote(car.get_bot_instance())
        print("IRRemote initialized. Enabled switch.")
    except Exception as e:
        print(f"IRRemote init failed: {e}")
        return
    
    print("Testing IR... Press buttons on remote. (Ctrl+C to stop)")
    print("If you see no output when pressing buttons, the issue is in reading/decoding.")
    
    last_val = -1
    
    try:
        while True:
            # Debug: Read raw direct from bot to compare
            # raw = car.get_bot_instance().read_data_array(0x0c, 1)[0]
            # if raw != 255:
            #    print(f"RAW: {raw}")
            
            # Read via module
            code = ir.read_code()
            
            if code is not None:
                name = ir.get_key_name(code)
                print(f"Decoded: {name} (Hex: {hex(code)})")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        ir.disable()

if __name__ == "__main__":
    main()
