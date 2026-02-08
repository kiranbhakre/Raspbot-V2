#!/usr/bin/env python3
# coding: utf-8
"""
Face Recognition Module
Provides face detection, recognition, and tracking capabilities using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict
from camera_controller import CameraController
from vision_utils import ServoTracker, draw_bounding_box, calculate_center, FPSCounter


class FaceRecognitionModule:
    """
    Face detection and recognition using MediaPipe Face Detection
    
    Features:
    - Real-time face detection
    - Face encoding and recognition
    - Face database management
    - Camera tracking for detected faces
    - Multiple face detection
    """
    
    def __init__(self,
                 camera: Optional[CameraController] = None,
                 min_detection_confidence: float = 0.5,
                 enable_tracking: bool = True,
                 database_path: str = "face_database.json"):
        """
        Initialize face recognition module
        
        Args:
            camera: CameraController instance (optional)
            min_detection_confidence: Minimum confidence for face detection (0.0-1.0)
            enable_tracking: Enable servo tracking for detected faces
            database_path: Path to face database JSON file
        """
        self.camera = camera
        self.enable_tracking = enable_tracking
        self.database_path = database_path
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=min_detection_confidence,
            model_selection=0  # 0 for short-range (2m), 1 for full-range (5m)
        )
        
        # Face database (stored as face encodings)
        self.face_database = self.load_database()
        
        # Servo tracker for camera control
        self.servo_tracker = None
        if camera and enable_tracking:
            self.servo_tracker = ServoTracker(
                frame_width=camera.width,
                frame_height=camera.height
            )
        
        # Detection results
        self.last_detections = []
        self.tracked_face_idx = 0  # Index of face to track
        
        print("Face Recognition Module initialized")
    
    def load_database(self) -> Dict:
        """
        Load face database from JSON file
        
        Returns:
            Dictionary of face names and encodings
        """
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading face database: {e}")
        
        return {}
    
    def save_database(self):
        """Save face database to JSON file"""
        try:
            with open(self.database_path, 'w') as f:
                json.dump(self.face_database, f, indent=2)
            print(f"Face database saved to {self.database_path}")
        except Exception as e:
            print(f"Error saving face database: {e}")
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in frame
        
        Args:
            frame: Input image frame (BGR)
        
        Returns:
            List of detected faces with bounding boxes and confidence
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.face_detection.process(rgb_frame)
        
        detections = []
        
        if results.detections:
            h, w, _ = frame.shape
            
            for detection in results.detections:
                # Get bounding box
                bbox = detection.location_data.relative_bounding_box
                
                # Convert to pixel coordinates
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Ensure coordinates are within frame
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                # Get confidence score
                confidence = detection.score[0] if hasattr(detection, 'score') else 1.0
                
                detections.append({
                    'bbox': (x, y, width, height),
                    'confidence': confidence,
                    'center': calculate_center((x, y, width, height)),
                    'landmarks': self._extract_landmarks(detection, w, h)
                })
        
        self.last_detections = detections
        return detections
    
    def _extract_landmarks(self, detection, width: int, height: int) -> List[Tuple[int, int]]:
        """Extract facial landmarks from detection"""
        landmarks = []
        
        if hasattr(detection.location_data, 'relative_keypoints'):
            for keypoint in detection.location_data.relative_keypoints:
                x = int(keypoint.x * width)
                y = int(keypoint.y * height)
                landmarks.append((x, y))
        
        return landmarks
    
    def extract_face_encoding(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extract face encoding from face region
        
        Args:
            frame: Full image frame
            bbox: Bounding box (x, y, width, height)
        
        Returns:
            Face encoding as numpy array or None
        """
        x, y, w, h = bbox
        
        # Extract face region
        face_region = frame[y:y+h, x:x+w]
        
        if face_region.size == 0:
            return None
        
        # Resize to standard size for encoding
        face_resized = cv2.resize(face_region, (128, 128))
        
        # Simple encoding: use histogram of oriented gradients (HOG) features
        # In production, you could use face_recognition library or deep learning
        gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram as a simple encoding
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        hist = hist / (hist.sum() + 1e-6)  # Normalize
        
        return hist
    
    def add_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], name: str) -> bool:
        """
        Add a face to the database
        
        Args:
            frame: Image frame containing the face
            bbox: Bounding box of the face
            name: Name/label for the face
        
        Returns:
            True if successful
        """
        encoding = self.extract_face_encoding(frame, bbox)
        
        if encoding is None:
            print("Failed to extract face encoding")
            return False
        
        # Store encoding
        self.face_database[name] = encoding.tolist()
        self.save_database()
        
        print(f"Added face '{name}' to database")
        return True
    
    def recognize_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                      threshold: float = 0.6) -> Tuple[Optional[str], float]:
        """
        Recognize face by comparing with database
        
        Args:
            frame: Image frame containing the face
            bbox: Bounding box of the face
            threshold: Similarity threshold for recognition (0.0-1.0)
        
        Returns:
            Tuple of (name, confidence) or (None, 0.0) if no match
        """
        encoding = self.extract_face_encoding(frame, bbox)
        
        if encoding is None or len(self.face_database) == 0:
            return None, 0.0
        
        best_match = None
        best_similarity = 0.0
        
        # Compare with all faces in database
        for name, db_encoding in self.face_database.items():
            db_encoding = np.array(db_encoding)
            
            # Calculate similarity (using histogram correlation)
            similarity = cv2.compareHist(
                encoding.astype(np.float32),
                db_encoding.astype(np.float32),
                cv2.HISTCMP_CORREL
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = name
        
        # Check if similarity exceeds threshold
        if best_similarity >= threshold:
            return best_match, best_similarity
        
        return None, best_similarity
    
    def track_face(self, face_idx: int = 0):
        """
        Track a detected face with camera servos
        
        Args:
            face_idx: Index of face to track (0 for first detected face)
        """
        if not self.enable_tracking or self.camera is None or self.servo_tracker is None:
            return
        
        if face_idx >= len(self.last_detections):
            return
        
        face = self.last_detections[face_idx]
        cx, cy = face['center']
        
        # Calculate servo angles
        pan, tilt = self.servo_tracker.calculate_servo_angles(cx, cy)
        
        # Update camera servos
        self.camera.set_servo_angles(pan=pan, tilt=tilt)
    
    def draw_detections(self, frame: np.ndarray, 
                       recognize: bool = True,
                       draw_landmarks: bool = True):
        """
        Draw face detections on frame
        
        Args:
            frame: Image frame to draw on
            recognize: Attempt to recognize faces
            draw_landmarks: Draw facial landmarks
        """
        for i, face in enumerate(self.last_detections):
            bbox = face['bbox']
            confidence = face['confidence']
            
            # Recognize face if enabled
            label = f"Face {i+1}"
            color = (0, 255, 0)
            
            if recognize:
                name, recog_conf = self.recognize_face(frame, bbox)
                if name:
                    label = f"{name} ({recog_conf:.2f})"
                    color = (0, 255, 255)  # Yellow for recognized faces
                else:
                    label = f"Unknown ({confidence:.2f})"
                    color = (0, 0, 255)  # Red for unknown faces
            else:
                label = f"Face {i+1} ({confidence:.2f})"
            
            # Draw bounding box
            draw_bounding_box(frame, bbox, label, color)
            
            # Draw landmarks
            if draw_landmarks and face['landmarks']:
                for landmark in face['landmarks']:
                    cv2.circle(frame, landmark, 3, color, -1)
            
            # Mark tracked face
            if i == self.tracked_face_idx:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x-5, y-5), (x+w+5, y+h+5), (255, 0, 255), 3)
    
    def process_frame(self, frame: np.ndarray, 
                     recognize: bool = True,
                     track: bool = True,
                     draw: bool = True) -> np.ndarray:
        """
        Process frame for face detection and recognition
        
        Args:
            frame: Input frame
            recognize: Enable face recognition
            track: Enable face tracking with servos
            draw: Draw detections on frame
        
        Returns:
            Processed frame with annotations
        """
        # Detect faces
        self.detect_faces(frame)
        
        # Track face if enabled
        if track and len(self.last_detections) > 0:
            self.track_face(self.tracked_face_idx)
        
        # Draw detections
        if draw:
            self.draw_detections(frame, recognize=recognize)
        
        return frame
    
    def close(self):
        """Cleanup resources"""
        if self.face_detection:
            self.face_detection.close()


