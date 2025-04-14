from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import Config
import logging
import sqlite3
import asyncio

# Enable detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== DATABASE SETUP ==================
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
conn.commit()

def add_user(user_id: int):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]

# ================== AUTO-DELETE WITH OPTIONAL NOTIFICATION ==================
async def auto_delete(message: Message, delay: int, context: ContextTypes.DEFAULT_TYPE = None, notify: bool = False):
    """Delete a Telegram Message object after delay, optionally notify user"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
        logger.info(f"Deleted message {message.message_id}")

        if notify and context:
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=(
                    '<b>"Eng: Your video has been automatically deleted to save space.\n'
                    'Uzbek: Xotirani tejash uchun videongiz avtomatik tarzda o\'chirildi."</b>'
                ),
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Delete failed: {e}")

# ================== COMMAND HANDLERS ==================

# /start command: sends a video with a bold, quoted bilingual caption
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    
    # Define your caption with bold formatting and quotes
    caption = (
        '<b>"👋 Eng: Hi P C! Send a number to get the corresponding file.\n'
        'Uzbek: Salom! Faylni olish uchun raqam yuboring."</b>'
    )
    
    # Replace with your actual video file_id
    video_file_id = 'YOUR_VIDEO_FILE_ID'
    
    # Send the video with the caption
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=video_file_id,
        caption=caption,
        parse_mode='HTML'
    )
    
    # Optionally, you can schedule deletion of the /start command message too
    asyncio.create_task(auto_delete(update.message, 10))

# /stats command: shows user count and then sends an awesome animation
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_all_users()
    total_users = len(users)
    
    # Create a bold, quoted bilingual message with stats
    stats_message = (
        f'<b>"Eng: Total Users: {total_users}\n'
        f'Uzbek: Umumiy foydalanuvchilar: {total_users}"</b>'
    )
    
    # Send stats message
    sent_stats = await update.message.reply_text(
        stats_message,
        parse_mode='HTML'
    )
    
    # Optionally, delete the user's command message after a short delay
    asyncio.create_task(auto_delete(update.message, 10))
    
    # Replace with your actual animation file_id or URL
    animation_file_id = 'YOUR_ANIMATION_FILE_ID'
    # Send an awesome animation to celebrate!
    await context.bot.send_animation(
        chat_id=update.effective_chat.id,
        animation=animation_file_id,
        caption=(
            '<b>"Eng: Enjoy the animation!\n'
            'Uzbek: Animatsiyadan bahramand bo\'ling!"</b>'
        ),
        parse_mode='HTML'
    )
    # Optionally, auto-delete the stats message after some time
    asyncio.create_task(auto_delete(sent_stats, 30))

# /handle_number command: unchanged from previous version
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_msg = update.message
        number = int(user_msg.text)
        
        if number < 1:
            reply = await user_msg.reply_text(
                '<b>"Eng: Please enter a positive number.\n'
                'Uzbek: Iltimos, musbat raqam kiriting."</b>',
                parse_mode='HTML'
            )
            asyncio.create_task(auto_delete(reply, 10))
            asyncio.create_task(auto_delete(user_msg, 10))
            return
        
        message_id = Config.BASE_MESSAGE_ID + (number - 1)
        
        # Forward file (ensures we get a full Message object for deletion)
        forwarded_msg = await context.bot.forward_message(
            chat_id=user_msg.chat_id,
            from_chat_id=Config.CHANNEL_ID,
            message_id=message_id
        )
        
        # Schedule deletions: notify user after deletion
        asyncio.create_task(auto_delete(forwarded_msg, 60, context, notify=True))
        asyncio.create_task(auto_delete(user_msg, 10))
        
    except ValueError:
        reply = await update.message.reply_text(
            '<b>"Eng: Please enter a valid number.\n'
            'Uzbek: Iltimos, to\'g\'ri raqam kiriting."</b>',
            parse_mode='HTML'
        )
        asyncio.create_task(auto_delete(reply, 10))
        asyncio.create_task(auto_delete(update.message, 10))
    except Exception as e:
        logger.error(f"Error: {e}")
        reply = await update.message.reply_text(
            '<b>"Eng: File not found or invalid number.\n'
            'Uzbek: Fayl topilmadi yoki noto‘g‘ri raqam."</b>',
            parse_mode='HTML'
        )
        asyncio.create_task(auto_delete(reply, 10))
        asyncio.create_task(auto_delete(update.message, 10))

# ================== MAIN FUNCTION ==================
def main():
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+$'), handle_number))
    
    application.run_polling()

if __name__ == "__main__":
    main()
