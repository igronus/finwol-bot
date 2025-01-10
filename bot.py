import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()

# Get token from environment variable
TOKEN = os.getenv('BOT_TOKEN')

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f'Hi {user.first_name}! 👋\nI am your friendly bot. How can I help you today?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
Here are the available commands:
/start - Start the bot
/help - Show this help message
Just send any message and I'll respond!
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all incoming messages."""
    message_text = update.message.text.lower()
    
    # Simple response logic
    if 'hello' in message_text or 'hi' in message_text:
        response = "Hello! How are you?"
    elif 'how are you' in message_text:
        response = "I'm doing great, thanks for asking! How about you?"
    elif 'bye' in message_text:
        response = "Goodbye! Have a great day! 👋"
    else:
        response = "I received your message: " + update.message.text

    await update.message.reply_text(response)

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
