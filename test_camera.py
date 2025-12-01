#!/usr/bin/env python3
"""
scripts/test_camera.py - Test USB Camera

Tests that the USB camera is working and can capture frames.

Run with: python3 scripts/test_camera.py
"""

import cv2
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config


def test_camera():
    """Test camera connection"""
    print("=" * 60)
    print("Testing USB Camera")
    print("=" * 60)
    
    print(f"\n📷 Attempting to open camera at index: {config.CAMERA_INDEX}")
    print(f"   Resolution: {config.CAMERA_RESOLUTION[0]}x{config.CAMERA_RESOLUTION[1]}")
    print(f"   FPS: {config.CAMERA_FPS}")
    
    # Open camera
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    
    if not cap.isOpened():
        print(f"\n❌ ERROR: Cannot open camera at index {config.CAMERA_INDEX}")
        print("\nTroubleshooting:")
        print("1. Check USB connection")
        print("2. Run: ls /dev/video*  (to find camera index)")
        print("3. If /dev/video1 exists, change CAMERA_INDEX = 1 in config.py")
        print("4. Check permissions: sudo usermod -aG video $USER")
        return False
    
    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_RESOLUTION[1])
    cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
    
    # Get actual properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"\n✅ Camera opened successfully!")
    print(f"   Actual Resolution: {width}x{height}")
    print(f"   Actual FPS: {fps:.0f}")
    
    # Capture frames
    print(f"\n📹 Capturing {10} frames...")
    
    frame_count = 0
    try:
        for i in range(10):
            ret, frame = cap.read()
            
            if ret:
                frame_count += 1
                print(f"   Frame {i+1}/10: {frame.shape}")
            else:
                print(f"   Frame {i+1}/10: ❌ Failed")
    
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    
    cap.release()
    
    if frame_count >= 10:
        print(f"\n✅ Camera test successful! ({frame_count}/10 frames captured)")
        print("\n🎉 Camera is working correctly!")
        print("\nNext steps:")
        print("1. Test Telegram: python3 scripts/test_telegram.py")
        print("2. Start detection: python3 main.py")
        return True
    else:
        print(f"\n❌ Camera test failed! ({frame_count}/10 frames captured)")
        return False


if __name__ == "__main__":
    success = test_camera()
    sys.exit(0 if success else 1)