#!/usr/bin/env python3
# coding: utf-8
"""
Vision System Demo
Unified demonstration of all vision capabilities
"""

import cv2
import argparse
from camera_controller import CameraController
from face_recognition_module import FaceRecognitionModule
from gesture_recognition_module import GestureRecognitionModule
from object_3d_detection_module import Object3DDetectionModule
from vision_utils import FPSCounter, add_overlay_text


class VisionSystemDemo:
    """
    Unified vision system demonstration
    
    Modes:
    - face: Face detection and recognition
    - gesture: Hand gesture recognition
    - 3d_object: 3D object detection
    - all: All features combined
    """
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """Initialize vision system"""
        
        # Initialize camera
        print("Initializing camera...")
        self.camera = CameraController(
            camera_id=camera_id,
            width=width,
            height=height,
            enable_servos=True
        )
        self.camera.start_capture()
        
        # Initialize vision modules
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
            object_type='Cup',  # Use correct model name format
            enable_tracking=True
        )
        
        # FPS counter
        self.fps_counter = FPSCounter()
        
        # Mode states
        self.mode = 'face'
        self.modes = ['face', 'gesture', '3d_object', 'all']
        
        print("Vision System initialized successfully!")
    
    def run_face_mode(self, frame):
        """Run face detection and recognition"""
        self.face_module.process_frame(frame, recognize=True, track=True)
        
        info = [
            "MODE: Face Recognition",
            f"Faces detected: {len(self.face_module.last_detections)}",
            f"Database: {len(self.face_module.face_database)} faces",
            "",
            "Press 'a' to add face to database"
        ]
        
        return frame, info
    
    def run_gesture_mode(self, frame):
        """Run gesture recognition"""
        self.gesture_module.process_frame(frame, track=True)
        
        info = [
            "MODE: Gesture Recognition",
            f"Hands detected: {len(self.gesture_module.last_detections)}"
        ]
        
        # Add gesture info
        for i, hand in enumerate(self.gesture_module.last_detections):
            info.append(f"Hand {i+1}: {hand['gesture']}")
        
        return frame, info
    
    def run_3d_object_mode(self, frame):
        """Run 3D object detection"""
        self.object_3d_module.process_frame(frame, track=True)
        
        info = [
            "MODE: 3D Object Detection",
            f"Object type: {self.object_3d_module.OBJECT_TYPES[self.object_3d_module.object_type_key]}",
            f"Detected: {len(self.object_3d_module.last_detections)}",
            "",
            "Press 1-4 to change object type:",
            "1=Shoe, 2=Chair, 3=Cup, 4=Camera"
        ]
        
        return frame, info
    
    def run_all_mode(self, frame):
        """Run all detection modes simultaneously"""
        # Disable tracking for individual modules to avoid conflicts
        self.face_module.process_frame(frame, recognize=True, track=False)
        self.gesture_module.process_frame(frame, track=False)
        self.object_3d_module.process_frame(frame, track=False)
        
        info = [
            "MODE: All Features",
            f"Faces: {len(self.face_module.last_detections)}",
            f"Hands: {len(self.gesture_module.last_detections)}",
            f"3D Objects: {len(self.object_3d_module.last_detections)}"
        ]
        
        return frame, info
    
    def run(self):
        """Main demonstration loop"""
        print("\n" + "="*50)
        print("Vision System Demo")
        print("="*50)
        print("\nControls:")
        print("  'q' - Quit")
        print("  'm' - Switch mode (face/gesture/3d_object/all)")
        print("  'r' - Reset camera servos")
        print("  'a' - Add face to database (face mode)")
        print("  '1-4' - Change object type (3d_object mode)")
        print("  't' - Test camera")
        print("="*50 + "\n")
        
        try:
            while True:
                # Read frame
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    continue
                
                # Process based on mode
                if self.mode == 'face':
                    frame, info = self.run_face_mode(frame)
                elif self.mode == 'gesture':
                    frame, info = self.run_gesture_mode(frame)
                elif self.mode == '3d_object':
                    frame, info = self.run_3d_object_mode(frame)
                elif self.mode == 'all':
                    frame, info = self.run_all_mode(frame)
                
                # Display FPS
                fps = self.fps_counter.update()
                self.fps_counter.draw_fps(frame, fps)
                
                # Display info
                add_overlay_text(frame, info, position=(10, 60), font_scale=0.5, line_spacing=25)
                
                # Display frame
                cv2.imshow("Vision System Demo", frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('m'):
                    # Switch mode
                    current_idx = self.modes.index(self.mode)
                    self.mode = self.modes[(current_idx + 1) % len(self.modes)]
                    print(f"Switched to mode: {self.mode}")
                    self.camera.reset_servos()
                elif key == ord('r'):
                    self.camera.reset_servos()
                    print("Camera servos reset")
                elif key == ord('a') and self.mode == 'face':
                    # Add face to database
                    if len(self.face_module.last_detections) > 0:
                        print("\nEnter name for this face: ", end='', flush=True)
                        name = input()
                        face = self.face_module.last_detections[self.face_module.tracked_face_idx]
                        self.face_module.add_face(frame, face['bbox'], name)
                elif key == ord('1') and self.mode == '3d_object':
                    self.object_3d_module.change_object_type('SHOE')
                elif key == ord('2') and self.mode == '3d_object':
                    self.object_3d_module.change_object_type('CHAIR')
                elif key == ord('3') and self.mode == '3d_object':
                    self.object_3d_module.change_object_type('CUP')
                elif key == ord('4') and self.mode == '3d_object':
                    self.object_3d_module.change_object_type('CAMERA')
                elif key == ord('t'):
                    self.test_camera()
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def test_camera(self):
        """Test camera connection"""
        print("\nCamera Test:")
        stats = self.camera.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        self.face_module.close()
        self.gesture_module.close()
        self.object_3d_module.close()
        self.camera.close()
        cv2.destroyAllWindows()
        print("Cleanup complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Vision System Demo for Raspbot V2")
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID')
    parser.add_argument('--width', type=int, default=640, help='Frame width')
    parser.add_argument('--height', type=int, default=480, help='Frame height')
    parser.add_argument('--mode', type=str, default='face', 
                       choices=['face', 'gesture', '3d_object', 'all'],
                       help='Initial mode')
    parser.add_argument('--test-camera', action='store_true', help='Test camera and exit')
    
    args = parser.parse_args()
    
    # Test camera if requested
    if args.test_camera:
        print("Testing camera...")
        cam = CameraController(camera_id=args.camera, width=args.width, height=args.height)
        if cam.open():
            print("✓ Camera opened successfully")
            cam.start_capture()
            
            ret, frame = cam.read()
            if ret and frame is not None:
                print(f"✓ Frame captured: {frame.shape}")
                cv2.imshow("Camera Test", frame)
                cv2.waitKey(2000)
            else:
                print("✗ Failed to capture frame")
            
            cam.close()
            cv2.destroyAllWindows()
        else:
            print("✗ Failed to open camera")
        return
    
    # Run demo
    demo = VisionSystemDemo(camera_id=args.camera, width=args.width, height=args.height)
    demo.mode = args.mode
    demo.run()


if __name__ == "__main__":
    main()
