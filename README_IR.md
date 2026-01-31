
# IR Control Setup for Raspbot V2

This project contains a modular Python control system for the Yahboom Raspbot V2 using an IR remote.

## File Structure

*   `remote_control_main.py`: **Main Entry Point**. Run this script to start the remote control program.
*   `car_driver.py`: Class `CarDriver` handling motor movements and light control.
*   `ir_decoder.py`: Class `IRRemote` handling IR signal reception and decoding.
*   `Raspbot_Lib.py`: Low-level hardware driver.

## Prerequisites

1.  **Hardware**: Yahboom Raspbot V2 with IR Receiver (enabled by the script).
2.  **System**: Raspberry Pi with I2C enabled (`sudo raspi-config` -> Interface Options -> I2C).
3.  **Dependencies**:
    *   `python3-smbus`: Required for I2C communication.
        ```bash
        sudo apt-get update
        sudo apt-get install python3-smbus
        ```

## How to Run

1.  Run the main script:
    ```bash
    sudo python3 remote_control_main.py
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
| **Light** | Cycle LED Colors / Off |
| **Power** | Stop |
| **0 / 5** | Stop |
| **+** | Increase Speed |
| **-** | Decrease Speed |

## Troubleshooting

*   **Motors not moving?** Ensure the battery is charged and the motor switch is ON.
*   **IR not responding?** Point the remote directly at the IR receiver. Make sure the IR switch is enabled (the script does this automatically).
