#!/usr/bin/env python3
# coding: utf-8
"""
Vision Utilities Module
Provides helper functions for computer vision tasks including:
- Frame preprocessing
- FPS counting
- Coordinate transformations
- Annotation drawing
- Servo angle calculations for tracking
"""

import cv2
import numpy as np
import time
from typing import Tuple, List, Optional


class FPSCounter:
    """Calculate and display frames per second"""
    
    def __init__(self, buffer_size: int = 30):
        self.buffer_size = buffer_size
        self.buffer_size = buffer_size # This buffer_size is no longer directly used for FPS calculation in the new update logic
        self.frame_times = []
        self.last_time = time.time() # This is no longer directly used for FPS calculation in the new update logic
        self.fps = 0.0 # Initialize fps
    
    def update(self) -> float:
        """Update FPS counter and return current FPS"""
        current_time = time.time()
        self.frame_times.append(current_time)
        
        # Keep only last second of frame times
        cutoff_time = current_time - 1.0
        self.frame_times = [t for t in self.frame_times if t > cutoff_time]
        
        # Calculate FPS
        self.fps = float(len(self.frame_times))
        
        return self.fps
    
    def get_fps(self) -> float:
        """Get current FPS value"""
        return self.fps
    
    def draw_fps(self, frame: np.ndarray, fps: Optional[float] = None, position: Tuple[int, int] = (10, 30)):
        """Draw FPS on frame"""
        # Use the provided fps value or get the current one from the counter
        display_fps = fps if fps is not None else self.get_fps()
        cv2.putText(frame, f"FPS: {display_fps:.1f}", position, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


class ServoTracker:
    """Calculate servo angles for object tracking"""
    
    def __init__(self, frame_width: int, frame_height: int,
                 pan_range: Tuple[int, int] = (0, 180),
                 tilt_range: Tuple[int, int] = (0, 110),
                 pan_center: int = 90,
                 tilt_center: int = 55):
        """
        Initialize servo tracker
        
        Args:
            frame_width: Width of camera frame
            frame_height: Height of camera frame
            pan_range: Min and max angles for pan servo
            tilt_range: Min and max angles for tilt servo
            pan_center: Center position for pan servo
            tilt_center: Center position for tilt servo
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.pan_range = pan_range
        self.tilt_range = tilt_range
        self.pan_center = pan_center
        self.tilt_center = tilt_center
        
        # Current servo positions
        self.current_pan = pan_center
        self.current_tilt = tilt_center
        
        # Tracking parameters (adjusted for better face tracking)
        self.dead_zone = 0.15  # 15% dead zone in center (increased for stability)
        self.max_step = 8  # Maximum angle change per update (increased for faster response)
    
    def calculate_servo_angles(self, x: int, y: int, 
                               smooth: bool = True) -> Tuple[int, int]:
        """
        Calculate servo angles to center object at (x, y)
        
        Args:
            x: X coordinate of object in frame
            y: Y coordinate of object in frame
            smooth: Apply smoothing to servo movement
        
        Returns:
            Tuple of (pan_angle, tilt_angle)
        """
        # Normalize coordinates to [-1, 1]
        norm_x = (x - self.frame_width / 2) / (self.frame_width / 2)
        norm_y = (y - self.frame_height / 2) / (self.frame_height / 2)
        
        # Apply dead zone
        if abs(norm_x) < self.dead_zone:
            norm_x = 0
        if abs(norm_y) < self.dead_zone:
            norm_y = 0
        
        # Calculate target angles (adjusted for better tracking)
        pan_delta = -norm_x * 40  # Max 40 degree adjustment (increased range)
        tilt_delta = norm_y * 25  # Max 25 degree adjustment (increased range)
        
        target_pan = self.current_pan + pan_delta
        target_tilt = self.current_tilt + tilt_delta
        
        # Apply smoothing
        if smooth:
            pan_delta = np.clip(target_pan - self.current_pan, -self.max_step, self.max_step)
            tilt_delta = np.clip(target_tilt - self.current_tilt, -self.max_step, self.max_step)
            
            target_pan = self.current_pan + pan_delta
            target_tilt = self.current_tilt + tilt_delta
        
        # Clamp to valid ranges
        target_pan = np.clip(target_pan, self.pan_range[0], self.pan_range[1])
        target_tilt = np.clip(target_tilt, self.tilt_range[0], self.tilt_range[1])
        
        # Update current positions
        self.current_pan = int(target_pan)
        self.current_tilt = int(target_tilt)
        
        return self.current_pan, self.current_tilt
    
    def reset(self):
        """Reset servos to center position"""
        self.current_pan = self.pan_center
        self.current_tilt = self.tilt_center
        return self.current_pan, self.current_tilt


def draw_bounding_box(frame: np.ndarray, 
                      bbox: Tuple[int, int, int, int],
                      label: str = "",
                      color: Tuple[int, int, int] = (0, 255, 0),
                      thickness: int = 2):
    """
    Draw bounding box with label on frame
    
    Args:
        frame: Image frame to draw on
        bbox: Bounding box as (x, y, width, height)
        label: Text label to display
        color: Box color in BGR
        thickness: Line thickness
    """
    x, y, w, h = bbox
    
    # Draw rectangle
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    
    # Draw label if provided
    if label:
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        label_w, label_h = label_size
        
        # Draw label background
        cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w, y), color, -1)
        
        # Draw label text
        cv2.putText(frame, label, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def draw_landmarks(frame: np.ndarray,
                   landmarks: List[Tuple[int, int]],
                   color: Tuple[int, int, int] = (0, 255, 0),
                   radius: int = 3):
    """
    Draw landmark points on frame
    
    Args:
        frame: Image frame to draw on
        landmarks: List of (x, y) landmark coordinates
        color: Point color in BGR
        radius: Point radius
    """
    for point in landmarks:
        cv2.circle(frame, point, radius, color, -1)


def draw_connections(frame: np.ndarray,
                     landmarks: List[Tuple[int, int]],
                     connections: List[Tuple[int, int]],
                     color: Tuple[int, int, int] = (0, 255, 0),
                     thickness: int = 2):
    """
    Draw connections between landmarks
    
    Args:
        frame: Image frame to draw on
        landmarks: List of (x, y) landmark coordinates
        connections: List of (start_idx, end_idx) pairs
        color: Line color in BGR
        thickness: Line thickness
    """
    for connection in connections:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start_point = landmarks[start_idx]
            end_point = landmarks[end_idx]
            cv2.line(frame, start_point, end_point, color, thickness)


def preprocess_frame(frame: np.ndarray,
                     target_size: Optional[Tuple[int, int]] = None,
                     flip: bool = False,
                     convert_rgb: bool = False) -> np.ndarray:
    """
    Preprocess frame for vision processing
    
    Args:
        frame: Input frame
        target_size: Resize to (width, height) if provided
        flip: Flip horizontally
        convert_rgb: Convert BGR to RGB
    
    Returns:
        Preprocessed frame
    """
    processed = frame.copy()
    
    if flip:
        processed = cv2.flip(processed, 1)
    
    if target_size:
        processed = cv2.resize(processed, target_size)
    
    if convert_rgb:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
    
    return processed


def calculate_center(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """
    Calculate center point of bounding box
    
    Args:
        bbox: Bounding box as (x, y, width, height)
    
    Returns:
        Center point as (cx, cy)
    """
    x, y, w, h = bbox
    cx = x + w // 2
    cy = y + h // 2
    return cx, cy


def calculate_distance(point1: Tuple[int, int], 
                      point2: Tuple[int, int]) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
    
    Returns:
        Distance in pixels
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def estimate_depth_from_bbox(bbox_width: int, 
                             reference_width: int = 200,
                             reference_distance: float = 100.0) -> float:
    """
    Estimate relative depth/distance based on bounding box size
    
    Args:
        bbox_width: Width of detected object bounding box
        reference_width: Reference width at known distance
        reference_distance: Known distance for reference width
    
    Returns:
        Estimated distance (relative units)
    """
    if bbox_width > 0:
        return (reference_width * reference_distance) / bbox_width
    return float('inf')


def add_overlay_text(frame: np.ndarray,
                    text_lines: List[str],
                    position: Tuple[int, int] = (10, 30),
                    font_scale: float = 0.6,
                    color: Tuple[int, int, int] = (0, 255, 0),
                    thickness: int = 2,
                    line_spacing: int = 30):
    """
    Add multiple lines of overlay text to frame
    
    Args:
        frame: Image frame to draw on
        text_lines: List of text strings to display
        position: Starting position (x, y)
        font_scale: Font size scale
        color: Text color in BGR
        thickness: Text thickness
        line_spacing: Pixels between lines
    """
    x, y = position
    for i, line in enumerate(text_lines):
        y_pos = y + (i * line_spacing)
        cv2.putText(frame, line, (x, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
