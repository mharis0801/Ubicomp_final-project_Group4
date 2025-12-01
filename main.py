#!/usr/bin/env python3
"""
main.py - Smart Door Camera Main Detection Loop

Core functionality:
- Capture frames from USB webcam
- Run YOLOv8 inference
- Recognize persons with face recognition
- Send Telegram alerts
- Save detection logs and images

Run with: python3 main.py
"""

import cv2
import numpy as np
import logging
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
import threading
import time
import signal
import sys

import config
from notification import send_detection_sync, send_startup_sync, send_error_sync
from utils import setup_logging, cleanup_old_images, save_detection_csv, validate_config

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Import face recognizer if available
try:
    from face_recognition import FaceRecognizer
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition module not available")


class SmartDoorCamera:
    """Main smart door camera system"""
    
    def __init__(self):
        """Initialize camera system"""
        self.running = False
        self.model = None
        self.face_recognizer = None
        self.cap = None
        self.lock = threading.Lock()
        
        logger.info("=" * 60)
        logger.info("Smart Door Camera System - RPi 5")
        logger.info("=" * 60)
        
        # Validate configuration
        if not validate_config():
            raise RuntimeError("Configuration validation failed")
        
        # Initialize components
        self._load_model()
        self._load_face_recognizer()
        logger.info("✅ System initialized successfully")
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            logger.info(f"📦 Loading YOLOv8 model: {config.DETECTION_MODEL}")
            self.model = YOLO(config.DETECTION_MODEL)
            logger.info(f"✅ Model loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load model: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _load_face_recognizer(self):
        """Load face recognizer if enabled"""
        if not config.ENABLE_FACE_RECOGNITION:
            logger.info("Face recognition disabled in config")
            return
        
        if not FACE_RECOGNITION_AVAILABLE:
            logger.warning("Face recognition library not available")
            logger.warning("Install with: pip install face-recognition")
            return
        
        try:
            logger.info("👤 Loading face recognizer...")
            self.face_recognizer = FaceRecognizer(config.KNOWN_FACES_DIR)
            logger.info("✅ Face recognizer loaded")
        except Exception as e:
            logger.warning(f"⚠️  Face recognition disabled: {e}")
            self.face_recognizer = None
    
    def run(self):
        """Main camera loop"""
        self.running = True
        logger.info("🎥 Starting camera loop...")
        
        # Send startup notification
        try:
            send_startup_sync()
        except Exception as e:
            logger.warning(f"Startup notification failed: {e}")
        
        # Open camera
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        if not self.cap.isOpened():
            error_msg = f"Failed to open camera at index {config.CAMERA_INDEX}"
            logger.error(f"❌ {error_msg}")
            send_error_sync(error_msg)
            return
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_RESOLUTION[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_RESOLUTION[1])
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(
            f"✅ Camera opened: {actual_width}x{actual_height} @ {actual_fps:.0f}fps"
        )
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("❌ Failed to grab frame")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Process frame
                self._process_frame(frame)
                
                # Display if configured
                if config.DISPLAY_FRAMES:
                    cv2.imshow('Smart Door Camera', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Quit requested by user")
                        break
                
                # Log FPS every 100 frames
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    logger.debug(f"Processing FPS: {fps:.1f}")
                    
                    # Cleanup old images periodically
                    if frame_count % 1000 == 0:
                        cleanup_old_images(config.ALERT_RETENTION_DAYS)
        
        except KeyboardInterrupt:
            logger.info("⏹️  Keyboard interrupt received")
        except Exception as e:
            error_msg = f"Camera loop error: {e}"
            logger.error(f"❌ {error_msg}")
            send_error_sync(error_msg)
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        logger.info("🔌 Cleaning up resources...")
        self.running = False
        
        if self.cap:
            self.cap.release()
            logger.info("✅ Camera released")
        
        if config.DISPLAY_FRAMES:
            cv2.destroyAllWindows()
    
    def _process_frame(self, frame: np.ndarray):
        """Process single frame for detections"""
        try:
            # Run inference
            results = self.model(
                frame,
                conf=config.CONFIDENCE_THRESHOLD,
                verbose=False,
                device=0  # 0 = GPU if available, else CPU
            )
            
            # Process detections
            for result in results:
                if not result.boxes or len(result.boxes) == 0:
                    continue
                
                for box in result.boxes:
                    # Get detection info
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Only care about 'person' class (index 0 in COCO)
                    if cls != 0:
                        continue
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Validate coordinates
                    if x1 >= x2 or y1 >= y2:
                        continue
                    
                    # Extract face crop
                    crop = frame[max(0, y1):min(frame.shape[0], y2), 
                                 max(0, x1):min(frame.shape[1], x2)]
                    
                    if crop.size == 0:
                        continue
                    
                    # Recognize face if enabled
                    person_name = "Unknown"
                    if self.face_recognizer:
                        person_name = self.face_recognizer.recognize_face(
                            crop,
                            tolerance=config.FACE_RECOGNITION_THRESHOLD
                        )
                    
                    # Determine person type
                    person_type = "ALLOWED" if person_name != "Unknown" else "INTRUDER"
                    
                    # Save detection image
                    image_path = self._save_detection_image(frame, conf, person_name)
                    
                    # Send alert
                    try:
                        send_detection_sync(
                            person_type=person_type,
                            confidence=conf,
                            image_path=image_path,
                            person_name=person_name
                        )
                    except Exception as e:
                        logger.error(f"Failed to send alert: {e}")
                    
                    # Log detection
                    save_detection_csv(
                        timestamp=datetime.now().isoformat(),
                        person_type=person_type,
                        person_name=person_name,
                        confidence=conf
                    )
                    
                    emoji = "🚨" if person_type == "INTRUDER" else "👤"
                    logger.info(
                        f"{emoji} Detection: {person_type} - {person_name} "
                        f"(confidence: {conf:.1%})"
                    )
        
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
    
    def _save_detection_image(self, frame: np.ndarray, confidence: float, 
                              person_name: str) -> str:
        """Save detection image with metadata overlay"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"detection_{person_name}_{timestamp}.jpg"
            filepath = config.DETECTIONS_DIR / filename
            
            # Create copy to avoid modifying original
            frame_copy = frame.copy()
            
            # Add text overlay
            text = f"{person_name} ({confidence:.0%})"
            cv2.putText(
                frame_copy, text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2
            )
            
            # Add timestamp
            cv2.putText(
                frame_copy,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2
            )
            
            # Save image
            cv2.imwrite(str(filepath), frame_copy)
            logger.debug(f"Image saved: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return ""
    
    def stop(self):
        """Stop camera loop gracefully"""
        logger.info("Requesting stop...")
        self.running = False


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n⏹️  Received signal, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    camera = None
    
    try:
        camera = SmartDoorCamera()
        camera.run()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        try:
            send_error_sync(f"Fatal error: {e}")
        except:
            pass
    finally:
        if camera:
            camera._cleanup()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    main()