#!/usr/bin/env python3
# coding: utf-8
"""
3D Object Detection Module
3D object detection and tracking using MediaPipe Objectron
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional, Dict
from camera_controller import CameraController
from vision_utils import ServoTracker, calculate_center, estimate_depth_from_bbox, FPSCounter


class Object3DDetectionModule:
    """
    3D object detection using MediaPipe Objectron
    
    Supported objects:
    - Shoe
    - Chair
    - Cup
    - Camera
    
    Features:
    - 3D bounding box detection
    - Object pose estimation
    - Depth/distance estimation
    - Camera tracking
    """
    
    # Object types supported by MediaPipe Objectron
    OBJECT_TYPES = {
        'SHOE': 'Shoe',
        'CHAIR': 'Chair',
        'CUP': 'Cup',
        'CAMERA': 'Camera'
    }
    
    # Valid model names for MediaPipe Objectron
    MODEL_NAMES = {
        'SHOE': 'Shoe',
        'CHAIR': 'Chair',
        'CUP': 'Cup',
        'CAMERA': 'Camera'
    }
    
    def __init__(self,
                 camera: Optional[CameraController] = None,
                 object_type: str = 'Cup',  # Default to 'Cup' (lowercase)
                 max_num_objects: int = 5,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 enable_tracking: bool = True):
        """
        Initialize 3D object detection module
        
        Args:
            camera: CameraController instance (optional)
            object_type: Type of object to detect ('Shoe', 'Chair', 'Cup', 'Camera')
            max_num_objects: Maximum number of objects to detect
            min_detection_confidence: Minimum confidence for object detection
            min_tracking_confidence: Minimum confidence for object tracking
            enable_tracking: Enable servo tracking for detected objects
        """
        self.camera = camera
        self.enable_tracking = enable_tracking
        
        # Normalize object type
        object_type_upper = object_type.upper()
        if object_type_upper in self.MODEL_NAMES:
            self.object_type_key = object_type_upper
            model_name = self.MODEL_NAMES[object_type_upper]
        else:
            print(f"Warning: Unknown object type '{object_type}'. Using 'Cup'")
            self.object_type_key = 'CUP'
            model_name = 'Cup'
        
        # Initialize MediaPipe Objectron
        self.mp_objectron = mp.solutions.objectron
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.objectron = self.mp_objectron.Objectron(
            static_image_mode=False,
            max_num_objects=max_num_objects,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_name=model_name  # Use the correct model name format
        )
        
        # Servo tracker for camera control
        self.servo_tracker = None
        if camera and enable_tracking:
            self.servo_tracker = ServoTracker(
                frame_width=camera.width,
                frame_height=camera.height
            )
        
        # Detection results
        self.last_detections = []
        self.tracked_object_idx = 0
        
        print(f"3D Object Detection Module initialized (detecting {self.OBJECT_TYPES[self.object_type_key]})")
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect 3D objects in frame
        
        Args:
            frame: Input image frame (BGR)
        
        Returns:
            List of detected objects with 3D landmarks and bounding boxes
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect objects
        results = self.objectron.process(rgb_frame)
        
        detections = []
        
        if results.detected_objects:
            h, w, _ = frame.shape
            
            for obj in results.detected_objects:
                # Extract 3D landmarks (9 points defining the 3D box)
                landmarks_3d = []
                for landmark in obj.landmarks_3d.landmark:
                    landmarks_3d.append((landmark.x, landmark.y, landmark.z))
                
                # Extract 2D landmarks (projected onto image)
                landmarks_2d = []
                for landmark in obj.landmarks_2d.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks_2d.append((x, y))
                
                # Calculate 2D bounding box from landmarks
                if landmarks_2d:
                    x_coords = [lm[0] for lm in landmarks_2d]
                    y_coords = [lm[1] for lm in landmarks_2d]
                    
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
                    center = calculate_center(bbox)
                    
                    # Estimate depth/distance
                    depth = estimate_depth_from_bbox(bbox[2])
                    
                    # Get rotation and translation (pose)
                    rotation = obj.rotation if hasattr(obj, 'rotation') else None
                    translation = obj.translation if hasattr(obj, 'translation') else None
                    
                    detections.append({
                        'object_type': self.OBJECT_TYPES[self.object_type_key],
                        'landmarks_2d': landmarks_2d,
                        'landmarks_3d': landmarks_3d,
                        'bbox': bbox,
                        'center': center,
                        'estimated_depth': depth,
                        'rotation': rotation,
                        'translation': translation
                    })
        
        self.last_detections = detections
        return detections
    
    def track_object(self, object_idx: int = 0):
        """
        Track a detected object with camera servos
        
        Args:
            object_idx: Index of object to track
        """
        if not self.enable_tracking or self.camera is None or self.servo_tracker is None:
            return
        
        if object_idx >= len(self.last_detections):
            return
        
        obj = self.last_detections[object_idx]
        cx, cy = obj['center']
        
        # Calculate servo angles
        pan, tilt = self.servo_tracker.calculate_servo_angles(cx, cy)
        
        # Update camera servos
        self.camera.set_servo_angles(pan=pan, tilt=tilt)
    
    def draw_3d_bbox(self, frame: np.ndarray, landmarks_2d: List[Tuple[int, int]]):
        """
        Draw 3D bounding box on frame
        
        Args:
            frame: Image frame to draw on
            landmarks_2d: List of 2D landmark points
        """
        # MediaPipe Objectron provides 9 landmarks defining a 3D box:
        # 0: center
        # 1-8: corners of the box
        
        if len(landmarks_2d) < 9:
            return
        
        # Define edges of the 3D box
        edges = [
            (1, 2), (2, 3), (3, 4), (4, 1),  # Bottom face
            (5, 6), (6, 7), (7, 8), (8, 5),  # Top face
            (1, 5), (2, 6), (3, 7), (4, 8)   # Vertical edges
        ]
        
        # Draw edges
        for edge in edges:
            start_idx, end_idx = edge
            if start_idx < len(landmarks_2d) and end_idx < len(landmarks_2d):
                start_point = landmarks_2d[start_idx]
                end_point = landmarks_2d[end_idx]
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)
        
        # Draw landmarks
        for i, point in enumerate(landmarks_2d):
            if i == 0:  # Center point
                cv2.circle(frame, point, 5, (255, 0, 0), -1)
            else:  # Corner points
                cv2.circle(frame, point, 4, (0, 255, 0), -1)
    
    def draw_detections(self, frame: np.ndarray,
                       draw_3d_box: bool = True,
                       draw_2d_bbox: bool = True,
                       show_depth: bool = True):
        """
        Draw object detections on frame
        
        Args:
            frame: Image frame to draw on
            draw_3d_box: Draw 3D bounding box
            draw_2d_bbox: Draw 2D bounding box
            show_depth: Show estimated depth
        """
        for i, obj in enumerate(self.last_detections):
            landmarks_2d = obj['landmarks_2d']
            bbox = obj['bbox']
            depth = obj['estimated_depth']
            obj_type = obj['object_type']
            
            # Draw 3D bounding box
            if draw_3d_box:
                self.draw_3d_bbox(frame, landmarks_2d)
            
            # Draw 2D bounding box
            if draw_2d_bbox:
                x, y, w, h = bbox
                color = (255, 255, 0)  # Cyan
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label
                label = obj_type
                if show_depth:
                    label += f" (D:{depth:.1f})"
                
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_w, label_h = label_size
                
                cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w, y), color, -1)
                cv2.putText(frame, label, (x, y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Mark tracked object
            if i == self.tracked_object_idx:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x-5, y-5), (x+w+5, y+h+5), (255, 0, 255), 3)
    
    def process_frame(self, frame: np.ndarray,
                     track: bool = True,
                     draw: bool = True) -> np.ndarray:
        """
        Process frame for 3D object detection
        
        Args:
            frame: Input frame
            track: Enable object tracking with servos
            draw: Draw detections on frame
        
        Returns:
            Processed frame with annotations
        """
        # Detect objects
        self.detect_objects(frame)
        
        # Track object if enabled
        if track and len(self.last_detections) > 0:
            self.track_object(self.tracked_object_idx)
        
        # Draw detections
        if draw:
            self.draw_detections(frame)
        
        return frame
    
    def change_object_type(self, object_type: str):
        """
        Change the type of object to detect
        
        Args:
            object_type: New object type ('Shoe', 'Chair', 'Cup', 'Camera' or 'SHOE', 'CHAIR', 'CUP', 'CAMERA')
        """
        object_type_upper = object_type.upper()
        
        if object_type_upper not in self.MODEL_NAMES:
            print(f"Error: Unknown object type '{object_type}'")
            print(f"Available types: {list(self.OBJECT_TYPES.keys())}")
            return
        
        self.object_type_key = object_type_upper
        model_name = self.MODEL_NAMES[object_type_upper]
        
        # Recreate objectron with new model
        self.objectron.close()
        self.objectron = self.mp_objectron.Objectron(
            static_image_mode=False,
            max_num_objects=5,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_name=model_name  # Use correct model name format
        )
        
        print(f"Switched to detecting: {self.OBJECT_TYPES[self.object_type_key]}")
    
    def close(self):
        """Cleanup resources"""
        if self.objectron:
            self.objectron.close()


def main():
    """Test 3D object detection module"""
    print("3D Object Detection Test")
    print("Commands:")
    print("  'q' - Quit")
    print("  't' - Toggle tracking")
    print("  's' - Switch tracked object")
    print("  '1' - Detect shoes")
    print("  '2' - Detect chairs")
    print("  '3' - Detect cups")
    print("  '4' - Detect cameras")
    print("  'b' - Toggle 2D bbox")
    print("  'd' - Toggle depth display")
    
    # Initialize camera
    camera = CameraController(camera_id=0, width=640, height=480, enable_servos=True)
    camera.start_capture()
    
    # Initialize 3D object detection
    object_3d = Object3DDetectionModule(camera=camera, object_type='Cup', enable_tracking=True)
    
    # FPS counter
    fps_counter = FPSCounter()
    
    tracking_enabled = True
    draw_2d_bbox = True
    show_depth = True
    
    try:
        while True:
            # Read frame
            ret, frame = camera.read()
            if not ret or frame is None:
                continue
            
            # Process frame
            object_3d.process_frame(frame, track=tracking_enabled)
            
            # Display FPS
            fps = fps_counter.update()
            fps_counter.draw_fps(frame, fps)
            
            # Display info
            info = [
                f"Object Type: {object_3d.OBJECT_TYPES[object_3d.object_type_key]}",
                f"Detected: {len(object_3d.last_detections)}",
                f"Tracking: {'ON' if tracking_enabled else 'OFF'}",
                f"2D BBox: {'ON' if draw_2d_bbox else 'OFF'}",
                f"Depth: {'ON' if show_depth else 'OFF'}"
            ]
            
            y_pos = 60
            for text in info:
                cv2.putText(frame, text, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
            
            cv2.imshow("3D Object Detection", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('t'):
                tracking_enabled = not tracking_enabled
                print(f"Tracking: {'ON' if tracking_enabled else 'OFF'}")
            elif key == ord('s'):
                # Switch to next object
                if len(object_3d.last_detections) > 0:
                    object_3d.tracked_object_idx = (object_3d.tracked_object_idx + 1) % len(object_3d.last_detections)
            elif key == ord('1'):
                object_3d.change_object_type('SHOE')
            elif key == ord('2'):
                object_3d.change_object_type('CHAIR')
            elif key == ord('3'):
                object_3d.change_object_type('CUP')
            elif key == ord('4'):
                object_3d.change_object_type('CAMERA')
            elif key == ord('b'):
                draw_2d_bbox = not draw_2d_bbox
                print(f"2D BBox: {'ON' if draw_2d_bbox else 'OFF'}")
            elif key == ord('d'):
                show_depth = not show_depth
                print(f"Depth: {'ON' if show_depth else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        object_3d.close()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
