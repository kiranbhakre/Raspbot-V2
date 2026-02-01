from Raspbot_Lib import Raspbot
import time

bot = Raspbot()

def test_hardware():
    print("--- Hardware Diagnostic Starting ---")
    
    # 1. Test Lights
    print("Testing Lights (Red)...")
    bot.Ctrl_WQ2812_ALL(1, 0) # Red
    time.sleep(2)
    print("Testing Lights (Green)...")
    bot.Ctrl_WQ2812_ALL(1, 1) # Green
    time.sleep(2)
    bot.Ctrl_WQ2812_ALL(0, 0) # Off
    
    # 2. Test Motors
    print("Testing Motors (All Forward at 100)...")
    print("IMPORTANT: Ensure motor power switch is ON and battery is connected.")
    for i in range(4):
        bot.Ctrl_Car(i, 0, 100)
    time.sleep(3)
    
    print("Stopping Motors...")
    for i in range(4):
        bot.Ctrl_Car(i, 0, 0)
    
    print("--- Diagnostic Complete ---")

if __name__ == "__main__":
    test_hardware()
