import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

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

async def analyze_word(word: str) -> str:
    """Fetch word analysis from Lingsoft service"""
    try:
        url = f"http://www2.lingsoft.fi/cgi-bin/fintwol?word={quote(word)}"
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        pre_tag = soup.find('pre')
        
        if pre_tag:
            return pre_tag.text.strip()
        return "No analysis found"
    except Exception as e:
        logging.error(f"Error analyzing word: {e}")
        return "Sorry, there was an error analyzing the word"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all incoming messages."""
    message_text = update.message.text.lower()
    
    # Check for basic greetings first
    if message_text in ['hello', 'hi']:
        response = "Hello! Send me any Finnish word to analyze it!"
    elif message_text == 'how are you':
        response = "I'm doing great! Send me a word to analyze!"
    elif message_text == 'bye':
        response = "Goodbye! Have a great day! 👋"
    else:
        # Analyze the word
        await update.message.reply_text(f"Analyzing word: {message_text}...")
        analysis = await analyze_word(message_text)
        response = f"Analysis for '{message_text}':\n\n{analysis}"

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
