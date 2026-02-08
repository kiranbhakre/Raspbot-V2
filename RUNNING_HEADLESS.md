# Running Vision System over SSH (Headless Mode)

## The Problem

When running over SSH without X11 forwarding, OpenCV's `cv2.imshow()` fails with:
```
qt.qpa.xcb: could not connect to display
```

## Solutions

### Option 1: Headless Mode (Recommended for SSH)

Use the headless script that doesn't require a display:

```bash
cd /home/pi/Raspbot-V2
source .venv/bin/activate
python vision_system_headless.py --mode face --duration 30
```

**Features:**
- Runs without display
- Prints detection info to console
- Saves snapshot frames every 5 seconds
- Shows servo positions
- Perfect for SSH access

**Arguments:**
- `--mode`: face, gesture, or 3d_object
- `--duration`: How long to run (seconds)
- `--save-interval`: Save frame every N seconds
- `--camera`: Camera device ID (default: 0)

**Examples:**
```bash
# Test face recognition for 60 seconds
python vision_system_headless.py --mode face --duration 60

# Test gesture recognition, save every 10 seconds
python vision_system_headless.py --mode gesture --duration 120 --save-interval 10

# Test 3D object detection
python vision_system_headless.py --mode 3d_object --duration 30
```

### Option 2: X11 Forwarding over SSH

Enable X11 forwarding when connecting:

```bash
# On your local machine, connect with X11:
ssh -X pi@raspberrypi

# Then run the demo:
python vision_system_demo.py
```

**Note**: This requires X server on your local machine (XQuartz on Mac, VcXsrv on Windows)

### Option 3: VNC Remote Desktop

1. Enable VNC on Raspberry Pi:
   ```bash
   sudo raspi-config
   # Interface Options > VNC > Enable
   ```

2. Connect with VNC viewer (RealVNC, TightVNC, etc.)

3. Run the demo in the VNC session:
   ```bash
   python vision_system_demo.py
   ```

### Option 4: Direct HDMI Display

Connect monitor directly to Raspberry Pi HDMI port and run locally.

## Checking Saved Frames

When using headless mode, frames are saved to the current directory:

```bash
# List saved frames
ls -lh vision_frame_*.jpg

# View frame information
file vision_frame_5s.jpg

# Download frames to your local machine
scp pi@raspberrypi:~/Raspbot-V2/vision_frame_*.jpg ./
```

## Troubleshooting

### Camera Tracking Issues

If the camera moves but doesn't focus on faces:

1. **Check lighting**: Ensure good, even lighting
2. **Adjust tracking parameters** in `vision_config.json`:
   ```json
   "servos": {
     "dead_zone": 0.15,
     "max_step": 8
   }
   ```
3. **Test servo range**: 
   ```bash
   python camera_controller.py
   # Use arrow keys to test servo movement
   ```

### Performance Issues

If experiencing lag or low FPS:

1. **Reduce resolution**:
   ```bash
   python vision_system_headless.py --width 320 --height 240
   ```

2. **Use single feature** instead of "all" mode

3. **Check CPU temperature**:
   ```bash
   vcgencmd measure_temp
   ```

## Servo Tracking Calibration

To improve face tracking accuracy:

1. Run camera controller test:
   ```bash
   python camera_controller.py
   ```

2. Use arrow keys to manually test servo movement

3. Note the optimal pan/tilt center positions

4. Update `vision_config.json` if needed:
   ```json
   "servos": {
     "pan_center": 90,
     "tilt_center": 55
   }
   ```

## Remote Web Viewer (Advanced)

For a web-based interface over network, you can use the included MJPEG server:

```bash
# Check if available
ls ~/Camera_Web_Preview/mjpeg_server.py

# Run the web server (if available)
python ~/Camera_Web_Preview/mjpeg_server.py
```

Then access from browser: `http://raspberrypi:8080`
