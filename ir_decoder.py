
import time

# IR Remote Key Codes (NEC Protocol)
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

class IRRemote:
    def __init__(self, bot_instance):
        """
        Initialize IR Remote.
        :param bot_instance: The Raspbot instance from the driver (shares I2C bus)
        """
        self.bot = bot_instance
        self.enabled = False
        self.enable()

    def enable(self):
        try:
            self.bot.Ctrl_IR_Switch(1)
            self.enabled = True
            print("IR Remote Enabled")
        except:
            print("Failed to enable IR request")

    def disable(self):
        try:
            self.bot.Ctrl_IR_Switch(0)
            self.enabled = False
        except:
            pass

    def read_code(self):
        """
        Reads one byte from the IR register.
        Returns the raw code (int) or None if no valid key press.
        """
        if not self.enabled:
            return None
            
        try:
            # 0x0C is the register for IR
            data = self.bot.read_data_array(0x0c, 1)
            if data and len(data) > 0:
                code = data[0]
                if code != 255: # 255 is idle/no data
                    return code
        except Exception as e:
            # print(f"IR Read Error: {e}")
            pass
            
        return None

    def get_key_name(self, code):
        """Returns the name of the key from the code, or None"""
        for name, key_code in IR_KEYS.items():
            if code == key_code:
                return name
        return None
