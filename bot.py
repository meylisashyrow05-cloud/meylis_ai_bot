import os
import telebot
import google.generativeai as genai
import time

# --- НАСТРОЙКИ ---
# Убедись, что эти переменные заданы в Termux через: export BOT_TOKEN="твой_токен"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Конфигурация Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="""Ты дружелюбный AI-ассистент. Отвечай кратко и по делу. Будь неформальным и дружелюбным.
Если тебя спросят кто тебя создал — отвечай: Меня создал Meylis Ashyrow.
Отвечай на том языке, на котором пишет пользователь. Используй эмодзи для настроения."""
)

bot = telebot.TeleBot(BOT_TOKEN)
user_chats = {}

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_chats[chat_id] = model.start_chat(history=[])
    bot.reply_to(message, "Йо! Я AI-ассистент на связи. Спрашивай что угодно! 🤖\n\nСоздатель: Meylis Ashyrow")

@bot.message_handler(commands=['reset'])
def reset(message):
    chat_id = message.chat.id
    user_chats[chat_id] = model.start_chat(history=[])
    bot.reply_to(message, "История очищена, начинаем с чистого листа! 🔄")

# --- ОБРАБОТКА СООБЩЕНИЙ ---

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    
    # Если чата еще нет в памяти, создаем его
    if chat_id not in user_chats:
        user_chats[chat_id] = model.start_chat(history=[])
    
    try:
        # Показываем, что бот "печатает"
        bot.send_chat_action(chat_id, 'typing')
        
        # Отправляем запрос в Gemini
        response = user_chats[chat_id].send_message(message.text)
        
        # Проверяем, есть ли текст в ответе
        if response and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "Хмм, чет я призадумался... Попробуй спросить по-другому. 🤔")
            
    except Exception as e:
        error_text = str(e)
        
        # Обработка лимитов (ошибка 429)
        if "429" in error_text:
            bot.reply_to(message, "Нигга, притормози! 🛑 Слишком много вопросов сразу. Подожди 20-30 секунд и напиши снова.")
        
        # Обработка блокировки контента (безопасность Google)
        elif "finish_reason" in error_text or "safety" in error_text:
            bot.reply_to(message, "Бро, на такие темы я общаться не могу по правилам безопасности. Давай сменим тему? 🤐")
            
        # Все остальные ошибки
        else:
            bot.reply_to(message, f"Случился какой-то баг, нигга. Вот лог: {error_text[:100]}...")
            print(f"Error: {e}")

# Запуск бота
print("Бот Meylis Ashyrow запущен! 🚀")
bot.infinity_polling()
