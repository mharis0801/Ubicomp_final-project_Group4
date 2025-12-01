#!/usr/bin/env python3
"""
scripts/encode_face.py - Encode Known Faces

Creates face encodings from images and saves them as *.npy files
for face recognition.

Usage:
  python3 scripts/encode_face.py photo.jpg person_name
  python3 scripts/encode_face.py john.jpg john
  python3 scripts/encode_face.py sarah.jpg sarah

Requirements:
  pip install face-recognition
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config as config
from face_recognition import FaceRecognizer


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("=" * 60)
        print("Face Encoding Tool")
        print("=" * 60)
        print("\nUsage: python3 scripts/encode_face.py <image_path> <person_name>")
        print("\nExamples:")
        print("  python3 scripts/encode_face.py photo_john.jpg john")
        print("  python3 scripts/encode_face.py sarah.png sarah")
        print("\nRequirements:")
        print("  pip install face-recognition")
        print("\nOutput:")
        print(f"  Encoding saved to: known_faces/[person_name].npy")
        return
    
    image_path = sys.argv[1]
    person_name = sys.argv[2]
    
    print("=" * 60)
    print("Face Encoding Tool")
    print("=" * 60)
    
    # Check if image exists
    image_file = Path(image_path)
    if not image_file.exists():
        print(f"\n❌ ERROR: Image file not found: {image_path}")
        return
    
    print(f"\n📷 Image: {image_path}")
    print(f"👤 Person: {person_name}")
    print(f"💾 Output directory: {config.KNOWN_FACES_DIR}")
    
    # Encode face
    print(f"\n🔄 Encoding face...")
    
    try:
        success = FaceRecognizer.encode_and_save_face(
            image_path,
            person_name,
            config.KNOWN_FACES_DIR
        )
        
        if success:
            output_file = config.KNOWN_FACES_DIR / f"{person_name}.npy"
            print(f"\n✅ Success! Face encoding saved:")
            print(f"   {output_file}")
            print(f"\n📝 To enable face recognition:")
            print(f"   1. Edit config.py")
            print(f"   2. Set: ENABLE_FACE_RECOGNITION = True")
            print(f"   3. Repeat this script for each known person")
            print(f"   4. Run: python3 main.py")
        else:
            print(f"\n❌ Failed to encode face")
            print(f"   Make sure the image contains a clear face")
            print(f"   Try with a different photo")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n📦 Install face_recognition:")
        print(f"   pip install face-recognition")


if __name__ == "__main__":
    main()