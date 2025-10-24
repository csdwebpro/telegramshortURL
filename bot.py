from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
updater = Updater("8399630958:AAER8YaRRyimVstfa0N-5RsPR57XEi_hOZU", use_context=True)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the URL Shortener Bot! Use /shorten <url> to shorten a URL.')

def shorten(update: Update, context: CallbackContext) -> None:
    if context.args:
        long_url = context.args[0]
        # Here we use the API you provided for shortening
        api_url = f"http://ouo.io/api/JIx6qdJt?s={long_url}"
        response = requests.get(api_url)
        if response.status_code == 200:
            short_url = response.text.strip()
            update.message.reply_text(f'Shortened URL: {short_url}')
        else:
            update.message.reply_text('Failed to shorten URL. Please try again later.')
    else:
        update.message.reply_text('Please provide a URL to shorten. Example: /shorten https://example.com')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('shorten', shorten))

updater.start_polling()
updater.idle()
