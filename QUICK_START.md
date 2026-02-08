# 🤖 Raspbot V2 Vision System - Quick Start Guide

## 🚀 ONE-CLICK LAUNCHER

### GUI Control Center (Recommended)

**Double-click to run:**
```bash
./launch_vision.sh
```

Or run directly:
```bash
python vision_control_center.py
```

This opens a beautiful GUI with buttons for:
- 🌐 **Web Viewer** - Live camera stream in browser (best option!)
- 👤 **Face Recognition** - Headless mode
- 👋 **Gesture Detection** - Headless mode  
- 📦 **3D Object Detection** - Headless mode
- 📹 **Video Recording** - Save to video file

---

## 📱 Quick Access Methods

### 1. Web Viewer (Best for Remote Access)
```bash
python vision_web_viewer.py
```
Then open in browser: **http://raspberrypi:5000**

**Features:**
- ✅ Live camera stream
- ✅ Switch modes with buttons (Face/Gesture/3D/All/Raw)
- ✅ Start/stop recording
- ✅ Real-time FPS and detection counts
- ✅ Servo position display
- ✅ Works from any device on network

### 2. Headless Mode (SSH-Friendly)
```bash
# Face detection with snapshots
python vision_system_headless.py --mode face --duration 30

# Record video
python vision_system_headless.py --mode gesture --duration 30 --save-video
```

### 3. Desktop Mode (Direct HDMI)
```bash
python vision_system_demo.py
```
(Requires display connected)

---

## 🎯 Use Cases

### Scenario 1: Testing Vision Features
1. Run: `./launch_vision.sh`
2. Click "🌐 Web Viewer"
3. Open browser to http://raspberrypi:5000
4. Click mode buttons to switch between features
5. See live results!

### Scenario 2: Recording Demo Video
1. Run: `./launch_vision.sh`
2. Set duration (e.g., 30 seconds)
3. Click "● Record Video"
4. Select mode (Face/Gesture/3D Object)
5. Video saved to `vision_*.mp4`

### Scenario 3: SSH Remote Testing
1. Run: `./launch_vision.sh`
2. Click headless mode button
3. Watch console output
4. Frames saved to `vision_frame_*.jpg`

---

## 📋 All Applications

| Application | Purpose | Access Method |
|-------------|---------|---------------|
| `vision_control_center.py` | 🎮 Main GUI launcher | Double-click or `./launch_vision.sh` |
| `vision_web_viewer.py` | 🌐 Web-based viewer | Browser: http://raspberrypi:5000 |
| `vision_system_headless.py` | 💻 SSH-friendly mode | Command line |
| `vision_system_demo.py` | 🖥️ Desktop mode | Requires display |
| `vision_tracking.py` | 🤖 Robot integration | Command line |

---

## 🌐 Web Viewer Features

**Live Controls:**
- Switch vision modes on-the-fly
- Start/stop video recording
- Reset camera servos
- View real-time statistics

**Access from:**
- Same Raspberry Pi: http://localhost:5000
- Other computer: http://raspberrypi.local:5000
- Mobile device: http://<raspberry-pi-ip>:5000

**Perfect for:**
- Remote monitoring
- Live demonstrations  
- Testing different modes
- Recording showcase videos

---

## 🎨 GUI Control Center Features

**Quick Launch Buttons:**
- Large "Web Viewer" button (recommended)
- Headless mode buttons for Face/Gesture/3D
- Video recording with duration control

**Live Monitoring:**
- Console output log
- Current status display
- Stop button for active processes
- Clear log functionality

**Designed for:**
- Easy access to all features
- No command-line needed
- Visual feedback
- One-click operation

---

## 💡 Tips

### For Best Results:
1. **Start with Web Viewer** - Most features in one interface
2. **Good Lighting** - Ensure adequate light for detection
3. **Camera Position** - Mount at appropriate height
4. **Network Access** - Connect devices to same network

### Performance:
- Web viewer: ~15-20 FPS
- Headless mode: ~9-10 FPS
- Single mode vs All: Use single for better performance

### Troubleshooting:
- **Can't access web viewer?** Check firewall, ensure port 5000 is open
- **No video stream?** Verify camera connected: `ls /dev/video*`
- **Low FPS?** Reduce resolution or use single mode instead of "All"
- **GUI won't start?** Ensure X11 display available or use SSH with X forwarding

---

## 📁 Files Summary

**Core Vision Modules:**
- `camera_controller.py` - Camera & servo control
- `face_recognition_module.py` - Face detection/recognition
- `gesture_recognition_module.py` - Hand gestures
- `object_3d_detection_module.py` - 3D object detection
- `vision_utils.py` - Helper utilities

**User Applications:**
- `vision_control_center.py` - **GUI launcher (use this!)**
- `vision_web_viewer.py` - Web interface
- `vision_system_headless.py` - SSH mode
- `vision_system_demo.py` - Desktop mode
- `vision_tracking.py` - Robot control
- `launch_vision.sh` - Quick launcher script

**Configuration:**
- `vision_config.json` - Settings
- `requirements.txt` - Dependencies

**Documentation:**
- `VISION_README.md` - Main documentation
- `RUNNING_HEADLESS.md` - SSH guide
- `VIDEO_RECORDING.md` - Recording guide
- `QUICK_START.md` - This file

---

## 🚀 Get Started NOW!

```bash
cd /home/pi/Raspbot-V2
./launch_vision.sh
```

Then click "🌐 Web Viewer" and open http://raspberrypi:5000 in your browser!

**That's it! You're ready to explore AI vision on your Raspbot V2!** 🎉
