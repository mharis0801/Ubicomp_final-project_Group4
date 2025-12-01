#!/usr/bin/env python3
"""
face_recognition.py - Face Recognition Module

Optional face recognition using face_recognition library
Enables classification of ALLOWED (known) vs INTRUDER (unknown) persons

Setup:
  1. Install: pip install face-recognition
  2. Use scripts/encode_face.py to create known_faces/*.npy files
  3. Enable in config.py: ENABLE_FACE_RECOGNITION = True
"""

import numpy as np
from pathlib import Path
import cv2
import logging

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """Face recognition using pre-computed face encodings"""
    
    def __init__(self, known_faces_dir: Path):
        """
        Initialize face recognizer
        
        Args:
            known_faces_dir: Directory containing *.npy encoding files
        """
        self.known_faces_dir = known_faces_dir
        self.known_faces = {}
        self.face_recognition = None
        self._load_library()
        self._load_known_faces()
    
    def _load_library(self):
        """Load face_recognition library"""
        try:
            import face_recognition as face_recognition
            self.face_recognition = face_recognition
            logger.info("✅ face_recognition library loaded")
        except ImportError:
            logger.warning("⚠️  face_recognition not installed")
            logger.warning("   Install with: pip install face-recognition")
            self.face_recognition = None
    
    def _load_known_faces(self):
        """Load pre-computed face encodings from disk"""
        if not self.face_recognition:
            logger.warning("Skipping face loading - library not available")
            return
        
        encoding_files = list(self.known_faces_dir.glob("*.npy"))
        if not encoding_files:
            logger.warning(f"No face encodings found in {self.known_faces_dir}")
            return
        
        for face_file in encoding_files:
            try:
                person_name = face_file.stem
                encoding = np.load(face_file)
                self.known_faces[person_name] = encoding
                logger.info(f"✅ Loaded face: {person_name}")
            except Exception as e:
                logger.error(f"Error loading {face_file}: {e}")
    
    def recognize_face(self, image: np.ndarray, tolerance: float = 0.6) -> str:
        """
        Recognize face in image
        
        Args:
            image: OpenCV image (BGR format)
            tolerance: Face matching tolerance (0-1, lower = stricter)
                      0.6 = default (works for most people)
                      0.5 = stricter (fewer false positives)
                      0.7 = looser (more detections)
        
        Returns:
            Person name if recognized, "UNKNOWN" if not found
        """
        if not self.face_recognition or not self.known_faces:
            return "UNKNOWN"
        
        try:
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find faces in image
            face_locations = self.face_recognition.face_locations(
                rgb_image,
                model="hog"  # "hog" for speed, "cnn" for accuracy
            )
            if not face_locations:
                logger.debug("No faces detected in image")
                return "UNKNOWN"
            
            # Get encoding for first detected face
            face_encodings = self.face_recognition.face_encodings(
                rgb_image, 
                face_locations
            )
            if not face_encodings:
                logger.debug("Could not encode detected face")
                return "UNKNOWN"
            
            detected_encoding = face_encodings[0]
            
            # Compare with known faces
            min_distance = float('inf')
            matched_name = "UNKNOWN"
            
            for person_name, known_encoding in self.known_faces.items():
                distance = np.linalg.norm(detected_encoding - known_encoding)
                logger.debug(f"Face match distance for {person_name}: {distance:.3f}")
                
                if distance < min_distance:
                    min_distance = distance
                    matched_name = person_name
            
            # Check if distance is within tolerance
            if min_distance < tolerance:
                logger.info(
                    f"✅ Face recognized: {matched_name} (distance: {min_distance:.3f})"
                )
                return matched_name
            else:
                logger.info(
                    f"❌ Face not recognized (distance: {min_distance:.3f} > {tolerance})"
                )
                return "UNKNOWN"
        
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return "UNKNOWN"
    
    @staticmethod
    def encode_and_save_face(image_path: str, person_name: str, output_dir: Path) -> bool:
        """
        Encode a face from image and save encoding to *.npy file
        
        Use this to create known_faces/*.npy files for recognition
        
        Args:
            image_path: Path to image file (jpg, png, etc)
            person_name: Name of person in image
            output_dir: Directory to save *.npy encoding file
        
        Returns:
            True if successful, False otherwise
        
        Example:
            FaceRecognizer.encode_and_save_face(
                'photos/john.jpg',
                'john',
                Path('known_faces')
            )
        """
        try:
            import face_recognition as face_recognition
        except ImportError:
            logger.error("face_recognition not installed")
            logger.error("Install with: pip install face-recognition")
            return False
        
        try:
            logger.info(f"Loading image: {image_path}")
            image = face_recognition.load_image_file(image_path)
            
            logger.info("Encoding face...")
            encodings = face_recognition.face_encodings(image)
            
            if not encodings:
                logger.warning(f"❌ No face found in {image_path}")
                return False
            
            if len(encodings) > 1:
                logger.warning(f"⚠️  Multiple faces found, using first one")
            
            encoding = encodings[0]
            output_path = output_dir / f"{person_name}.npy"
            
            logger.info(f"Saving encoding: {output_path}")
            np.save(output_path, encoding)
            
            logger.info(f"✅ Face encoding saved: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error encoding face: {e}")
            return False


# Quick test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 face_recognition.py <image_path> <person_name>")
        print("Example: python3 face_recognition.py john.jpg john")
        sys.exit(1)
    
    image_path = sys.argv[1]
    person_name = sys.argv[2]
    
    FaceRecognizer.encode_and_save_face(image_path, person_name, Path("known_faces"))