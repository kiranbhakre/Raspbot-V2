# Video Recording Examples

## Save Video Output

The headless mode now supports recording annotated video output!

### Basic Video Recording

Record 30 seconds of face tracking to video:
```bash
python vision_system_headless.py --mode face --duration 30 --save-video
```

This creates a video file like: `vision_face_20260202_201845.mp4`

### Custom Video Filename

Specify your own filename:
```bash
python vision_system_headless.py --mode face --duration 60 --save-video --output my_face_tracking.mp4
```

### Different Modes

**Record gesture recognition:**
```bash
python vision_system_headless.py --mode gesture --duration 30 --save-video
```

**Record 3D object detection:**
```bash
python vision_system_headless.py --mode 3d_object --duration 30 --save-video
```

### Long Recording

Record for 5 minutes:
```bash
python vision_system_headless.py --mode face --duration 300 --save-video
```

## Video vs Snapshot Mode

### Snapshot Mode (Default)
```bash
python vision_system_headless.py --mode face --duration 60
# Saves: vision_frame_5s.jpg, vision_frame_10s.jpg, etc.
```

### Video Mode
```bash
python vision_system_headless.py --mode face --duration 60 --save-video
# Saves: vision_face_TIMESTAMP.mp4 (continuous video)
```

## Video Features

✅ **Annotated output**: Includes all detection boxes, labels, FPS counter
✅ **Mode label**: Shows which mode is active
✅ **Servo tracking**: Video shows camera following faces/objects
✅ **Timestamped**: Auto-generated filenames with timestamp
✅ **MP4 format**: Compatible with most video players
✅ **~10 FPS**: Optimized for Raspberry Pi performance

## Download Video to Your Computer

After recording, transfer the video to your local machine:

```bash
# On your local computer:
scp pi@raspberrypi:~/Raspbot-V2/vision_face_*.mp4 ./
```

Then watch it with any video player (VLC, QuickTime, etc.)!

## Tips

1. **Better quality**: Use higher resolution
   ```bash
   python vision_system_headless.py --mode face --save-video --width 1280 --height 720
   ```

2. **Quick test**: Record just 10 seconds
   ```bash
   python vision_system_headless.py --mode face --duration 10 --save-video
   ```

3. **Stop early**: Press Ctrl+C to stop recording early (video will still be saved)

4. **Check file size**: Videos are ~1-2 MB per 10 seconds at 640x480

## Troubleshooting

**Video file is 0 bytes or corrupted:**
- The script automatically tries AVI format if MP4 fails
- Check console output for error messages

**Low FPS in video:**
- Expected on Raspberry Pi, video records at ~10 FPS
- Reduce resolution for better performance

**Can't play video:**
- Try VLC media player (supports most formats)
- Video might still be being written if script is running
