#!/usr/bin/env python3
# coding: utf-8
"""
Vision System Headless Mode
Run vision system without display (for SSH/remote access)
Saves frames to files and prints detection info to console
"""

import cv2
import time
import argparse
from camera_controller import CameraController
from face_recognition_module import FaceRecognitionModule
from gesture_recognition_module import GestureRecognitionModule
from object_3d_detection_module import Object3DDetectionModule
from vision_utils import FPSCounter


class VisionSystemHeadless:
    """Vision system for headless operation (no display)"""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """Initialize vision system"""
        
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
        self.mode = 'face'
        self.frame_count = 0
        self.video_writer = None
        
        print("Vision System initialized!")
    
    def run(self, duration: int = 60, save_interval: int = 5, save_video: bool = False, video_filename: str = None):
        """
        Run headless vision system
        
        Args:
            duration: How long to run (seconds)
            save_interval: Save frame every N seconds (ignored if save_video=True)
            save_video: Save output as video file instead of snapshot images
            video_filename: Output video filename (auto-generated if None)
        """
        print(f"\nRunning in {self.mode} mode for {duration} seconds...")
        
        # Setup video writer if requested
        if save_video:
            if video_filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                video_filename = f"vision_{self.mode}_{timestamp}.mp4"
            
            # Try H264 codec first (better compression), fall back to MJPEG
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                video_filename,
                fourcc,
                10.0,  # FPS for video file
                (self.camera.width, self.camera.height)
            )
            
            if self.video_writer.isOpened():
                print(f"📹 Recording video to: {video_filename}")
            else:
                print(f"⚠️  Failed to open video writer, trying AVI format...")
                video_filename = video_filename.replace('.mp4', '.avi')
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                self.video_writer = cv2.VideoWriter(
                    video_filename,
                    fourcc,
                    10.0,
                    (self.camera.width, self.camera.height)
                )
                if self.video_writer.isOpened():
                    print(f"📹 Recording video to: {video_filename}")
                else:
                    print("❌ Failed to initialize video writer")
                    self.video_writer = None
                    save_video = False
        
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        last_save = 0
        last_print = 0
        
        try:
            while (time.time() - start_time) < duration:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    continue
                
                self.frame_count += 1
                
                # Process based on mode
                if self.mode == 'face':
                    self.face_module.process_frame(frame, recognize=True, track=True, draw=True)
                    detections = self.face_module.last_detections
                    
                    # Print detections every 2 seconds to avoid spam
                    if detections and (time.time() - last_print) >= 2.0:
                        print(f"[Face] Detected {len(detections)} face(s)")
                        for i, face in enumerate(detections):
                            print(f"  Face {i+1}: confidence={face['confidence']:.2f}, center={face['center']}")
                        last_print = time.time()
                
                elif self.mode == 'gesture':
                    self.gesture_module.process_frame(frame, track=True, draw=True)
                    detections = self.gesture_module.last_detections
                    
                    if detections and (time.time() - last_print) >= 2.0:
                        print(f"[Gesture] Detected {len(detections)} hand(s)")
                        for i, hand in enumerate(detections):
                            print(f"  Hand {i+1}: {hand['gesture']} ({hand['handedness']})")
                        last_print = time.time()
                
                elif self.mode == '3d_object':
                    self.object_3d_module.process_frame(frame, track=True, draw=True)
                    detections = self.object_3d_module.last_detections
                    
                    if detections and (time.time() - last_print) >= 2.0:
                        print(f"[3D Object] Detected {len(detections)} object(s)")
                        for i, obj in enumerate(detections):
                            print(f"  Object {i+1}: {obj['object_type']}, depth={obj['estimated_depth']:.1f}")
                        last_print = time.time()
                
                # Calculate FPS and add to frame
                fps = self.fps_counter.update()
                self.fps_counter.draw_fps(frame, fps)
                
                # Add mode label to frame
                cv2.putText(frame, f"Mode: {self.mode.upper()}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Write to video file
                if save_video and self.video_writer is not None:
                    self.video_writer.write(frame)
                
                # Save snapshot frames periodically (if not recording video)
                elif not save_video:
                    elapsed = time.time() - start_time
                    if elapsed - last_save >= save_interval:
                        filename = f"vision_frame_{int(elapsed)}s.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"\n[SAVED] Frame saved to {filename} (FPS: {fps:.1f})")
                        
                        # Print servo positions
                        pan, tilt = self.camera.get_servo_angles()
                        print(f"[SERVO] Pan: {pan}°, Tilt: {tilt}°\n")
                        
                        last_save = elapsed
                
                time.sleep(0.05)  # Reduce CPU usage
            
            # Print final statistics
            print(f"\n{'='*50}")
            print(f"Session complete!")
            print(f"Total frames processed: {self.frame_count}")
            print(f"Average FPS: {fps:.1f}")
            if save_video and self.video_writer is not None:
                print(f"Video saved to: {video_filename}")
            print(f"{'='*50}\n")
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            if save_video and self.video_writer is not None:
                print(f"Video saved to: {video_filename}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        if self.video_writer is not None:
            self.video_writer.release()
            print("Video writer released")
        self.face_module.close()
        self.gesture_module.close()
        self.object_3d_module.close()
        self.camera.close()
        print("Done!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Headless Vision System for Raspbot V2")
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID')
    parser.add_argument('--width', type=int, default=640, help='Frame width')
    parser.add_argument('--height', type=int, default=480, help='Frame height')
    parser.add_argument('--mode', type=str, default='face',
                       choices=['face', 'gesture', '3d_object'],
                       help='Vision mode')
    parser.add_argument('--duration', type=int, default=60, help='Run duration in seconds')
    parser.add_argument('--save-interval', type=int, default=5, 
                       help='Save frame every N seconds (only used if --save-video is not set)')
    parser.add_argument('--save-video', action='store_true',
                       help='Save output as video file instead of snapshot images')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video filename (only used with --save-video)')
    
    args = parser.parse_args()
    
    system = VisionSystemHeadless(camera_id=args.camera, width=args.width, height=args.height)
    system.mode = args.mode
    system.run(
        duration=args.duration, 
        save_interval=args.save_interval,
        save_video=args.save_video,
        video_filename=args.output
    )


if __name__ == "__main__":
    main()
