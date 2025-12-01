#!/usr/bin/env python3
"""
notification.py - Telegram Bot Notification Handler

Handles all Telegram notifications:
- Detection alerts with images
- Startup notifications
- Error alerts
- Rate limiting to prevent spam
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError

import smart_door_camera.config as config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handle all Telegram notifications for door camera alerts"""
    
    def __init__(self):
        """Initialize Telegram bot"""
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.user_id = config.TELEGRAM_USER_ID
        self.channel_id = config.TELEGRAM_CHANNEL_ID
        self.last_alert_time = {}  # Track last alert per person
        self.alerts_today = {}  # Track alerts per hour
    
    async def send_detection_alert(self, 
                                   person_type: str, 
                                   confidence: float, 
                                   image_path: str = None, 
                                   person_name: str = "Unknown"):
        """
        Send detection alert with image to admin
        
        Args:
            person_type: "ALLOWED" or "INTRUDER"
            confidence: Detection confidence (0-1)
            image_path: Path to detection image
            person_name: Name of detected person (if recognized)
        """
        
        # Check alert rate limit
        if not self._check_rate_limit(person_name):
            if config.DEBUG_MODE:
                logger.info(f"Rate limited alert for {person_name}")
            return
        
        try:
            # Create alert message
            alert_level = "🚨 INTRUDER ALERT" if person_type == "INTRUDER" else "👤 Person Detected"
            emoji = "🔴" if person_type == "INTRUDER" else "🟢"
            
            message = f"""{emoji} *{alert_level}*

*Status:* {person_type}
*Confidence:* {confidence:.1%}
*Person:* {person_name}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

_Smart Door Camera | RPi5_"""
            
            # Send to user
            if image_path and config.SEND_IMAGE_WITH_ALERT:
                await self._send_photo_with_caption(
                    chat_id=self.user_id,
                    photo_path=image_path,
                    caption=message,
                    person_type=person_type
                )
            else:
                await self.bot.send_message(
                    chat_id=self.user_id,
                    text=message,
                    parse_mode="Markdown"
                )
            
            # Also send to channel if configured
            if self.channel_id and self.channel_id != "@rpi5doorcam":
                if image_path and config.SEND_IMAGE_WITH_ALERT:
                    await self._send_photo_with_caption(
                        chat_id=self.channel_id,
                        photo_path=image_path,
                        caption=message,
                        person_type=person_type
                    )
            
            logger.info(f"✅ Alert sent: {person_type} - {person_name}")
            self._update_rate_limit(person_name)
            
        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
    
    async def _send_photo_with_caption(self, 
                                      chat_id: str, 
                                      photo_path: str, 
                                      caption: str, 
                                      person_type: str):
        """Send photo with caption, handling file validation"""
        try:
            photo_file = Path(photo_path)
            if not photo_file.exists():
                logger.warning(f"Photo not found: {photo_path}")
                return
            
            with open(photo_file, 'rb') as f:
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=caption,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            # Fallback to text-only message
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode="Markdown"
                )
            except Exception as e2:
                logger.error(f"Fallback message failed: {e2}")
    
    def _check_rate_limit(self, person_name: str) -> bool:
        """Check if enough time has passed since last alert for this person"""
        current_time = datetime.now().timestamp()
        last_time = self.last_alert_time.get(person_name, 0)
        return (current_time - last_time) >= config.MIN_DETECTION_INTERVAL
    
    def _update_rate_limit(self, person_name: str):
        """Update last alert time for person"""
        self.last_alert_time[person_name] = datetime.now().timestamp()
    
    async def send_startup_notification(self):
        """Send notification when system starts"""
        if not config.SEND_STARTUP_NOTIFICATION:
            return
        
        try:
            message = f"""✅ *Door Camera Online*

*Device:* Raspberry Pi 5
*Started:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Model:* YOLOv8 Nano
*Face Recognition:* {'Enabled' if config.ENABLE_FACE_RECOGNITION else 'Disabled'}
*Status:* Ready for detections

_Smart Door Security System_"""
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode="Markdown"
            )
            logger.info("✅ Startup notification sent")
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
    
    async def send_error_notification(self, error_msg: str):
        """Send error alert to admin"""
        if not config.SEND_ERROR_NOTIFICATIONS:
            return
        
        try:
            message = f"""⚠️ *System Error*

*Error:* {error_msg}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

_Smart Door Camera Alert_"""
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode="Markdown"
            )
            logger.error(f"Error notification sent: {error_msg}")
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")


# Synchronous wrappers for easy integration with main.py
def send_detection_sync(person_type: str, 
                       confidence: float, 
                       image_path: str = None, 
                       person_name: str = "Unknown"):
    """Synchronous wrapper to send alerts"""
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_detection_alert(
        person_type=person_type,
        confidence=confidence,
        image_path=image_path,
        person_name=person_name
    ))


def send_startup_sync():
    """Synchronous wrapper for startup notification"""
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_startup_notification())


def send_error_sync(error_msg: str):
    """Synchronous wrapper for error notification"""
    notifier = TelegramNotifier()
    asyncio.run(notifier.send_error_notification(error_msg))