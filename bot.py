import os
import logging
import re
from typing import Optional, Dict, List
from urllib.parse import urlparse

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class URLShortenerBot:
    def __init__(self, token: str):
        self.token = token
        self.ouo_api_url = "http://ouo.io/api/JIx6qdJt?s="
        self.user_stats = {}  # Store user statistics
        
    def is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def shorten_url(self, long_url: str) -> Optional[str]:
        """Shorten URL using OUO.io API"""
        try:
            # Clean and validate URL
            if not long_url.startswith(('http://', 'https://')):
                long_url = 'https://' + long_url
            
            if not self.is_valid_url(long_url):
                return None
            
            # Make API request
            api_url = f"{self.ouo_api_url}{long_url}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                shortened_url = response.text.strip()
                # Validate the shortened URL
                if self.is_valid_url(shortened_url):
                    return shortened_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error shortening URL: {e}")
            return None
    
    def update_user_stats(self, user_id: int):
        """Update user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {'urls_shortened': 0}
        self.user_stats[user_id]['urls_shortened'] += 1
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        return self.user_stats.get(user_id, {'urls_shortened': 0})

# Initialize bot with your token
BOT_TOKEN = "8239963008:AAFm8PU6N_432qAsz_v1yK4EgDL3_YP0xmA"
bot = URLShortenerBot(BOT_TOKEN)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when the command /start is issued."""
    user = update.effective_user
    welcome_text = f"""
👋 Welcome {user.first_name} to Advanced URL Shortener Bot!

🤖 *Bot Features:*
• 🔗 Shorten any long URL instantly
• 📊 Track your shortening statistics
• ⚡ Fast and reliable service
• 🔒 Secure URL shortening

📝 *How to use:*
1. Send me any long URL
2. I'll shorten it using OUO.io
3. Get your shortened URL instantly

💡 *Commands:*
/start - Show this welcome message
/help - Get help and instructions
/stats - Check your shortening statistics
/about - About this bot

Send me a URL to get started! 🚀
    """
    
    keyboard = [
        [InlineKeyboardButton("📖 Help", callback_data="help"),
         InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message when the command /help is issued."""
    help_text = """
🆘 *Help Guide*

📝 *How to Shorten URLs:*
Simply send me any long URL and I'll shorten it for you!

🌐 *Supported URL formats:*
• http://example.com
• https://example.com/path
• example.com (I'll add https:// automatically)

⚡ *Example URLs:*
• https://www.google.com/search?q=telegram+bot
• youtube.com/watch?v=example
• amazon.com/dp/product_id

📊 *Check Your Stats:*
Use /stats to see how many URLs you've shortened

🔧 *Need Help?*
If you encounter any issues, make sure your URL is valid and accessible.

Happy shortening! 🎉
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    user_id = update.effective_user.id
    stats = bot.get_user_stats(user_id)
    
    stats_text = f"""
📊 *Your Statistics*

🔗 URLs Shortened: *{stats['urls_shortened']}*
👤 User ID: `{user_id}`

Keep shortening! The more you use, the more you save! 💪
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about information."""
    about_text = """
🤖 *Advanced URL Shortener Bot*

*Version:* 2.0
*Service:* OUO.io URL Shortener
*Developer:* Advanced Bot Team

🌟 *Features:*
• Lightning-fast URL shortening
• User statistics tracking
• Easy-to-use interface
• Support for all types of URLs

📡 *API:* OUO.io URL Shortener
🔧 *Built with:* Python + python-telegram-bot

Thank you for using our bot! ❤️
    """
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and shorten URLs."""
    message_text = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Check if the message contains a URL
    url_pattern = r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*'
    urls_found = re.findall(url_pattern, message_text)
    
    if not urls_found:
        await update.message.reply_text(
            "❌ Please send a valid URL to shorten.\n"
            "Use /help for instructions."
        )
        return
    
    # Process each found URL
    for url in urls_found:
        # Show typing action
        await update.message.chat.send_action(action="typing")
        
        # Shorten the URL
        shortened_url = bot.shorten_url(url)
        
        if shortened_url:
            # Update user statistics
            bot.update_user_stats(user_id)
            
            # Create response with nice formatting
            response_text = f"""
✅ *URL Shortened Successfully!*

🔗 *Original URL:*
`{url}`

➡️ *Shortened URL:*
`{shortened_url}`

📊 *Your total shortened URLs:* {bot.get_user_stats(user_id)['urls_shortened']}

💡 *Tip:* Click the URL above to copy it!
            """
            
            # Create inline keyboard with actions
            keyboard = [
                [InlineKeyboardButton("🌐 Open Short URL", url=shortened_url)],
                [InlineKeyboardButton("📊 Check Stats", callback_data="stats"),
                 InlineKeyboardButton("🔗 Shorten Another", callback_data="shorten_another")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            error_text = f"""
❌ *Failed to shorten URL*

🔗 *URL:* `{url}`

⚠️ *Possible reasons:*
• Invalid URL format
• URL is not accessible
• Service temporarily unavailable

💡 *Try:*
• Make sure the URL starts with http:// or https://
• Check if the URL is valid and accessible
• Try again in a few moments

Use /help for more guidance.
            """
            await update.message.reply_text(error_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "help":
        help_text = """
🆘 *Quick Help*

Just send me any URL to shorten it!
I support all common URL formats.

Need more help? Use /help for detailed instructions.
        """
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif query.data == "stats":
        stats = bot.get_user_stats(user_id)
        stats_text = f"📊 Your Stats:\n🔗 URLs Shortened: {stats['urls_shortened']}"
        await query.edit_message_text(stats_text)
    
    elif query.data == "about":
        about_text = "🤖 Advanced URL Shortener Bot v2.0\nUsing OUO.io API"
        await query.edit_message_text(about_text)
    
    elif query.data == "shorten_another":
        await query.edit_message_text("🔗 Send me another URL to shorten!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and send a friendly message."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Send a friendly error message
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Sorry, something went wrong. Please try again later."
        )

def main():
    """Start the bot."""
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("🤖 Bot is running...")
    print("Press Ctrl+C to stop")
    
    # Run the bot until you press Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
