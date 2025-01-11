import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import sqlite3
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()

# Get token from environment variable
TOKEN = os.getenv('BOT_TOKEN')
ERROR_MESSAGE = os.getenv('ERROR_MESSAGE')

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

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS word_analyses (
            word TEXT PRIMARY KEY,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def get_word_from_db(word: str) -> str | None:
    """Get word analysis from database"""
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('SELECT analysis FROM word_analyses WHERE word = ?', (word,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

async def save_word_to_db(word: str, analysis: str):
    """Save word analysis to database"""
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO word_analyses (word, analysis) VALUES (?, ?)',
        (word, analysis)
    )
    conn.commit()
    conn.close()

async def analyze_word(word: str) -> str:
    """Fetch word analysis from DB or Lingsoft service"""
    # First try to get from DB
    cached_analysis = await get_word_from_db(word)
    if cached_analysis:
        logging.info(f"Found analysis for '{word}' in cache")
        return cached_analysis

    # If not in DB, fetch from service
    try:
        # Custom encoding for Finnish characters
        encoded_word = word.replace('ä', '%E4').replace('ö', '%F6').replace('å', '%E5')
        url = f"http://www2.lingsoft.fi/cgi-bin/fintwol?word={encoded_word}"
        logging.info(f"Fetching data from '{url}'")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        pre_tag = soup.find('pre')
        
        if pre_tag:
            analysis = pre_tag.text.strip()
            # Save to DB before returning
            await save_word_to_db(word, analysis)
            return analysis
        return ERROR_MESSAGE or "Something is wrong. Please try again later."
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
        # Split message into unique words
        words = list(dict.fromkeys(message_text.split()))
        if len(words) > 1:
            await update.message.reply_text(f"Analyzing {len(words)} unique words...")
            analyses = []
            for word in words:
                analysis = await analyze_word(word)
                analyses.append(f"Analysis for '{word}':\n{analysis}\n")
            response = "\n".join(analyses)
        else:
            # Single word analysis
            word = words[0]  # Use the first (and only) word
            await update.message.reply_text(f"Analyzing word: {word}...")
            analysis = await analyze_word(word)
            response = f"Analysis for '{word}':\n\n{analysis}"

    await update.message.reply_text(response)

def main():
    """Start the bot."""
    # Initialize the database
    init_db()
    
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
