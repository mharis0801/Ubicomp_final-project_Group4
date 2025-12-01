# Smart Door Security Camera - Complete Setup Guide

## 📋 Overview

This is a production-ready Raspberry Pi 5 security system that:
- ✅ Detects humans using YOLOv8 Nano ML model
- ✅ Classifies as ALLOWED (known) or INTRUDER (unknown)
- ✅ Sends instant Telegram notifications with photos
- ✅ Runs completely on-device (no cloud upload of frames)
- ✅ Auto-starts on boot
- ✅ Logs all detections to CSV

## 📦 What You Get

**Core Files:**
- `config.py` - Configuration (tokens, thresholds)
- `main.py` - Detection loop (YOLOv8 + Telegram alerts)
- `notification.py` - Telegram bot handler
- `face_recognition.py` - Face recognition module (optional)
- `utils.py` - Helper functions
- `requirements.txt` - Python dependencies

**Testing Scripts:**
- `scripts/test_telegram.py` - Verify Telegram setup
- `scripts/test_camera.py` - Test USB camera
- `scripts/encode_face.py` - Add known faces

**Auto-start Service:**
- `systemd/smart-door-camera.service` - Boot service

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Telegram Bot

1. Open Telegram
2. Search for **@BotFather**
3. Send `/newbot`
4. Choose name: `RPI5DoorCam`
5. Choose username: `rpi5doorcam_bot`
6. **Copy the token** (save for later)

Get your User ID:
1. Search for **@userinfobot**
2. Send `/start`
3. **Copy your User ID**

### Step 2: Clone Project

```bash
cd ~/
git clone <your-repo> smart_door_camera
cd smart_door_camera
```

### Step 3: Configure

Edit `config.py`:

```bash
nano config.py
```

Find and replace:
```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"    # → paste bot token
TELEGRAM_USER_ID = "YOUR_USER_ID_HERE"       # → paste user ID
```

### Step 4: Install Dependencies

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p known_faces detections
```

### Step 5: Test Connection

```bash
source venv/bin/activate
python3 scripts/test_telegram.py
```

You should receive a test message on Telegram!

### Step 6: Test Camera

```bash
python3 scripts/test_camera.py
```

Should capture 10 frames successfully.

### Step 7: Start Detection

```bash
python3 main.py
```

Stand in front of camera → You get a Telegram alert! 🎉

## 🔧 Project Structure

```
smart_door_camera/
├── config.py                          # ⭐ EDIT THIS
├── main.py                            # Core detection
├── notification.py                    # Telegram sender
├── face_recognition.py                # Face matching
├── utils.py                           # Helpers
├── requirements.txt                   # Dependencies
│
├── known_faces/                       # Store face encodings
│   ├── person1.npy
│   └── person2.npy
│
├── detections/                        # Detection images & logs
│   ├── detection_log.csv              # Auto-created
│   ├── camera.log                     # Auto-created
│   └── detection_john_20250101_100530_123.jpg
│
├── scripts/
│   ├── test_telegram.py               # Test Telegram
│   ├── test_camera.py                 # Test camera
│   └── encode_face.py                 # Encode faces
│
├── systemd/
│   └── smart-door-camera.service      # Auto-start
│
└── README.md                          # This file
```

## ⚙️ Configuration (config.py)

**Required:**
```python
TELEGRAM_BOT_TOKEN = "123456789:ABCDefGhIjkl..."  # From @BotFather
TELEGRAM_USER_ID = "987654321"                    # From @userinfobot
```

**Optional - Performance:**
```python
# For faster (less accurate):
CAMERA_FPS = 10
CAMERA_RESOLUTION = (640, 480)
CONFIDENCE_THRESHOLD = 0.6
ENABLE_FACE_RECOGNITION = False

# For more accurate (slower):
CAMERA_FPS = 30
CAMERA_RESOLUTION = (1920, 1080)
CONFIDENCE_THRESHOLD = 0.4
ENABLE_FACE_RECOGNITION = True
```

**Optional - Features:**
```python
SEND_IMAGE_WITH_ALERT = True        # Include photo
MIN_DETECTION_INTERVAL = 2          # Min seconds between alerts
ALERT_RETENTION_DAYS = 7            # Keep images 7 days
ENABLE_FACE_RECOGNITION = True      # Match known faces
```

## 👤 Add Known Faces (Optional)

Enable ALLOWED person classification:

```bash
# Encode John's face
python3 scripts/encode_face.py john.jpg john

