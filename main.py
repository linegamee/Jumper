import os
import json
import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8711059649:AAF7ysdDRw3rbWo9INoHvekeSCwy49QYhWE"
MINI_APP_URL = "https://curious-kitsune-70d212.netlify.app"

bot = TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

ADMIN_ID = 854916968

# Файл для хранения FILE_ID
CONFIG_FILE = 'config.json'

def load_config():
    """Загружает конфигурацию из файла"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'image_file_id': ''}

def save_config(config):
    """Сохраняет конфигурацию в файл"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Загружаем сохраненный FILE_ID
config = load_config()
IMAGE_FILE_ID = config.get('image_file_id', '')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=MINI_APP_URL)
    button = InlineKeyboardButton(
        text="🚀 СТАРТ",
        web_app=web_app
    )
    keyboard.add(button)
    
    # Проверяем, есть ли сохраненное фото
    if IMAGE_FILE_ID:
        try:
            bot.send_photo(
                message.chat.id,
                photo=IMAGE_FILE_ID,
                caption="Привет! Нажмите на кнопку ниже, чтобы открыть JAMPER SIGNAL:",
                reply_markup=keyboard
            )
        except Exception as e:
            # Если фото не найдено, отправляем без фото
            logging.error(f"Ошибка отправки фото: {e}")
            bot.send_message(
                message.chat.id,
                "Привет! Нажми на кнопку ниже, чтобы открыть JAMPER SIGNAL:",
                reply_markup=keyboard
            )
    else:
        # Если фото не установлено, отправляем только текст
        bot.send_message(
            message.chat.id,
            "Привет! Нажми на кнопку ниже, чтобы открыть JAMPER SIGNAL:",
            reply_markup=keyboard
        )

# Команда для админа - показать текущий FILE_ID
@bot.message_handler(commands=['getfileid'])
def get_current_file_id(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    if IMAGE_FILE_ID:
        bot.reply_to(
            message,
            f"📸 *Текущий FILE_ID фото:*\n\n`{IMAGE_FILE_ID}`\n\n"
            f"💡 Чтобы обновить фото, отправь новое фото в этот чат",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(
            message,
            "❌ Фото не установлено.\n"
            "📤 Отправь фото в этот чат, чтобы установить его для приветствия",
            parse_mode="Markdown"
        )

# Только админ может получать и обновлять file_id
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    photo = message.photo[-1]
    new_file_id = photo.file_id
    
    # Сохраняем новый FILE_ID в конфиг
    global IMAGE_FILE_ID
    IMAGE_FILE_ID = new_file_id
    config['image_file_id'] = new_file_id
    save_config(config)
    
    # Отправляем подтверждение
    keyboard = InlineKeyboardMarkup()
    test_button = InlineKeyboardButton(
        text="🔍 ТЕСТИРОВАТЬ (/start)",
        callback_data="test_welcome"
    )
    keyboard.add(test_button)
    
    bot.reply_to(
        message,
        f"✅ *Новое фото сохранено!*\n\n"
        f"📸 FILE_ID:\n`{new_file_id}`\n\n"
        f"👉 Используй /start для теста\n"
        f"👉 Используй /getfileid чтобы посмотреть текущий ID",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    logging.info(f"Admin {message.from_user.id} обновил photo ID: {new_file_id}")

# Обработчик для тестовой кнопки
@bot.callback_query_handler(func=lambda call: call.data == "test_welcome")
def test_welcome(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Access denied")
        return
    
    # Отправляем тестовое сообщение с новым фото
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=MINI_APP_URL)
    button = InlineKeyboardButton(
        text="🚀 СТАРТ",
        web_app=web_app
    )
    keyboard.add(button)
    
    if IMAGE_FILE_ID:
        bot.send_photo(
            call.message.chat.id,
            photo=IMAGE_FILE_ID,
            caption="✅ *ТЕСТОВОЕ СООБЩЕНИЕ*\nПривет! Нажми на кнопку ниже:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "❌ Фото не установлено. Отправь фото для установки.",
            reply_markup=keyboard
        )
    
    bot.answer_callback_query(call.id, "✅ Тестовое сообщение отправлено!")

# Блокировка остальных медиа для не-админов
@bot.message_handler(content_types=['video', 'document', 'audio', 'voice', 'animation'])
def block_media(message):
    if message.from_user.id != ADMIN_ID: 
        bot.reply_to(message, "❌ Access denied.")

print("✅ Бот запущен!")
print("🤖 Команды для админа:")
print("  📤 Отправь фото - обновить приветственное изображение")
print("  /getfileid - показать текущий FILE_ID")
print("  /start - тест приветствия")
bot.infinity_polling()
