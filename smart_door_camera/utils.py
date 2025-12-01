#!/usr/bin/env python3
"""
utils.py - Utility Functions

Helper functions for:
- Image cleanup (remove old detection images)
- Logging setup
- File operations
- Statistics
"""

import logging
import csv
import shutil
from pathlib import Path
from datetime import datetime, timedelta

import smart_door_camera.config as config


def setup_logging():
    """Setup logging to file and console"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if config.LOG_TO_FILE:
        log_file = config.DETECTIONS_DIR / "camera.log"
        handlers = [
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    else:
        handlers = [logging.StreamHandler()]
    
    logging.basicConfig(
        level=logging.INFO if not config.DEBUG_MODE else logging.DEBUG,
        format=log_format,
        handlers=handlers
    )


def cleanup_old_images(days: int = 7):
    """
    Delete detection images older than specified days
    
    Args:
        days: Number of days to keep images (default 7)
    """
    if not config.CLEANUP_OLD_IMAGES:
        return
    
    logger = logging.getLogger(__name__)
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    try:
        for image_file in config.DETECTIONS_DIR.glob("detection_*.jpg"):
            if image_file.stat().st_mtime < cutoff_date.timestamp():
                image_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"🧹 Cleaned up {deleted_count} old detection images")
    
    except Exception as e:
        logger.error(f"Error cleaning up images: {e}")


def save_detection_csv(timestamp: str, person_type: str, person_name: str, 
                      confidence: float, camera: str = "front_door"):
    """
    Log detection to CSV file
    
    Args:
        timestamp: ISO format timestamp
        person_type: "ALLOWED" or "INTRUDER"
        person_name: Name of detected person
        confidence: Detection confidence (0-1)
        camera: Camera identifier
    """
    logger = logging.getLogger(__name__)
    
    try:
        log_entry = {
            'timestamp': timestamp,
            'person_type': person_type,
            'person_name': person_name,
            'confidence': f"{confidence:.3f}",
            'camera': camera
        }
        
        file_exists = config.LOG_FILE.exists()
        
        with open(config.LOG_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)
        
        logger.debug(f"Detection logged: {person_type} - {person_name}")
    
    except Exception as e:
        logger.error(f"Error logging detection: {e}")


def get_detection_stats(hours: int = 24) -> dict:
    """
    Get detection statistics from log
    
    Args:
        hours: Number of hours to analyze (default 24)
    
    Returns:
        Dictionary with stats
    """
    logger = logging.getLogger(__name__)
    stats = {
        'total_detections': 0,
        'allowed_count': 0,
        'intruder_count': 0,
        'unique_persons': set(),
        'average_confidence': 0.0
    }
    
    try:
        if not config.LOG_FILE.exists():
            return stats
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        confidences = []
        
        with open(config.LOG_FILE, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                    
                    if timestamp < cutoff_time:
                        continue
                    
                    stats['total_detections'] += 1
                    stats['unique_persons'].add(row['person_name'])
                    
                    if row['person_type'] == 'ALLOWED':
                        stats['allowed_count'] += 1
                    else:
                        stats['intruder_count'] += 1
                    
                    confidences.append(float(row['confidence']))
                
                except Exception as e:
                    logger.debug(f"Error parsing log row: {e}")
        
        if confidences:
            stats['average_confidence'] = sum(confidences) / len(confidences)
        
        stats['unique_persons'] = len(stats['unique_persons'])
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
    
    return stats


def archive_detections(output_path: Path):
    """
    Archive all detection images and logs
    
    Args:
        output_path: Destination zip file
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Archiving detections to {output_path}")
        shutil.make_archive(
            str(output_path.with_suffix('')),
            'zip',
            config.DETECTIONS_DIR
        )
        logger.info(f"✅ Archive created: {output_path}")
    
    except Exception as e:
        logger.error(f"Error archiving detections: {e}")


def validate_config():
    """Validate configuration before starting"""
    logger = logging.getLogger(__name__)
    errors = []
    
    # Check Telegram config
    if config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("❌ TELEGRAM_BOT_TOKEN not configured")
    
    if config.TELEGRAM_USER_ID == "YOUR_USER_ID_HERE":
        errors.append("❌ TELEGRAM_USER_ID not configured")
    
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_USER_ID:
        errors.append("❌ Telegram credentials missing")
    
    # Check directories
    if not config.DETECTIONS_DIR.exists():
        try:
            config.DETECTIONS_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {config.DETECTIONS_DIR}")
        except Exception as e:
            errors.append(f"❌ Cannot create {config.DETECTIONS_DIR}: {e}")
    
    if not config.KNOWN_FACES_DIR.exists():
        try:
            config.KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {config.KNOWN_FACES_DIR}")
        except Exception as e:
            errors.append(f"❌ Cannot create {config.KNOWN_FACES_DIR}: {e}")
    
    if errors:
        for error in errors:
            logger.error(error)
        return False
    
    logger.info("✅ Configuration valid")
    return True