# Encode Sarah's face
python3 scripts/encode_face.py sarah.jpg sarah
```

This creates:
- `known_faces/john.npy`
- `known_faces/sarah.npy`

Then enable in `config.py`:
```python
ENABLE_FACE_RECOGNITION = True
```

Now when John or Sarah appear → "ALLOWED" alert  
Unknown person → "INTRUDER" alert 🚨

## 🔄 Auto-Start on Boot

```bash
sudo cp systemd/smart-door-camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smart-door-camera
sudo systemctl start smart-door-camera
```

Check status:
```bash
sudo systemctl status smart-door-camera

# View logs
sudo journalctl -u smart-door-camera -f

# Stop
sudo systemctl stop smart-door-camera

# Restart
sudo systemctl restart smart-door-camera
```

## 📊 Viewing Detections

**Real-time logs:**
```bash
tail -f detections/camera.log
```

**Detection CSV:**
```bash
cat detections/detection_log.csv
```

**Detection images:**
```bash
ls -lh detections/*.jpg
```

## 🐛 Troubleshooting

**Camera not found:**
```bash
ls /dev/video*

# If /dev/video1 exists, change in config.py:
CAMERA_INDEX = 1
```

**Telegram token error:**
```bash
# Check for extra spaces, paste exactly from @BotFather
# Re-run: python3 scripts/test_telegram.py
```

**Model too slow:**
```python
# config.py:
CAMERA_FPS = 10              # Lower FPS
CAMERA_RESOLUTION = (640, 480)  # Lower resolution
CONFIDENCE_THRESHOLD = 0.6   # Higher = faster
ENABLE_FACE_RECOGNITION = False  # Disable face matching
```

**High CPU usage:**
```bash
# Check current CPU:
top

# Reduce in config.py:
CAMERA_FPS = 5
CAMERA_RESOLUTION = (480, 360)
DISPLAY_FRAMES = False
```

**No detections:**
- Check lighting (need good illumination)
- Try lower confidence threshold
- Test: `python3 scripts/test_camera.py`
- Check logs: `tail detections/camera.log`

**Permission denied:**
```bash
sudo usermod -aG video $USER
# Log out and back in
```

## 📈 Performance Tips

**For RPi 5 with good performance:**
```python
CAMERA_FPS = 15
CAMERA_RESOLUTION = (1280, 720)
CONFIDENCE_THRESHOLD = 0.5
ENABLE_FACE_RECOGNITION = True
```

**For older/slower RPi:**
```python
CAMERA_FPS = 5
CAMERA_RESOLUTION = (640, 480)
CONFIDENCE_THRESHOLD = 0.6
ENABLE_FACE_RECOGNITION = False
```

**Check resources:**
```bash
# CPU/Memory usage
top

# Storage
df -h

# Network
speedtest-cli
```

## 🔒 Security

✅ **Implemented:**
- No raw frames uploaded to cloud
- Face encodings stored locally
- Telegram uses encryption
- Logs stored on device

⚠️ **Recommendations:**
- Use strong WiFi password
- Update RPi OS regularly: `sudo apt update && sudo apt upgrade`
- Delete old images periodically: `python3 scripts/cleanup.py`
- Enable Telegram 2FA

## 🎯 Use Cases

1. **Front Door Security** - Detect intruders, verify delivery persons
2. **Office Access** - Log who enters when
3. **Retail Store** - Track customer flow, VIP detection
4. **Warehouse** - Perimeter monitoring, after-hours alerts
5. **Pet Monitor** - Track pet movements, detect unusual behavior

## 🚀 Next Steps

1. **Web Dashboard** - Create Flask interface to view detections
2. **Email Alerts** - Add email notifications alongside Telegram
3. **Cloud Backup** - Auto-upload critical alerts to Drive
4. **Multiple Cameras** - Run multiple RPi units
5. **Sound Alert** - Add buzzer/speaker via GPIO
6. **Home Assistant** - Integrate with smart home
7. **Custom Training** - Fine-tune YOLOv8 on your door

## 📞 Support

**For issues:**
1. Check `detections/camera.log`
2. Run `python3 scripts/test_camera.py`
3. Run `python3 scripts/test_telegram.py`
4. Check `CAMERA_INDEX` and `TELEGRAM_*` config

**Common errors:**
- "Failed to open camera" → Check USB, verify index
- "Telegram error" → Check token, user ID, internet
- "Model too slow" → Reduce FPS/resolution
- "Out of memory" → Lower resolution, disable face recognition

## 📝 License

Open-source. Modify freely for personal/commercial use.

---

**Version:** 1.0  
**Last Updated:** January 15, 2025  
**Tested On:** Raspberry Pi 5 (Bookworm 64-bit)