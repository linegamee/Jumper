import os
import json
import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8609032177:AAHWc7s7iMBu0LPpJboovAG18g6l0yYdg8I"
MINI_APP_URL = "https://frolicking-arithmetic-a1914b.netlify.app"

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
    # Создаем клавиатуру с кнопкой "НАЧАТЬ" для WebApp
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Кнопка для открытия мини-приложения (WebApp)
    game_button = InlineKeyboardButton(
        text="🎮 НАЧАТЬ ИГРУ",
        web_app=WebAppInfo(url=MINI_APP_URL)  # Открывается как мини-приложение
    )
    keyboard.add(game_button)
    
    # Приветственный текст
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🎮 Добро пожаловать в **JAMPER SIGNAL**!\n\n"
        "🔥 Здесь тебя ждут:\n"
        "• Увлекательные игры\n"
        "• Крутые бонусы\n"
        "• Много веселья\n\n"
        "👇 Нажми на кнопку ниже, чтобы начать!"
    )
    
    # Проверяем, есть ли сохраненное фото
    if IMAGE_FILE_ID:
        try:
            bot.send_photo(
                message.chat.id,
                photo=IMAGE_FILE_ID,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Ошибка отправки фото: {e}")
            bot.send_message(
                message.chat.id,
                welcome_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    else:
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
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
            f"📸 Текущий FILE_ID фото:\n\n`{IMAGE_FILE_ID}`\n\n💡 Чтобы обновить фото, отправь новое фото в этот чат",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(
            message,
            "❌ Фото не установлено.\n📤 Отправь фото в этот чат, чтобы установить его для приветствия"
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
        text="🔍 ПРОВЕРИТЬ (/start)",
        callback_data="test_welcome"
    )
    keyboard.add(test_button)
    
    bot.reply_to(
        message,
        f"✅ Новое фото сохранено!\n\n📸 FILE_ID:\n`{new_file_id}`\n\n👉 Используй /start для проверки\n👉 Используй /getfileid чтобы посмотреть текущий ID",
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
    
    # Отправляем тестовое сообщение как приветствие
    keyboard = InlineKeyboardMarkup(row_width=1)
    game_button = InlineKeyboardButton(
        text="🎮 НАЧАТЬ ИГРУ",
        web_app=WebAppInfo(url=MINI_APP_URL)  # WebApp кнопка
    )
    keyboard.add(game_button)
    
    welcome_text = (
        "✅ *ТЕСТОВОЕ ПРИВЕТСТВИЕ*\n\n"
        "👋 Привет! Добро пожаловать в **JAMPER SIGNAL**!\n\n"
        "👇 Нажми на кнопку ниже, чтобы начать игру!"
    )
    
    if IMAGE_FILE_ID:
        bot.send_photo(
            call.message.chat.id,
            photo=IMAGE_FILE_ID,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            call.message.chat.id,
            welcome_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id, "✅ Тестовое сообщение отправлено!")

# Команда для сброса фото (только админ)
@bot.message_handler(commands=['resetphoto'])
def reset_photo(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Access denied.")
        return
    
    global IMAGE_FILE_ID
    IMAGE_FILE_ID = ''
    config['image_file_id'] = ''
    save_config(config)
    
    bot.reply_to(
        message,
        "✅ Фото приветствия сброшено!\nТеперь будет отправляться только текст."
    )

# Блокировка остальных медиа для не-админов
@bot.message_handler(content_types=['video', 'document', 'audio', 'voice', 'animation'])
def block_media(message):
    if message.from_user.id != ADMIN_ID: 
        bot.reply_to(message, "❌ Access denied.")

# Информация о боте
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🤖 *JAMPER SIGNAL BOT*\n\n"
        "📌 *Доступные команды:*\n"
        "/start - Запустить бота\n"
        "/help - Показать это сообщение\n\n"
        "👑 *Команды администратора:*\n"
        "/getfileid - Показать текущий FILE_ID фото\n"
        "/resetphoto - Сбросить приветственное фото\n\n"
        "📤 *Как установить фото:*\n"
        "1. Отправь фото боту\n"
        "2. Фото автоматически сохранится\n"
        "3. Используй /start для проверки"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

print("=" * 50)
print("✅ Бот JAMPER SIGNAL успешно запущен!")
print("=" * 50)
print(f"🤖 Имя бота: @{bot.get_me().username}")
print(f"👑 Админ ID: {ADMIN_ID}")
print(f"🌐 Mini App URL: {MINI_APP_URL}")
print(f"📸 Фото установлено: {'Да' if IMAGE_FILE_ID else 'Нет'}")
print("=" * 50)
print("📌 Команды для админа:")
print("  📤 Отправь фото - обновить приветственное изображение")
print("  /getfileid - показать текущий FILE_ID")
print("  /resetphoto - сбросить фото")
print("  /start - тест приветствия")
print("=" * 50)

bot.infinity_polling()
