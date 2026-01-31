import RPi.GPIO as GPIO
import time
import signal
import sys

# Try to import the YB_Pcb_Car library. 
# If it doesn't exist (because we are not on the Raspbot image), we can use a mock for testing logic.
try:
    from YB_Pcb_Car import YB_Pcb_Car
except ImportError:
    print("Warning: YB_Pcb_Car library not found. Using Mock class for demonstration.")
    class YB_Pcb_Car:
        def Car_Run(self, speed1, speed2):
            print(f"Car Run: speed1={speed1}, speed2={speed2}")
        def Car_Back(self, speed1, speed2):
            print(f"Car Back: speed1={speed1}, speed2={speed2}")
        def Car_Left(self, speed1, speed2):
            print(f"Car Left: speed1={speed1}, speed2={speed2}")
        def Car_Right(self, speed1, speed2):
            print(f"Car Right: speed1={speed1}, speed2={speed2}")
        def Car_Spin_Left(self, speed1, speed2):
            print(f"Car Spin Left: speed1={speed1}, speed2={speed2}")
        def Car_Spin_Right(self, speed1, speed2):
            print(f"Car Spin Right: speed1={speed1}, speed2={speed2}")
        def Car_Stop(self):
            print("Car Stop")
        def Car_Run_Speed(self, speed):
            # Assuming omnidirectional control might be simpler in some versions
            print(f"Car Run Speed: {speed}")

# IR Remote Key Codes (NEC Protocol)
# Based on Yahboom Raspbot V2 documentation
IR_KEYS = {
    'Power': 0x00,
    'Up': 0x01,
    'Light': 0x02,
    'Left': 0x04,
    'Sound': 0x05,
    'Right': 0x06,
    'Turn_Left': 0x08,
    'Down': 0x09,
    'Turn_Right': 0x0A,
    'Plus': 0x0C,
    'Zero': 0x0D,
    'Minus': 0x0E,
    'One': 0x10,
    'Two': 0x11,
    'Three': 0x12,
    'Four': 0x14,
    'Five': 0x15,
    'Six': 0x16,
    'Seven': 0x18,
    'Eight': 0x19,
    'Nine': 0x1A
}

# Pin definition for IR Receiver
# Note: This often varies. Common pins are GPIO 17, 18 or specific pins on the expansion board.
# Ensure this matches your hardware connection.
PIN_IR = 17 

class IR_Remote_Car:
    def __init__(self):
        self.car = YB_Pcb_Car()
        self.speed = 150  # Default speed
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_IR, GPIO.IN)
        
    def handle_key(self, key_code):
        """Execute action based on IR key code"""
        print(f"Processing Key Code: {key_code}")
        
        # Movement controls
        if key_code == IR_KEYS['Up']:
            self.car.Car_Run(self.speed, self.speed)
        elif key_code == IR_KEYS['Down']:
            self.car.Car_Back(self.speed, self.speed)
        elif key_code == IR_KEYS['Left']:
            self.car.Car_Left(self.speed, self.speed)
        elif key_code == IR_KEYS['Right']:
            self.car.Car_Right(self.speed, self.speed)
        elif key_code == IR_KEYS['Turn_Left']:
            self.car.Car_Spin_Left(self.speed, self.speed)
        elif key_code == IR_KEYS['Turn_Right']:
            self.car.Car_Spin_Right(self.speed, self.speed)
        elif key_code == IR_KEYS['Power']: # Uses Power button as Stop
            self.car.Car_Stop()
        
        # Speed controls
        elif key_code == IR_KEYS['Plus']:
            self.speed = min(255, self.speed + 10)
            print(f"Speed increased to {self.speed}")
        elif key_code == IR_KEYS['Minus']:
            self.speed = max(0, self.speed - 10)
            print(f"Speed decreased to {self.speed}")
            
        else:
            print("Unknown or Unmapped Key")

    def read_ir(self):
        """
        Simple software-based IR reading. 
        Note: For production, using 'lirc' or 'ir-keytable' with system drivers 
        is much more reliable than Python polling. 
        This is a simplified example of logic.
        """
        # In a real scenario without lirc, we would need a robust decoder function here,
        # which counts pulse widths (NEC protocol: 9ms header, 4.5ms space, etc.)
        # Since implementing a full NEC decoder in pure Python on a non-RTOS system
        # like Raspberry Pi is flaky, we recommend using the system's 'lirc' or 'evdev'.
        
        # Placeholder for where you would integrate the 'lirc' read or 'evdev' event loop.
        # For now, we wait for a raw input to simulate key presses for testing purposes
        # if the hardware isn't attached.
        print("Waiting for IR signal (Simulation mode: Use 'evdev' implementation for real hardware)")
        # To actually drive this, you would typically use:
        # import evdev
        # device = evdev.InputDevice('/dev/input/eventX')
        # for event in device.read_loop(): ...
        pass

    def cleanup(self):
        self.car.Car_Stop()
        GPIO.cleanup()

def main():
    bot = IR_Remote_Car()
    print("IR Remote Car Control Started")
    print("Press Ctrl+C to exit")
    
    try:
        # Example loop using a hypothetical 'lirc' socket or 'evdev' could go here.
        # Since we don't have the library, we'll keep the process alive.
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        bot.cleanup()

if __name__ == '__main__':
    main()
