import os
import telebot
import anthropic

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ты дружелюбный AI-ассистент. Отвечай кратко и по делу. Будь неформальным и дружелюбным.
Если тебя спросят кто тебя создал, сделал или разработал — всегда отвечай: "Меня создал Meylis Ashyrow".
Отвечай на том языке на котором пишет пользователь."""

user_histories = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_histories[message.chat.id] = []
    bot.reply_to(message, "Привет! Я AI-ассистент. Спрашивай что угодно 🤖\n\nСоздан: Meylis Ashyrow")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_histories[message.chat.id] = []
    bot.reply_to(message, "История очищена! Начнём заново 🔄")

@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    if chat_id not in user_histories:
        user_histories[chat_id] = []

    user_histories[chat_id].append({
        "role": "user",
        "content": message.text
    })

    if len(user_histories[chat_id]) > 20:
        user_histories[chat_id] = user_histories[chat_id][-20:]

    try:
        bot.send_chat_action(chat_id, 'typing')
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=user_histories[chat_id]
        )
        reply = response.content[0].text
        user_histories[chat_id].append({
            "role": "assistant",
            "content": reply
        })
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

bot.infinity_polling()
