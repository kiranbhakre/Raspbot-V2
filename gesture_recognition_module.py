#!/usr/bin/env python3
# coding: utf-8
"""
Gesture Recognition Module
Hand gesture detection and recognition using MediaPipe Hands
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional, Dict, Callable
from camera_controller import CameraController
from vision_utils import ServoTracker, draw_landmarks, draw_connections, calculate_center, FPSCounter


class GestureRecognitionModule:
    """
    Hand gesture detection and recognition using MediaPipe Hands
    
    Recognizes gestures:
    - Open palm / Stop
    - Thumbs up / Thumbs down
    - Peace sign (victory)
    - Pointing (index finger)
    - Fist / Closed hand
    - OK sign
    """
    
    # Hand landmark indices (MediaPipe convention)
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20
    
    def __init__(self,
                 camera: Optional[CameraController] = None,
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 enable_tracking: bool = True):
        """
        Initialize gesture recognition module
        
        Args:
            camera: CameraController instance (optional)
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
            enable_tracking: Enable servo tracking for detected hands
        """
        self.camera = camera
        self.enable_tracking = enable_tracking
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
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
        self.tracked_hand_idx = 0
        
        # Gesture callbacks
        self.gesture_callbacks: Dict[str, Callable] = {}
        
        print("Gesture Recognition Module initialized")
    
    def register_gesture_callback(self, gesture_name: str, callback: Callable):
        """
        Register a callback function for a specific gesture
        
        Args:
            gesture_name: Name of gesture (e.g., 'THUMBS_UP')
            callback: Function to call when gesture is detected
        """
        self.gesture_callbacks[gesture_name] = callback
    
    def detect_hands(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect hands in frame
        
        Args:
            frame: Input image frame (BGR)
        
        Returns:
            List of detected hands with landmarks and gestures
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect hands
        results = self.hands.process(rgb_frame)
        
        detections = []
        
        if results.multi_hand_landmarks:
            h, w, _ = frame.shape
            
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Extract landmark coordinates
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z  # Depth (relative)
                    landmarks.append((x, y, z))
                
                # Get hand label (left/right)
                handedness = "Unknown"
                if results.multi_handedness and idx < len(results.multi_handedness):
                    handedness = results.multi_handedness[idx].classification[0].label
                
                # Calculate bounding box
                x_coords = [lm[0] for lm in landmarks]
                y_coords = [lm[1] for lm in landmarks]
                
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
                center = calculate_center(bbox)
                
                # Recognize gesture
                gesture = self.recognize_gesture(landmarks)
                
                detections.append({
                    'landmarks': landmarks,
                    'bbox': bbox,
                    'center': center,
                    'handedness': handedness,
                    'gesture': gesture
                })
        
        self.last_detections = detections
        return detections
    
    def recognize_gesture(self, landmarks: List[Tuple[int, int, float]]) -> str:
        """
        Recognize hand gesture from landmarks
        
        Args:
            landmarks: List of hand landmarks with (x, y, z) coordinates
        
        Returns:
            Gesture name
        """
        # Extract fingertip and joint positions
        finger_tips = [
            self.THUMB_TIP,
            self.INDEX_FINGER_TIP,
            self.MIDDLE_FINGER_TIP,
            self.RING_FINGER_TIP,
            self.PINKY_TIP
        ]
        
        finger_pips = [
            self.THUMB_IP,
            self.INDEX_FINGER_PIP,
            self.MIDDLE_FINGER_PIP,
            self.RING_FINGER_PIP,
            self.PINKY_PIP
        ]
        
        # Count extended fingers
        extended_fingers = []
        
        for i, (tip, pip) in enumerate(zip(finger_tips, finger_pips)):
            if i == 0:  # Thumb (check x-axis for left/right)
                # Thumb is extended if tip is further from wrist than PIP
                wrist_x = landmarks[self.WRIST][0]
                tip_x = landmarks[tip][0]
                pip_x = landmarks[pip][0]
                
                # Calculate distance from wrist
                tip_dist = abs(tip_x - wrist_x)
                pip_dist = abs(pip_x - wrist_x)
                
                extended_fingers.append(tip_dist > pip_dist)
            else:  # Other fingers (check y-axis)
                # Finger is extended if tip is above PIP (lower y value)
                extended_fingers.append(landmarks[tip][1] < landmarks[pip][1])
        
        num_extended = sum(extended_fingers)
        
        # Recognize specific gestures
        
        # Fist (no fingers extended)
        if num_extended == 0:
            return "FIST"
        
        # Open palm (all fingers extended)
        if num_extended == 5:
            return "OPEN_PALM"
        
        # Thumbs up (only thumb extended)
        if extended_fingers == [True, False, False, False, False]:
            # Check if thumb is pointing up
            if landmarks[self.THUMB_TIP][1] < landmarks[self.THUMB_IP][1]:
                return "THUMBS_UP"
            else:
                return "THUMBS_DOWN"
        
        # Pointing (only index finger extended)
        if extended_fingers == [False, True, False, False, False]:
            return "POINTING"
        
        # Peace sign (index and middle fingers extended)
        if extended_fingers == [False, True, True, False, False]:
            return "PEACE"
        
        # OK sign (thumb and index forming circle, others extended)
        if extended_fingers == [False, False, True, True, True]:
            # Check if thumb and index are close
            thumb_tip = landmarks[self.THUMB_TIP]
            index_tip = landmarks[self.INDEX_FINGER_TIP]
            
            distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + 
                             (thumb_tip[1] - index_tip[1])**2)
            
            if distance < 40:  # Pixels
                return "OK_SIGN"
        
        # Three fingers
        if num_extended == 3:
            if extended_fingers[1] and extended_fingers[2] and extended_fingers[3]:
                return "THREE"
        
        # Four fingers
        if num_extended == 4:
            if not extended_fingers[0]:  # Thumb not extended
                return "FOUR"
        
        return "UNKNOWN"
    
    def track_hand(self, hand_idx: int = 0):
        """
        Track a detected hand with camera servos
        
        Args:
            hand_idx: Index of hand to track
        """
        if not self.enable_tracking or self.camera is None or self.servo_tracker is None:
            return
        
        if hand_idx >= len(self.last_detections):
            return
        
        hand = self.last_detections[hand_idx]
        cx, cy = hand['center']
        
        # Calculate servo angles
        pan, tilt = self.servo_tracker.calculate_servo_angles(cx, cy)
        
        # Update camera servos
        self.camera.set_servo_angles(pan=pan, tilt=tilt)
    
    def draw_detections(self, frame: np.ndarray, 
                       draw_skeleton: bool = True,
                       draw_bbox: bool = True):
        """
        Draw hand detections on frame
        
        Args:
            frame: Image frame to draw on
            draw_skeleton: Draw hand skeleton
            draw_bbox: Draw bounding box
        """
        for i, hand in enumerate(self.last_detections):
            landmarks = hand['landmarks']
            bbox = hand['bbox']
            gesture = hand['gesture']
            handedness = hand['handedness']
            
            # Draw skeleton
            if draw_skeleton:
                # Draw landmarks
                landmark_points = [(lm[0], lm[1]) for lm in landmarks]
                draw_landmarks(frame, landmark_points, color=(0, 255, 0), radius=5)
                
                # Draw connections
                connections = self.mp_hands.HAND_CONNECTIONS
                draw_connections(frame, landmark_points, connections, color=(255, 255, 255), thickness=2)
            
            # Draw bounding box
            if draw_bbox:
                x, y, w, h = bbox
                color = (0, 255, 255) if gesture != "UNKNOWN" else (0, 0, 255)
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label
                label = f"{handedness}: {gesture}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_w, label_h = label_size
                
                cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w, y), color, -1)
                cv2.putText(frame, label, (x, y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Mark tracked hand
            if i == self.tracked_hand_idx:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x-5, y-5), (x+w+5, y+h+5), (255, 0, 255), 3)
    
    def process_frame(self, frame: np.ndarray,
                     track: bool = True,
                     draw: bool = True,
                     trigger_callbacks: bool = True) -> np.ndarray:
        """
        Process frame for gesture recognition
        
        Args:
            frame: Input frame
            track: Enable hand tracking with servos
            draw: Draw detections on frame
            trigger_callbacks: Trigger gesture callbacks
        
        Returns:
            Processed frame with annotations
        """
        # Detect hands
        self.detect_hands(frame)
        
        # Track hand if enabled
        if track and len(self.last_detections) > 0:
            self.track_hand(self.tracked_hand_idx)
        
        # Trigger gesture callbacks
        if trigger_callbacks:
            for hand in self.last_detections:
                gesture = hand['gesture']
                if gesture in self.gesture_callbacks:
                    self.gesture_callbacks[gesture]()
        
        # Draw detections
        if draw:
            self.draw_detections(frame)
        
        return frame
    
    def close(self):
        """Cleanup resources"""
        if self.hands:
            self.hands.close()


def main():
    """Test gesture recognition module"""
    print("Gesture Recognition Test")
    print("Commands:")
    print("  'q' - Quit")
    print("  't' - Toggle tracking")
    print("  's' - Switch tracked hand")
    print("  'k' - Toggle skeleton drawing")
    
    # Initialize camera
    camera = CameraController(camera_id=0, width=640, height=480, enable_servos=True)
    camera.start_capture()
    
    # Initialize gesture recognition
    gesture_rec = GestureRecognitionModule(camera=camera, enable_tracking=True)
    
    # Register gesture callbacks
    def on_thumbs_up():
        print("👍 Thumbs up detected!")
    
    def on_peace():
        print("✌️ Peace sign detected!")
    
    def on_open_palm():
        print("✋ Open palm detected!")
    
    gesture_rec.register_gesture_callback("THUMBS_UP", on_thumbs_up)
    gesture_rec.register_gesture_callback("PEACE", on_peace)
    gesture_rec.register_gesture_callback("OPEN_PALM", on_open_palm)
    
    # FPS counter
    fps_counter = FPSCounter()
    
    tracking_enabled = True
    draw_skeleton = True
    
    try:
        while True:
            # Read frame
            ret, frame = camera.read()
            if not ret or frame is None:
                continue
            
            # Process frame
            gesture_rec.process_frame(frame, track=tracking_enabled, trigger_callbacks=False)
            
            # Display FPS
            fps = fps_counter.update()
            fps_counter.draw_fps(frame, fps)
            
            # Display info
            info = [
                f"Hands: {len(gesture_rec.last_detections)}",
                f"Tracking: {'ON' if tracking_enabled else 'OFF'}",
                f"Skeleton: {'ON' if draw_skeleton else 'OFF'}"
            ]
            
            # Add gesture info
            for i, hand in enumerate(gesture_rec.last_detections):
                info.append(f"Hand {i+1}: {hand['gesture']}")
            
            y_pos = 60
            for text in info:
                cv2.putText(frame, text, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
            
            cv2.imshow("Gesture Recognition", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('t'):
                tracking_enabled = not tracking_enabled
                print(f"Tracking: {'ON' if tracking_enabled else 'OFF'}")
            elif key == ord('s'):
                # Switch to next hand
                if len(gesture_rec.last_detections) > 0:
                    gesture_rec.tracked_hand_idx = (gesture_rec.tracked_hand_idx + 1) % len(gesture_rec.last_detections)
            elif key == ord('k'):
                draw_skeleton = not draw_skeleton
                print(f"Skeleton: {'ON' if draw_skeleton else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        gesture_rec.close()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
