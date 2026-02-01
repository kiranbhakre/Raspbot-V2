
import time
import sys

# Try to import Raspbot library
try:
    from Raspbot_Lib import Raspbot
except ImportError:
    # This mock is essential for testing on non-Pi systems or if lib is missing
    print("Raspbot_Lib.py not found. Using Mock.")
    class Raspbot:
        def __init__(self, *args, **kwargs): pass
        def Ctrl_Car(self, *args, **kwargs): pass
        def Ctrl_IR_Switch(self, *args, **kwargs): pass
        def read_data_array(self, *args, **kwargs): return [255]
        def Ctrl_WQ2812_ALL(self, *args, **kwargs): pass
        def Ctrl_Ulatist_Switch(self, *args, **kwargs): pass
        def Ctrl_WQ2812_brightness_ALL(self, *args, **kwargs): pass

class MockRaspbot:
    def Ctrl_Car(self, motor_id, motor_dir, motor_speed): pass
    def Ctrl_IR_Switch(self, state): pass
    def read_data_array(self, reg, count): return [255]
    def Ctrl_WQ2812_ALL(self, state, color): pass
    def Ctrl_Ulatist_Switch(self, state): pass
    def Ctrl_WQ2812_brightness_ALL(self, r, g, b): pass

class CarDriver:
    def __init__(self):
        try:
            self.bot = Raspbot()
        except Exception as e:
            print(f"Hardware initialization failed ({e}). Using Mock.")
            self.bot = MockRaspbot()
            
        self.speed = 100
        
        # Light state
        self.light_colors = [0, 1, 2, 3, 4, 5, 6] # Red, Green, Blue, Yellow, Purple, Cyan, White
        self.current_light_index = -1 
        
        # Reset
        try:
            self.stop()
            self.lights_off()
        except:
            pass

    def set_speed(self, speed):
        """Set the movement speed (0-255)"""
        self.speed = max(0, min(255, speed))
        print(f"Speed set to {self.speed}")

    def change_speed(self, delta):
        """Change speed by a delta amount"""
        self.set_speed(self.speed + delta)

    def stop(self):
        """Stop all motors"""
        for i in range(4):
            self.bot.Ctrl_Car(i, 0, 0)
        print("Car Stopped")

    def move_forward(self):
        s = self.speed
        self.bot.Ctrl_Car(0, 0, s)
        self.bot.Ctrl_Car(1, 0, s)
        self.bot.Ctrl_Car(2, 0, s)
        self.bot.Ctrl_Car(3, 0, s)
        # print("Moving Forward")

    def move_backward(self):
        s = self.speed
        self.bot.Ctrl_Car(0, 1, s)
        self.bot.Ctrl_Car(1, 1, s)
        self.bot.Ctrl_Car(2, 1, s)
        self.bot.Ctrl_Car(3, 1, s)
        # print("Moving Backward")

    def slide_left(self):
        s = self.speed
        self.bot.Ctrl_Car(0, 1, s)
        self.bot.Ctrl_Car(1, 0, s)
        self.bot.Ctrl_Car(2, 0, s)
        self.bot.Ctrl_Car(3, 1, s)
        print("Sliding Left")

    def slide_right(self):
        s = self.speed
        self.bot.Ctrl_Car(0, 0, s)
        self.bot.Ctrl_Car(1, 1, s)
        self.bot.Ctrl_Car(2, 1, s)
        self.bot.Ctrl_Car(3, 0, s)
        print("Sliding Right")

    def rotate_left(self):
        s = self.speed
        self.bot.Ctrl_Car(0, 1, s)
        self.bot.Ctrl_Car(1, 1, s)
        self.bot.Ctrl_Car(2, 0, s)
        self.bot.Ctrl_Car(3, 0, s)
        print("Rotating Left")

    def rotate_right(self):
        s = self.speed
        self.bot.Ctrl_Car(0, 0, s)
        self.bot.Ctrl_Car(1, 0, s)
        self.bot.Ctrl_Car(2, 1, s)
        self.bot.Ctrl_Car(3, 1, s)
        print("Rotating Right")

    def lights_off(self):
        self.bot.Ctrl_WQ2812_ALL(0, 0)
        self.current_light_index = -1
        print("Lights Off")

    def cycle_lights(self):
        """Cycle to the next color"""
        self.current_light_index += 1
        
        if self.current_light_index >= len(self.light_colors):
            self.lights_off()
        else:
            color = self.light_colors[self.current_light_index]
            self.bot.Ctrl_WQ2812_ALL(1, color)
            print(f"Lights On: Color {color}")
            
    def get_bot_instance(self):
        """Return the underlying bot instance if needed by other modules (like IR)"""
        return self.bot
        
    def enable_ultrasonic(self, enable=True):
        """Enable or disable the ultrasonic sensor"""
        try:
            self.bot.Ctrl_Ulatist_Switch(1 if enable else 0)
            print(f"Ultrasonic Sensor {'Enabled' if enable else 'Disabled'}")
        except:
            print("Failed to toggle Ultrasonic Sensor")

    def get_distance(self):
        """
        Get distance from ultrasonic sensor in mm.
        Returns distance or 0 if read fails after retries.
        """
        for _ in range(3): # Retry up to 3 times
            try:
                # 0x1b is High byte, 0x1a is Low byte
                # Attempt to read both if possible, but Raspbot_Lib example uses separate
                data_h = self.bot.read_data_array(0x1b, 1)
                data_l = self.bot.read_data_array(0x1a, 1)
                
                if data_h and data_l:
                    diss_H = data_h[0]
                    diss_L = data_l[0]
                    dis = (diss_H << 8) | diss_L
                    if dis > 0: # Ignore 0 readings as likely errors unless they persist
                        return dis
                
                time.sleep(0.01) # Small delay before retry
            except Exception as e:
                # print(f"DEBUG: Sonar read error: {e}")
                time.sleep(0.01)
        return 0
