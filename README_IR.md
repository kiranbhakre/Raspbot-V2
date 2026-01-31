
# IR Control Setup for Raspbot V2

This project contains a Python script `IR_Car_Drive.py` designed to control the Yahboom Raspbot V2 using an IR remote.

## Prerequisites

1.  **Hardware Connection**: Ensure your IR receiver is connected to the correct GPIO pin (Default logic assumes a standard setup, but you may need to configure `lirc` or `dtoverlay`).
2.  **Dependencies**:
    *   `RPi.GPIO`
    *   `YB_Pcb_Car.py`: This library is required to drive the motors. It is usually pre-installed on the Yahboom Raspbot image in `/home/pi/Yahboom_Project/Raspbot/`. If you are running this on a fresh install, we recommend downloading the driver from the [Yahboom Official Website](https://www.yahboom.net/study/Raspbot-V2) or copying it from the provided courses.

3.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  Make sure `YB_Pcb_Car.py` is in the same directory as `IR_Car_Drive.py`.
2.  Run the script:
    ```bash
    sudo python3 IR_Car_Drive.py
    ```

## Key Mappings

| Remote Key | Action |
| :--- | :--- |
| **Up** | Move Forward |
| **Down** | Move Backward |
| **Left** | Move Side Left |
| **Right** | Move Side Right |
| **Turn Left** | Rotate Left |
| **Turn Right** | Rotate Right |
| **Power** | Stop |
| **+** | Increase Speed |
| **-** | Decrease Speed |

## Troubleshooting

*   **Motors not moving?** Verify that `YB_Pcb_Car.py` is correctly importing and communicating with the I2C bus. You may need to enable I2C in `raspi-config`.
*   **IR not responding?** The script currently uses a placeholder for IR reading logic. For the best experience, configure `lirc` on your Raspberry Pi to map IR signals to system keys or use `evdev` to read the input device directly.
