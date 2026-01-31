import time
import signal
import sys

# Try to import Raspbot library from the local file
try:
    from Raspbot_Lib import Raspbot
except ImportError:
    print("Raspbot_Lib.py not found or smbus not available.")
    print("Ensure Raspbot_Lib.py is in the same directory and smbus is installed (sudo apt-get install python3-smbus).")
    # Mock for testing on non-Pi environments
    class Raspbot:
        def Ctrl_Car(self, motor_id, motor_dir, motor_speed):
            print(f"Mock Ctrl_Car: id={motor_id}, dir={motor_dir}, speed={motor_speed}")
        def Ctrl_IR_Switch(self, state):
            print(f"Mock IR Switch: {state}")
        def read_data_array(self, reg, count):
            return [255] # Return no key by default
        def Ctrl_WQ2812_ALL(self, state, color):
            print(f"Mock Lights: State={state}, Color={color}")

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

class IR_Remote_Car:
    def __init__(self):
        try:
            self.bot = Raspbot()
        except Exception as e:
            print(f"Failed to initialize Raspbot: {e}")
            sys.exit(1)
            
        self.speed = 100  # Default speed (0-255)
        self.running = True
        
        # Light state management
        self.light_colors = [0, 1, 2, 3, 4, 5, 6] # Red, Green, Blue, Yellow, Purple, Cyan, White
        self.current_light_index = -1 # -1 means Off
        
        # Enable IR Receiver and Reset Lights
        try:
            self.bot.Ctrl_IR_Switch(1)
            self.bot.Ctrl_WQ2812_ALL(0, 0)
            print("IR Receiver Enabled and Lights Reset")
        except Exception as e:
            print(f"Error initializing hardware: {e}")
        
    def toggle_lights(self):
        """Cycle through colors and off state"""
        self.current_light_index += 1
        
        if self.current_light_index >= len(self.light_colors):
            # Turn lights off
            self.current_light_index = -1
            self.bot.Ctrl_WQ2812_ALL(0, 0)
            print("Lights Off")
        else:
            # Set next color
            color = self.light_colors[self.current_light_index]
            self.bot.Ctrl_WQ2812_ALL(1, color)
            print(f"Lights On: Color Index {color}")

    def drive_car(self, direction):
        """
        Control motor movements based on direction.
        L1=0, L2=1, R1=2, R2=3
        Dir 0 = Forward, 1 = Backward
        """
        speed = self.speed
        
        if direction == 'stop':
            for i in range(4):
                self.bot.Ctrl_Car(i, 0, 0)
            print("Car Stopped")
                
        elif direction == 'forward':
            print("Moving Forward")
            self.bot.Ctrl_Car(0, 0, speed) # L1 Fwd
            self.bot.Ctrl_Car(1, 0, speed) # L2 Fwd
            self.bot.Ctrl_Car(2, 0, speed) # R1 Fwd
            self.bot.Ctrl_Car(3, 0, speed) # R2 Fwd
            
        elif direction == 'backward':
            print("Moving Backward")
            self.bot.Ctrl_Car(0, 1, speed) # L1 Back
            self.bot.Ctrl_Car(1, 1, speed) # L2 Back
            self.bot.Ctrl_Car(2, 1, speed) # R1 Back
            self.bot.Ctrl_Car(3, 1, speed) # R2 Back
            
        elif direction == 'left': # Slide Left
            print("Sliding Left")
            self.bot.Ctrl_Car(0, 1, speed) # L1 Back
            self.bot.Ctrl_Car(1, 0, speed) # L2 Fwd
            self.bot.Ctrl_Car(2, 0, speed) # R1 Fwd
            self.bot.Ctrl_Car(3, 1, speed) # R2 Back
            
        elif direction == 'right': # Slide Right
            print("Sliding Right")
            self.bot.Ctrl_Car(0, 0, speed) # L1 Fwd
            self.bot.Ctrl_Car(1, 1, speed) # L2 Back
            self.bot.Ctrl_Car(2, 1, speed) # R1 Back
            self.bot.Ctrl_Car(3, 0, speed) # R2 Fwd
            
        elif direction == 'turn_left': # Rotate Left
            print("Turning Left")
            self.bot.Ctrl_Car(0, 1, speed) # L1 Back
            self.bot.Ctrl_Car(1, 1, speed) # L2 Back
            self.bot.Ctrl_Car(2, 0, speed) # R1 Fwd
            self.bot.Ctrl_Car(3, 0, speed) # R2 Fwd
            
        elif direction == 'turn_right': # Rotate Right
            print("Turning Right")
            self.bot.Ctrl_Car(0, 0, speed) # L1 Fwd
            self.bot.Ctrl_Car(1, 0, speed) # L2 Fwd
            self.bot.Ctrl_Car(2, 1, speed) # R1 Back
            self.bot.Ctrl_Car(3, 1, speed) # R2 Back

    def handle_key(self, key_code):
        """Execute action based on IR key code"""
        
        if key_code > 0x1A: # Ignore unused codes or noise
            return

        # Map key codes to actions
        if key_code == IR_KEYS['Up']:
            self.drive_car('forward')
        elif key_code == IR_KEYS['Down']:
            self.drive_car('backward')
        elif key_code == IR_KEYS['Left']:
            self.drive_car('left')
        elif key_code == IR_KEYS['Right']:
            self.drive_car('right')
        elif key_code == IR_KEYS['Turn_Left']:
            self.drive_car('turn_left')
        elif key_code == IR_KEYS['Turn_Right']:
            self.drive_car('turn_right')
        elif key_code == IR_KEYS['Power']: 
            self.drive_car('stop')
        elif key_code == IR_KEYS['Zero'] or key_code == IR_KEYS['Five']: # 5/0 also Stop if desired
            self.drive_car('stop')
        
        # Light control
        elif key_code == IR_KEYS['Light']:
            self.toggle_lights()

        # Speed controls
        elif key_code == IR_KEYS['Plus']:
            self.speed = min(255, self.speed + 20)
            print(f"Speed increased to {self.speed}")
        elif key_code == IR_KEYS['Minus']:
            self.speed = max(20, self.speed - 20)
            print(f"Speed decreased to {self.speed}")

    def loop(self):
        print("Listening for IR signals... Press Ctrl+C to exit.")
        last_code = 255
        try:
            while self.running:
                # Read IR data
                # 0x0C is the register for IR, reading 1 byte
                data = self.bot.read_data_array(0x0c, 1)
                
                if data and len(data) > 0:
                    code = data[0]
                    
                    # 255 usually means no key press
                    if code != 255:
                        self.handle_key(code)
                        # Wait a bit to avoid flooding and to act as a simple debounce
                        time.sleep(0.15)
                    
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        print("\nStopping...")
        self.bot.Ctrl_IR_Switch(0)
        self.bot.Ctrl_WQ2812_ALL(0, 0) # Turn off lights
        self.drive_car('stop')

def main():
    bot = IR_Remote_Car()
    bot.loop()

if __name__ == '__main__':
    main()
