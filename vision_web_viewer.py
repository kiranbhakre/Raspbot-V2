#!/usr/bin/env python3
# coding: utf-8
"""
Vision Web Viewer
Live web-based camera viewer with vision processing
Stream annotated video to web browser over network
"""

import cv2
import time
import argparse
from flask import Flask, render_template, Response, request, jsonify
from camera_controller import CameraController
from face_recognition_module import FaceRecognitionModule
from gesture_recognition_module import GestureRecognitionModule
from object_3d_detection_module import Object3DDetectionModule
from vision_utils import FPSCounter
import threading


app = Flask(__name__)

# Custom JSON encoder to handle numpy types
import numpy as np
from flask.json.provider import DefaultJSONProvider

class NumpyJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super().default(obj)

app.json = NumpyJSONProvider(app)

# Global vision system instance
vision_system = None


class VisionWebStreamer:
    """Web-based vision system streamer"""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """Initialize vision web streamer"""
        
        print("Initializing camera...")
        self.camera = CameraController(
            camera_id=camera_id,
            width=width,
            height=height,
            enable_servos=True
        )
        self.camera.start_capture()
        
        print("Initializing vision modules...")
        self.face_module = FaceRecognitionModule(
            camera=self.camera,
            enable_tracking=True
        )
        
        self.gesture_module = GestureRecognitionModule(
            camera=self.camera,
            enable_tracking=True
        )
        
        self.object_3d_module = Object3DDetectionModule(
            camera=self.camera,
            object_type='Cup',
            enable_tracking=True
        )
        
        self.fps_counter = FPSCounter()
        
        # Current mode
        self.mode = 'face'
        self.modes = ['face', 'gesture', '3d_object', 'all', 'none']
        
        # Video recording
        self.recording = False
        self.video_writer = None
        self.video_filename = None
        
        # Statistics
        self.frame_count = 0
        self.start_time = time.time()
        
        print("Vision Web Streamer initialized!")
    
    def generate_frames(self):
        """Generate frames for MJPEG stream"""
        
        while True:
            ret, frame = self.camera.read()
            if not ret or frame is None:
                continue
            
            self.frame_count += 1
            
            # Process based on current mode
            if self.mode == 'face':
                self.face_module.process_frame(frame, recognize=True, track=True, draw=True)
                
            elif self.mode == 'gesture':
                self.gesture_module.process_frame(frame, track=True, draw=True)
                
            elif self.mode == '3d_object':
                self.object_3d_module.process_frame(frame, track=True, draw=True)
                
            elif self.mode == 'all':
                # Run all detectors (no tracking to avoid conflicts)
                self.face_module.process_frame(frame, recognize=True, track=False, draw=True)
                self.gesture_module.process_frame(frame, track=False, draw=True)
                self.object_3d_module.process_frame(frame, track=False, draw=True)
            
            # elif self.mode == 'none': just show raw camera
            
            # Add FPS counter
            fps = self.fps_counter.update()
            self.fps_counter.draw_fps(frame, fps)
            
            # Add mode label
            cv2.putText(frame, f"Mode: {self.mode.upper()}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add recording indicator
            if self.recording:
                cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                cv2.putText(frame, "REC", (frame.shape[1] - 70, 38),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Write to video file if recording
            if self.recording and self.video_writer is not None:
                self.video_writer.write(frame)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.03)  # ~30 FPS max
    
    def set_mode(self, mode: str):
        """Change vision mode"""
        if mode in self.modes:
            self.mode = mode
            print(f"Mode changed to: {mode}")
            return True
        return False
    
    def start_recording(self, filename: str = None):
        """Start recording video"""
        if self.recording:
            return False, "Already recording"
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"vision_web_{self.mode}_{timestamp}.mp4"
        
        self.video_filename = filename
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            filename,
            fourcc,
            15.0,  # FPS
            (self.camera.width, self.camera.height)
        )
        
        if self.video_writer.isOpened():
            self.recording = True
            print(f"Started recording to: {filename}")
            return True, f"Recording to {filename}"
        else:
            print("Failed to start recording")
            return False, "Failed to initialize video writer"
    
    def stop_recording(self):
        """Stop recording video"""
        if not self.recording:
            return False, "Not recording"
        
        self.recording = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        
        filename = self.video_filename
        self.video_filename = None
        
        print(f"Recording stopped: {filename}")
        return True, f"Video saved: {filename}"
    
    def get_status(self):
        """Get current status"""
        pan, tilt = self.camera.get_servo_angles()
        
        return {
            'mode': self.mode,
            'recording': self.recording,
            'video_filename': self.video_filename,
            'fps': float(self.fps_counter.get_fps()),
            'frame_count': int(self.frame_count),
            'uptime': int(time.time() - self.start_time),
            'servo_pan': int(pan),
            'servo_tilt': int(tilt),
            'detections': {
                'faces': int(len(self.face_module.last_detections)),
                'hands': int(len(self.gesture_module.last_detections)),
                'objects_3d': int(len(self.object_3d_module.last_detections))
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.recording:
            self.stop_recording()
        
        self.face_module.close()
        self.gesture_module.close()
        self.object_3d_module.close()
        self.camera.close()


# Flask routes

@app.route('/')
def index():
    """Main page"""
    return render_template('vision_viewer.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(vision_system.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Change vision mode"""
    data = request.json
    mode = data.get('mode')
    
    if vision_system.set_mode(mode):
        return jsonify({'success': True, 'mode': mode})
    else:
        return jsonify({'success': False, 'error': 'Invalid mode'}), 400


@app.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start recording"""
    success, message = vision_system.start_recording()
    return jsonify({'success': success, 'message': message})


@app.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop recording"""
    success, message = vision_system.stop_recording()
    return jsonify({'success': success, 'message': message})


@app.route('/api/servo/reset', methods=['POST'])
def reset_servo():
    """Reset servo positions"""
    vision_system.camera.reset_servos()
    return jsonify({'success': True})


@app.route('/api/status')
def get_status():
    """Get current status"""
    return jsonify(vision_system.get_status())


@app.route('/api/face/add', methods=['POST'])
def add_face():
    """Add a face to the database with a name"""
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': 'Name is required'}), 400
    
    # Get current frame and detections
    ret, frame = vision_system.camera.read()
    if not ret or frame is None:
        return jsonify({'success': False, 'error': 'Failed to capture frame'}), 500
    
    # Detect faces in current frame
    faces = vision_system.face_module.detect_faces(frame)
    
    if len(faces) == 0:
        return jsonify({'success': False, 'error': 'No face detected in frame'}), 400
    
    # Use the first detected face
    face = faces[0]
    bbox = face['bbox']
    
    # Add face to database
    face_id = vision_system.face_module.add_face(frame, bbox, name)
    
    if face_id:
        return jsonify({
            'success': True,
            'message': f'Face added for {name}',
            'face_id': face_id
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to add face'}), 500


def main():
    """Main entry point"""
    global vision_system
    
    parser = argparse.ArgumentParser(description="Vision Web Viewer for Raspbot V2")
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID')
    parser.add_argument('--width', type=int, default=640, help='Frame width')
    parser.add_argument('--height', type=int, default=480, help='Frame height')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    
    args = parser.parse_args()
    
    # Initialize vision system
    vision_system = VisionWebStreamer(
        camera_id=args.camera,
        width=args.width,
        height=args.height
    )
    
    print("\n" + "="*60)
    print("Vision Web Viewer Started!")
    print("="*60)
    print(f"\n🌐 Open in your browser:")
    print(f"   http://raspberrypi:{args.port}")
    print(f"   http://raspberrypi.local:{args.port}")
    print(f"   http://localhost:{args.port}  (on Raspberry Pi)")
    print("\n📱 From another device on the network:")
    print(f"   http://<raspberry-pi-ip>:{args.port}")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop\n")
    
    try:
        # Run Flask app
        app.run(host=args.host, port=args.port, threaded=True, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        vision_system.cleanup()


if __name__ == "__main__":
    main()
