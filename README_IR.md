
# IR Control Setup for Raspbot V2

This project contains a modular Python control system for the Yahboom Raspbot V2 using an IR remote.

## Features

1.  **Manual Control**: Drive the car using the directional buttons.
2.  **Obstacle Avoidance**: Autonomous mode using the ultrasonic sensor.
3.  **Light Control**: Cycle through RGB colors.

## File Structure

*   `remote_control_main.py`: **Main Entry Point**. Run this script to start the remote control program.
*   `car_driver.py`: Class `CarDriver` handling motor movements, lights, and sensors.
*   `auto_driver.py`: Class `ObstacleAvoidance` handling autonomous logic.
*   `ir_decoder.py`: Class `IRRemote` handling IR signal reception.
*   `Raspbot_Lib.py`: Low-level hardware driver.

## Prerequisites

1.  **Hardware**: Yahboom Raspbot V2 with IR Receiver and Ultrasonic Sensor.
2.  **System**: Raspberry Pi with I2C enabled.
3.  **Dependencies**: `python3-smbus`.

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
| **Sound** | **Toggle Obstacle Avoidance Mode** |
| **Light** | Cycle LED Colors / Off |
| **Power** | Stop |
| **+ / -** | Adjustment Speed |

### Obstacle Avoidance Mode
Press **Sound** to enable. The car will move forward automatically. If it detects an obstacle (< 40cm), it will stop and turn left. If it gets too close (< 20cm), it will back up. Press **Sound** again to return to Manual Mode.
