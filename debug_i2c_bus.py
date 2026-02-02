import smbus2 as smbus
import time

def test_bus(bus_id):
    print(f"Testing I2C Bus {bus_id}...")
    try:
        bus = smbus.SMBus(bus_id)
        # Try to write to the motor register 0x01
        # motor_id=0, motor_dir=0, motor_speed=100
        # This should move the L1 motor forward if correct
        bus.write_i2c_block_data(0x2b, 0x01, [0, 0, 100])
        print(f"SUCCESS: Write to Bus {bus_id} at 0x2b succeeded!")
        time.sleep(1)
        # Stop
        bus.write_i2c_block_data(0x2b, 0x01, [0, 0, 0])
        return True
    except Exception as e:
        print(f"FAILED: Bus {bus_id} - {e}")
        return False

for b in [1, 11, 12, 0]:
    if test_bus(b):
        print(f"FOUND WORKING BUS: {b}")
        break
