
# IR Control Setup for Raspbot V2

This project contains a Python script `IR_Car_Drive.py` designed to control the Yahboom Raspbot V2 using an IR remote.

## Prerequisites

1.  **Hardware**: Yahboom Raspbot V2 with IR Receiver (enabled by the script).
2.  **System**: Raspberry Pi with I2C enabled (`sudo raspi-config` -> Interface Options -> I2C).
3.  **Dependencies**:
    *   `python3-smbus`: Required for I2C communication.
        ```bash
        sudo apt-get update
        sudo apt-get install python3-smbus
        ```
    *   `Raspbot_Lib.py`: (Included) This library works with the Raspbot hardware.

## How to Run

1.  Ensure `Raspbot_Lib.py` is in the same directory as `IR_Car_Drive.py`.
2.  Run the script:
    ```bash
    sudo python3 IR_Car_Drive.py
    ```

## Key Mappings

| Remote Key | Action |
| :--- | :--- |
| **Up** | Move Forward |
| **Down** | Move Backward |
| **Left** | Slide Left (Mechanum) |
| **Right** | Slide Right (Mechanum) |
| **Turn Left** | Rotate Left |
| **Turn Right** | Rotate Right |
| **Power** | Stop |
| **0 / 5** | Stop |
| **+** | Increase Speed |
| **-** | Decrease Speed |

## Troubleshooting

*   **Motors not moving?** Ensure the battery is charged and the motor switch is ON.
*   **IR not responding?** Point the remote directly at the IR receiver. Make sure the IR switch is enabled (the script does this automatically).
