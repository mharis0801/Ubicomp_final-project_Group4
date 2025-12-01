#!/usr/bin/env python3
"""
config.py - Smart Door Camera Configuration File

EDIT THIS FILE FIRST with your Telegram credentials!
All other settings can be adjusted based on your needs.
"""

import os
from pathlib import Path

# ==================== TELEGRAM CONFIG ====================
# Get these from Telegram @BotFather and @userinfobot
TELEGRAM_BOT_TOKEN = "8263669951:AAH7Zdpm_0YX_rsNGTbF5v801_9VbqITe3M"     # Replace with your bot token
TELEGRAM_USER_ID = "1042611352"        # Replace with your user ID
TELEGRAM_CHANNEL_ID = "@rpi5doorcam"          # Optional: for persistent alerts

# ==================== DETECTION CONFIG ====================
CONFIDENCE_THRESHOLD = 0.5              # YOLOv8 confidence (0-1, higher = stricter)
DETECTION_MODEL = "yolov8n.pt"          # Nano model (fastest on RPi, 2MB)
# Other options: yolov8s.pt (small), yolov8m.pt (medium) - slower but more accurate
DETECTION_CLASSES = ["person"]          # Only detect humans

# ==================== FACE RECOGNITION CONFIG ====================
ENABLE_FACE_RECOGNITION = True          # Enable ALLOWED vs INTRUDER classification
FACE_RECOGNITION_THRESHOLD = 0.6        # Match threshold (0-1, lower = stricter matching)
KNOWN_FACES_DIR = Path("known_faces")   # Directory with known person face encodings
KNOWN_FACES_DIR.mkdir(exist_ok=True)

# ==================== CAMERA CONFIG ====================
CAMERA_INDEX = 0                        # USB webcam index (0 = first camera)
CAMERA_RESOLUTION = (1280, 720)         # Resolution (higher = slower but better detection)
CAMERA_FPS = 15                         # Process frames per second (lower = faster, less CPU)

# ==================== STORAGE CONFIG ====================
DETECTIONS_DIR = Path("detections")     # Directory for saved detection images
DETECTIONS_DIR.mkdir(exist_ok=True)
LOG_FILE = DETECTIONS_DIR / "detection_log.csv"  # CSV log of all detections

# ==================== ALERT CONFIG ====================
MIN_DETECTION_INTERVAL = 2              # Minimum seconds between alerts for same person
SEND_IMAGE_WITH_ALERT = True            # Send detection photo with Telegram alert
ALERT_RETENTION_DAYS = 7                # Delete images older than 7 days
MAX_DETECTIONS_PER_HOUR = 60            # Rate limit: max alerts per hour

# ==================== DEBUG & TESTING ====================
DEBUG_MODE = True                       # Print debug info to console
DISPLAY_FRAMES = False                  # Show real-time detection (requires display/SSH X11)

# ==================== PERFORMANCE TUNING ====================
# For FASTER performance (lower accuracy):
# CAMERA_FPS = 10
# CAMERA_RESOLUTION = (640, 480)
# CONFIDENCE_THRESHOLD = 0.6
# ENABLE_FACE_RECOGNITION = False

# For BETTER accuracy (higher resource usage):
# CAMERA_FPS = 30
# CAMERA_RESOLUTION = (1920, 1080)
# CONFIDENCE_THRESHOLD = 0.4
# ENABLE_FACE_RECOGNITION = True

# ==================== AUTO-COMPUTED PATHS ====================
PROJECT_ROOT = Path(__file__).parent
DETECTIONS_DIR = PROJECT_ROOT / DETECTIONS_DIR
KNOWN_FACES_DIR = PROJECT_ROOT / KNOWN_FACES_DIR

# ==================== FEATURE FLAGS ====================
LOG_TO_FILE = True                      # Save logs to detections/camera.log
CLEANUP_OLD_IMAGES = True               # Automatically delete old detection images
SEND_STARTUP_NOTIFICATION = True        # Alert when system starts
SEND_ERROR_NOTIFICATIONS = True         # Alert on errors