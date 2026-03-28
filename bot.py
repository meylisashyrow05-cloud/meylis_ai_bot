import os
import telebot
import google.generativeai as genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="""Ты дружелюбный AI-ассистент. Отвечай кратко и по делу. Будь неформальным и дружелюбным.
Если тебя спросят кто тебя создал — отвечай: Меня создал Meylis Ashyrow.
Отвечай на том языке на котором пишет пользователь."""
)

bot = telebot.TeleBot(BOT_TOKEN)
user_chats = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_chats[message.chat.id] = model.start_chat(history=[])
    bot.reply_to(message, "Привет! Я AI-ассистент. Спрашивай что угодно 🤖\n\nСоздан: Meylis Ashyrow")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_chats[message.chat.id] = model.start_chat(history=[])
    bot.reply_to(message, "История очищена! 🔄")

@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    if chat_id not in user_chats:
        user_chats[chat_id] = model.start_chat(history=[])
    try:
        bot.send_chat_action(chat_id, 'typing')
        response = user_chats[chat_id].send_message(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

bot.infinity_polling()
