#!/usr/bin/env python3
# coding: utf-8
"""
Camera Controller Module
Manages USB camera capture and pan/tilt servo control for Raspbot V2
"""

import cv2
import threading
import time
import numpy as np
from typing import Optional, Tuple
from Raspbot_Lib import Raspbot


class CameraController:
    """
    Camera controller with integrated servo control
    
    Features:
    - USB camera capture with configurable resolution and FPS
    - Thread-safe frame access
    - Pan/tilt servo control for camera tracking
    - Automatic reconnection on camera failure
    - Frame buffering
    """
    
    def __init__(self,
                 camera_id: int = 0,
                 width: int = 640,
                 height: int = 480,
                 fps: int = 30,
                 enable_servos: bool = True):
        """
        Initialize camera controller
        
        Args:
            camera_id: Camera device ID (usually 0 for /dev/video0)
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Target frames per second
            enable_servos: Enable servo control
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.enable_servos = enable_servos
        
        # Camera capture
        self.cap = None
        self.is_opened = False
        
        # Frame storage
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # Capture thread
        self.capture_thread = None
        self.running = False
        
        # Robot control for servos
        self.robot = None
        if enable_servos:
            try:
                self.robot = Raspbot()
                # Initialize servos to center position
                self.reset_servos()
            except Exception as e:
                print(f"Warning: Failed to initialize robot control: {e}")
                self.enable_servos = False
        
        # Servo positions
        self.pan_angle = 90  # Center position
        self.tilt_angle = 55  # Center position
        
        # Statistics
        self.frame_count = 0
        self.dropped_frames = 0
    
    def open(self) -> bool:
        """
        Open camera device
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify actual settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            print(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_opened = True
            return True
            
        except Exception as e:
            print(f"Error opening camera: {e}")
            return False
    
    def close(self):
        """Close camera and cleanup resources"""
        self.stop_capture()
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        self.is_opened = False
        print("Camera closed")
    
    def start_capture(self):
        """Start background frame capture thread"""
        if not self.is_opened:
            if not self.open():
                return False
        
        if self.running:
            print("Capture already running")
            return True
        
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print("Frame capture started")
        return True
    
    def stop_capture(self):
        """Stop background frame capture thread"""
        if not self.running:
            return
        
        self.running = False
        
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=2.0)
            self.capture_thread = None
        
        print("Frame capture stopped")
    
    def _capture_loop(self):
        """Background thread for continuous frame capture"""
        while self.running:
            try:
                ret, frame = self.cap.read()
                
                if ret:
                    with self.frame_lock:
                        self.current_frame = frame
                        self.frame_count += 1
                else:
                    self.dropped_frames += 1
                    print(f"Warning: Failed to capture frame (dropped: {self.dropped_frames})")
                    
                    # Try to reconnect
                    if self.dropped_frames > 10:
                        print("Attempting to reconnect camera...")
                        self.cap.release()
                        time.sleep(1)
                        self.cap = cv2.VideoCapture(self.camera_id)
                        self.dropped_frames = 0
                
                # Small delay to prevent CPU spinning
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Get the current frame (thread-safe)
        
        Returns:
            Current frame or None if not available
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read frame in OpenCV style (for compatibility)
        
        Returns:
            Tuple of (success, frame)
        """
        frame = self.read_frame()
        return (frame is not None, frame)
    
    def set_servo_angles(self, pan: Optional[int] = None, tilt: Optional[int] = None):
        """
        Set servo angles for camera pan/tilt
        
        Args:
            pan: Pan angle (0-180, 90 is center), None to keep current
            tilt: Tilt angle (0-110, 55 is center), None to keep current
        """
        if not self.enable_servos or self.robot is None:
            return
        
        try:
            if pan is not None:
                pan = np.clip(int(pan), 0, 180)
                self.robot.Ctrl_Servo(1, pan)  # Servo 1 is pan
                self.pan_angle = pan
            
            if tilt is not None:
                tilt = np.clip(int(tilt), 0, 110)
                self.robot.Ctrl_Servo(2, tilt)  # Servo 2 is tilt
                self.tilt_angle = tilt
                
        except Exception as e:
            print(f"Error setting servo angles: {e}")
    
    def reset_servos(self):
        """Reset servos to center position"""
        self.set_servo_angles(pan=90, tilt=55)
        print("Servos reset to center position")
    
    def get_servo_angles(self) -> Tuple[int, int]:
        """
        Get current servo angles
        
        Returns:
            Tuple of (pan, tilt) angles
        """
        return self.pan_angle, self.tilt_angle
    
    def set_camera_property(self, property_id: int, value: float) -> bool:
        """
        Set camera property
        
        Args:
            property_id: OpenCV property ID (e.g., cv2.CAP_PROP_BRIGHTNESS)
            value: Property value
        
        Returns:
            True if successful
        """
        if self.cap is not None:
            return self.cap.set(property_id, value)
        return False
    
    def get_camera_property(self, property_id: int) -> float:
        """
        Get camera property
        
        Args:
            property_id: OpenCV property ID
        
        Returns:
            Property value
        """
        if self.cap is not None:
            return self.cap.get(property_id)
        return 0.0
    
    def get_stats(self) -> dict:
        """
        Get capture statistics
        
        Returns:
            Dictionary with frame count and dropped frames
        """
        return {
            'frame_count': self.frame_count,
            'dropped_frames': self.dropped_frames,
            'is_opened': self.is_opened,
            'is_running': self.running,
            'pan_angle': self.pan_angle,
            'tilt_angle': self.tilt_angle
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def main():
    """Test camera controller"""
    print("Camera Controller Test")
    print("Press 'q' to quit")
    print("Arrow keys: control servos")
    print("'r': reset servos")
    
    camera = CameraController(camera_id=0, width=640, height=480, enable_servos=True)
    
    if not camera.open():
        print("Failed to open camera")
        return
    
    camera.start_capture()
    
    try:
        while True:
            frame = camera.read_frame()
            
            if frame is not None:
                # Get servo angles
                pan, tilt = camera.get_servo_angles()
                
                # Display info
                cv2.putText(frame, f"Pan: {pan} Tilt: {tilt}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                stats = camera.get_stats()
                cv2.putText(frame, f"Frames: {stats['frame_count']}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Camera Test", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == 82:  # Up arrow
                pan, tilt = camera.get_servo_angles()
                camera.set_servo_angles(tilt=min(tilt + 5, 110))
            elif key == 84:  # Down arrow
                pan, tilt = camera.get_servo_angles()
                camera.set_servo_angles(tilt=max(tilt - 5, 0))
            elif key == 81:  # Left arrow
                pan, tilt = camera.get_servo_angles()
                camera.set_servo_angles(pan=min(pan + 5, 180))
            elif key == 83:  # Right arrow
                pan, tilt = camera.get_servo_angles()
                camera.set_servo_angles(pan=max(pan - 5, 0))
            elif key == ord('r'):
                camera.reset_servos()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
