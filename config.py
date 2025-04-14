import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Telegram Bot Token
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # e.g., '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ'

    # Telegram Channel ID (use negative ID for channels)
    CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1001234567890"))  # Replace with your channel ID

    # Base message ID to calculate file references
    BASE_MESSAGE_ID = int(os.getenv("BASE_MESSAGE_ID", "100"))  # Replace with your base message ID

    # List of admin user IDs
    ADMINS = list(map(int, os.getenv("ADMINS", "").split(',')))  # e.g., '123456789,987654321'

    # Optional: File ID for the welcome video
    WELCOME_VIDEO_ID = os.getenv("WELCOME_VIDEO_ID")  # e.g., 'BAACAgUAAxkBAAIBQ2Q...'

    # Optional: File ID for the stats animation
    STATS_ANIMATION_ID = os.getenv("STATS_ANIMATION_ID")  # e.g., 'CgACAgQAAxkBAAIBR2Q...'
