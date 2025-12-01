#!/usr/bin/env python3
"""
scripts/test_telegram.py - Test Telegram Bot Connection

Verifies that Telegram bot credentials are correct
and that messages can be sent successfully.

Run with: python3 scripts/test_telegram.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config as config
from notification import TelegramNotifier
import asyncio


async def test_telegram():
    """Test Telegram connection"""
    print("=" * 60)
    print("Testing Telegram Connection")
    print("=" * 60)
    
    # Validate config
    if config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not configured")
        print("   Edit config.py and set your token from @BotFather")
        return False
    
    if config.TELEGRAM_USER_ID == "YOUR_USER_ID_HERE":
        print("❌ ERROR: TELEGRAM_USER_ID not configured")
        print("   Edit config.py and set your user ID from @userinfobot")
        return False
    
    print(f"✅ Token configured: {config.TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"✅ User ID configured: {config.TELEGRAM_USER_ID}")
    
    # Test connection
    print("\n📤 Sending test message...")
    
    try:
        notifier = TelegramNotifier()
        
        test_message = """✅ *Telegram Bot Test Successful*

Your door camera system is configured correctly!

*Configuration:*
• Bot Token: Connected ✓
• User ID: Connected ✓
• Camera: Ready to deploy

You will receive notifications at this chat when motion/persons are detected.

_Smart Door Camera System_"""
        
        await notifier.bot.send_message(
            chat_id=config.TELEGRAM_USER_ID,
            text=test_message,
            parse_mode="Markdown"
        )
        
        print("✅ Test message sent successfully!")
        print("\n🎉 Telegram is configured correctly!")
        print("\nNext steps:")
        print("1. Configure known faces (optional)")
        print("2. Run: python3 main.py")
        print("3. Point camera at a person")
        print("4. You should receive an alert on Telegram")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("• Check internet connection")
        print("• Verify bot token is correct")
        print("• Verify user ID is correct")
        print("• Check if bot is still active")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_telegram())
    sys.exit(0 if success else 1)