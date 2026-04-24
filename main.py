import os
import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8711059649:AAF7ysdDRw3rbWo9INoHvekeSCwy49QYhWE"
MINI_APP_URL = "https://curious-kitsune-70d212.netlify.app"

# ТВОЙ FILE_ID
IMAGE_FILE_ID = "file:///C:/Users/%D0%9C%D0%B0%D0%BA%D1%81/Downloads/Telegram%20Desktop/photo_2026-04-24_22-49-32.jpg"

bot = TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

ADMIN_ID = 854916968

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=MINI_APP_URL)
    button = InlineKeyboardButton(
        text="🚀 СТАРТ",
        web_app=web_app,
        style="success"
    )
    keyboard.add(button)
    
    # Отправляем картинку СРАЗУ, без проверок
    bot.send_photo(
        message.chat.id,
        photo=IMAGE_FILE_ID,
        caption="Привет! Нажмите на кнопку ниже, чтобы открыть JAMPER SIGNAL:",
        reply_markup=keyboard
    )

# Только админ может получать file_id
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    photo = message.photo[-1]
    new_file_id = photo.file_id
    bot.reply_to(
        message,
        f"✅ New file_id (admin only):\n`{new_file_id}`",
        parse_mode="Markdown"
    )

# Блокировка остальных медиа
@bot.message_handler(content_types=['video', 'document', 'audio', 'voice', 'animation'])
def block_media(message):
    if message.from_user.id != ADMIN_ID: 
        bot.reply_to(message, "❌ Access denied.")

bot.infinity_polling()
