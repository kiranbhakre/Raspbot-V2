# Vision System for Raspbot V2

Complete camera vision system with face recognition, gesture recognition, and 3D object detection.

## Features

### 🎥 Camera Control
- USB camera capture with configurable resolution
- Thread-safe frame access
- Pan/tilt servo control for camera tracking
- Automatic reconnection on failure

### 👤 Face Recognition
- Real-time face detection using MediaPipe
- Face database with JSON storage
- Face encoding and recognition
- Camera tracking for detected faces
- Supports multiple faces

### 👋 Gesture Recognition
- Hand detection and tracking using MediaPipe Hands
- Recognizes gestures:
  - ✋ Open Palm / Stop
  - 👍 Thumbs Up / 👎 Thumbs Down
  - ✌️ Peace Sign
  - 👉 Pointing
  - ✊ Fist
  - 👌 OK Sign
- Multi-hand detection (up to 2 hands)
- Callback system for gesture events

### 📦 3D Object Detection
- 3D bounding box detection using MediaPipe Objectron
- Supported objects: Shoe, Chair, Cup, Camera
- Depth/distance estimation
- Real-time 3D object tracking
- Object pose estimation

### 🤖 Robot Integration
- Face following mode (robot tracks and follows faces)
- Gesture control mode (control robot with hand gestures)
- Servo tracking for smooth camera movement

## Installation

### 1. Install Dependencies

```bash
cd /home/pi/Raspbot-V2
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Camera

```bash
python vision_system_demo.py --test-camera
```

## Usage

### Vision System Demo

Unified demo with all features:

```bash
python vision_system_demo.py
```

**Controls:**
- `q` - Quit
- `m` - Switch mode (face/gesture/3d_object/all)
- `r` - Reset camera servos
- `a` - Add face to database (face mode)
- `1-4` - Change object type (3d_object mode)

**Modes:**
- `face` - Face detection and recognition
- `gesture` - Hand gesture recognition
- `3d_object` - 3D object detection
- `all` - All features simultaneously

### Individual Module Tests

**Test Camera Controller:**
```bash
python camera_controller.py
```

**Test Face Recognition:**
```bash
python face_recognition_module.py
```

**Test Gesture Recognition:**
```bash
python gesture_recognition_module.py
```

**Test 3D Object Detection:**
```bash
python object_3d_detection_module.py
```

### Robot Integration

**Face Following Mode:**
```bash
python vision_tracking.py --mode face
```
Robot will track and follow detected faces.

**Gesture Control Mode:**
```bash
python vision_tracking.py --mode gesture
```

Gesture commands:
- ✋ **Open Palm / Fist**: Stop
- 👍 **Thumbs Up**: Move forward
- 👎 **Thumbs Down**: Move backward
- 👉 **Pointing**: Turn (left/right based on hand position)
- ✌️ **Peace**: Spin

## Files

### Core Modules
- `camera_controller.py` - Camera capture and servo control
- `vision_utils.py` - Helper functions and utilities
- `face_recognition_module.py` - Face detection and recognition
- `gesture_recognition_module.py` - Hand gesture recognition
- `object_3d_detection_module.py` - 3D object detection

### Integration
- `vision_system_demo.py` - Unified demonstration script
- `vision_tracking.py` - Robot movement integration
- `vision_config.json` - Configuration parameters

### Data
- `face_database.json` - Face recognition database (created on first use)

## Configuration

Edit `vision_config.json` to customize:
- Camera settings (resolution, FPS)
- Servo parameters (range, speed)
- Detection confidence thresholds
- Robot movement speeds

## Troubleshooting

### Camera Not Found
- Check camera connection: `ls /dev/video*`
- Try different device ID: `python vision_system_demo.py --camera 1`

### Low FPS / Performance Issues
- Reduce resolution: `--width 320 --height 240`
- Use single module instead of 'all' mode
- Close other applications using camera

### Face Recognition Not Working
- Ensure good lighting
- Add faces to database with `a` key
- Adjust `recognition_threshold` in config

### Gesture Recognition Issues
- Ensure hands are clearly visible
- Try different lighting conditions
- Keep hands within camera frame

### Servos Not Moving
- Check I2C connection to expansion board
- Verify servo power supply
- Test with `camera_controller.py`

## Examples

### Add Faces to Database
1. Run: `python vision_system_demo.py --mode face`
2. Position face in frame
3. Press `a` and enter name
4. Face is now in database

### Control Robot with Gestures
```bash
python vision_tracking.py --mode gesture
```
Show thumbs up to move forward, peace sign to spin!

### Detect 3D Objects
```bash
python vision_system_demo.py --mode 3d_object
```
Press 1-4 to switch between shoe/chair/cup/camera detection.

## Performance Tips

1. **Good Lighting**: Ensure adequate, even lighting for best results
2. **Camera Position**: Mount camera at appropriate height and angle
3. **Resolution**: Use 640x480 for balanced performance/quality
4. **Single Focus**: Use individual modules for best performance
5. **CPU Usage**: Close unnecessary applications on Raspberry Pi

## Credits

Built using:
- **OpenCV** - Computer vision library
- **MediaPipe** - ML solutions for face, hands, and objects
- **NumPy** - Numerical computing

## License

Part of Raspbot V2 project by Yahboom Technology
