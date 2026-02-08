#!/usr/bin/env python3
# coding: utf-8
"""
Vision Tracking Integration
Integrates vision modules with robot movement and control
"""

import time
from typing import Optional
from camera_controller import CameraController
from face_recognition_module import FaceRecognitionModule
from gesture_recognition_module import GestureRecognitionModule
from Raspbot_Lib import Raspbot


class VisionTracker:
    """
    Integrates vision detection with robot movement
    
    Features:
    - Face following (robot follows detected face)
    - Gesture commands (control robot with hand gestures)
    - Obstacle avoidance using object detection
    """
    
    def __init__(self, camera: CameraController):
        """Initialize vision tracker"""
        self.camera = camera
        self.robot = Raspbot()
        
        # Initialize vision modules
        self.face_module = FaceRecognitionModule(camera=camera, enable_tracking=False)
        self.gesture_module = GestureRecognitionModule(camera=camera, enable_tracking=False)
        
        # Movement parameters
        self.base_speed = 100
        self.turn_speed = 80
        
        # Control state
        self.is_running = True
        self.mode = 'idle'  # idle, face_following, gesture_control
        
        print("Vision Tracker initialized")
    
    def stop_motors(self):
        """Stop all motors"""
        self.robot.Ctrl_Car(0, 0, 0)  # L1
        self.robot.Ctrl_Car(1, 0, 0)  # L2
        self.robot.Ctrl_Car(2, 0, 0)  # R1
        self.robot.Ctrl_Car(3, 0, 0)  # R2
    
    def move_forward(self, speed: int = None):
        """Move robot forward"""
        if speed is None:
            speed = self.base_speed
        
        self.robot.Ctrl_Car(0, 0, speed)  # L1 forward
        self.robot.Ctrl_Car(1, 0, speed)  # L2 forward
        self.robot.Ctrl_Car(2, 0, speed)  # R1 forward
        self.robot.Ctrl_Car(3, 0, speed)  # R2 forward
    
    def move_backward(self, speed: int = None):
        """Move robot backward"""
        if speed is None:
            speed = self.base_speed
        
        self.robot.Ctrl_Car(0, 1, speed)  # L1 backward
        self.robot.Ctrl_Car(1, 1, speed)  # L2 backward
        self.robot.Ctrl_Car(2, 1, speed)  # R1 backward
        self.robot.Ctrl_Car(3, 1, speed)  # R2 backward
    
    def turn_left(self, speed: int = None):
        """Turn robot left"""
        if speed is None:
            speed = self.turn_speed
        
        self.robot.Ctrl_Car(0, 1, speed)  # L1 backward
        self.robot.Ctrl_Car(1, 1, speed)  # L2 backward
        self.robot.Ctrl_Car(2, 0, speed)  # R1 forward
        self.robot.Ctrl_Car(3, 0, speed)  # R2 forward
    
    def turn_right(self, speed: int = None):
        """Turn robot right"""
        if speed is None:
            speed = self.turn_speed
        
        self.robot.Ctrl_Car(0, 0, speed)  # L1 forward
        self.robot.Ctrl_Car(1, 0, speed)  # L2 forward
        self.robot.Ctrl_Car(2, 1, speed)  # R1 backward
        self.robot.Ctrl_Car(3, 1, speed)  # R2 backward
    
    def face_following_mode(self, frame):
        """
        Follow detected faces
        
        Robot turns to keep face centered and maintains distance
        """
        # Detect faces
        faces = self.face_module.detect_faces(frame)
        
        if len(faces) == 0:
            # No face detected, stop
            self.stop_motors()
            return
        
        # Track first face
        face = faces[0]
        cx, cy = face['center']
        bbox = face['bbox']
        
        # Get frame dimensions
        frame_width = self.camera.width
        frame_center_x = frame_width // 2
        
        # Calculate horizontal offset
        offset_x = cx - frame_center_x
        
        # Dead zone (don't move if face is roughly centered)
        dead_zone = frame_width * 0.15
        
        if abs(offset_x) < dead_zone:
            # Face is centered, check distance
            bbox_width = bbox[2]
            
            # Target width (face should fill ~30% of frame)
            target_width = frame_width * 0.3
            
            if bbox_width < target_width * 0.8:
                # Too far, move forward
                self.move_forward(speed=80)
            elif bbox_width > target_width * 1.2:
                # Too close, move backward
                self.move_backward(speed=80)
            else:
                # Good distance, stop
                self.stop_motors()
        else:
            # Turn to center face
            if offset_x < 0:
                # Face is on left, turn left
                self.turn_left()
            else:
                # Face is on right, turn right
                self.turn_right()
    
    def gesture_control_mode(self, frame):
        """
        Control robot with hand gestures
        
        Gestures:
        - OPEN_PALM: Stop
        - THUMBS_UP: Move forward
        - THUMBS_DOWN: Move backward
        - POINTING (left/right): Turn left/right
        - PEACE: Special action (spin)
        - FIST: Stop
        """
        # Detect gestures
        hands = self.gesture_module.detect_hands(frame)
        
        if len(hands) == 0:
            # No gesture, maintain last command for a moment
            return
        
        # Get first hand gesture
        gesture = hands[0]['gesture']
        handedness = hands[0]['handedness']
        
        print(f"Gesture: {gesture}")
        
        # Execute command based on gesture
        if gesture == "OPEN_PALM" or gesture == "FIST":
            self.stop_motors()
        
        elif gesture == "THUMBS_UP":
            self.move_forward()
        
        elif gesture == "THUMBS_DOWN":
            self.move_backward()
        
        elif gesture == "POINTING":
            # Determine direction from hand position
            cx = hands[0]['center'][0]
            if cx < self.camera.width // 2:
                self.turn_left()
            else:
                self.turn_right()
        
        elif gesture == "PEACE":
            # Special action: spin
            self.turn_right(speed=100)
            time.sleep(1)
            self.stop_motors()
        
        else:
            # Unknown gesture, stop
            self.stop_motors()
    
    def run_face_following(self):
        """Run face following mode"""
        print("Face Following Mode")
        print("Press Ctrl+C to stop")
        
        self.mode = 'face_following'
        
        try:
            while self.is_running:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    continue
                
                self.face_following_mode(frame)
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\nStopping...")
        
        finally:
            self.stop_motors()
    
    def run_gesture_control(self):
        """Run gesture control mode"""
        print("Gesture Control Mode")
        print("Press Ctrl+C to stop")
        print("\nGestures:")
        print("  OPEN_PALM / FIST: Stop")
        print("  THUMBS_UP: Forward")
        print("  THUMBS_DOWN: Backward")
        print("  POINTING: Turn (left/right based on hand position)")
        print("  PEACE: Spin")
        
        self.mode = 'gesture_control'
        
        try:
            while self.is_running:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    continue
                
                self.gesture_control_mode(frame)
                time.sleep(0.2)
        
        except KeyboardInterrupt:
            print("\nStopping...")
        
        finally:
            self.stop_motors()
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_motors()
        self.face_module.close()
        self.gesture_module.close()


def main():
    """Test vision tracking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vision Tracking for Raspbot V2")
    parser.add_argument('--mode', type=str, default='gesture',
                       choices=['face', 'gesture'],
                       help='Tracking mode')
    
    args = parser.parse_args()
    
    # Initialize camera
    camera = CameraController(camera_id=0, width=640, height=480, enable_servos=True)
    camera.start_capture()
    
    # Initialize tracker
    tracker = VisionTracker(camera)
    
    try:
        if args.mode == 'face':
            tracker.run_face_following()
        elif args.mode == 'gesture':
            tracker.run_gesture_control()
    
    finally:
        tracker.cleanup()
        camera.close()


if __name__ == "__main__":
    main()