def main():
    """Test face recognition module"""
    print("Face Recognition Test")
    print("Commands:")
    print("  'q' - Quit")
    print("  'a' - Add current face to database")
    print("  'r' - Toggle recognition")
    print("  't' - Toggle tracking")
    print("  's' - Switch tracked face")
    print("  'c' - Clear database")
    
    # Initialize camera
    camera = CameraController(camera_id=0, width=640, height=480, enable_servos=True)
    camera.start_capture()
    
    # Initialize face recognition
    face_rec = FaceRecognitionModule(camera=camera, enable_tracking=True)
    
    # FPS counter
    fps_counter = FPSCounter()
    
    recognize_enabled = True
    tracking_enabled = True
    
    try:
        while True:
            # Read frame
            ret, frame = camera.read()
            if not ret or frame is None:
                continue
            
            # Process frame
            face_rec.process_frame(frame, recognize=recognize_enabled, track=tracking_enabled)
            
            # Display FPS
            fps = fps_counter.update()
            fps_counter.draw_fps(frame, fps)
            
            # Display info
            info = [
                f"Faces: {len(face_rec.last_detections)}",
                f"Database: {len(face_rec.face_database)} faces",
                f"Recognition: {'ON' if recognize_enabled else 'OFF'}",
                f"Tracking: {'ON' if tracking_enabled else 'OFF'}"
            ]
            y_pos = 60
            for text in info:
                cv2.putText(frame, text, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
            
            cv2.imshow("Face Recognition", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('a'):
                # Add face to database
                if len(face_rec.last_detections) > 0:
                    name = input("Enter name for this face: ")
                    face = face_rec.last_detections[face_rec.tracked_face_idx]
                    face_rec.add_face(frame, face['bbox'], name)
            elif key == ord('r'):
                recognize_enabled = not recognize_enabled
                print(f"Recognition: {'ON' if recognize_enabled else 'OFF'}")
            elif key == ord('t'):
                tracking_enabled = not tracking_enabled
                print(f"Tracking: {'ON' if tracking_enabled else 'OFF'}")
            elif key == ord('s'):
                # Switch to next face
                if len(face_rec.last_detections) > 0:
                    face_rec.tracked_face_idx = (face_rec.tracked_face_idx + 1) % len(face_rec.last_detections)
            elif key == ord('c'):
                # Clear database
                face_rec.face_database = {}
                face_rec.save_database()
                print("Database cleared")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        face_rec.close()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
