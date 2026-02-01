from Raspbot_Lib import Raspbot
import time

bot = Raspbot()
bot.Ctrl_Ulatist_Switch(1)
time.sleep(1)

print("Reading registers 0x1A and 0x1B separately vs together:")
for _ in range(10):
    # Separately
    h = bot.read_data_array(0x1b, 1)[0]
    l = bot.read_data_array(0x1a, 1)[0]
    sep_dis = (h << 8) | l
    
    # Together (Starting from 0x1A)
    data = bot.read_data_array(0x1a, 2)
    tog_dis = (data[1] << 8) | data[0]
    
    # Together (Starting from 0x1B) - less likely but worth checking if it's High-Low
    data2 = bot.read_data_array(0x1a, 2) # Wait, if it's 0x1b and then 0x1a, maybe it doesn't auto-increment forwards?
    # Usually it's 0x1a then 0x1b.
    
    print(f"Sep: {sep_dis}mm (H={h}, L={l}) | Tog: {tog_dis}mm (Data={data})")
    time.sleep(0.5)

bot.Ctrl_Ulatist_Switch(0)
