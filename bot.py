import telebot
from telebot import types

# Токен та твій Telegram ID
TOKEN = '7462016871:AAEE67D7obQEiogoFoUXMlOtXK6jVjmzb0U'
ADMIN_ID = 582421023  # твій ID

bot = telebot.TeleBot(TOKEN)
user_data = {}

# /start
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "Привіт! Я бот «Міша може» 🤖\n\nЯ допомагаю зі шкільними та студентськими завданнями.\n\nНатисни /order, щоб залишити замовлення!"
    )

# /order
@bot.message_handler(commands=['order'])
def order(msg):
    chat_id = msg.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "✏️ Введи своє ім’я:")
    bot.register_next_step_handler(msg, get_name)

def get_name(msg):
    chat_id = msg.chat.id
    user_data[chat_id]['name'] = msg.text
    bot.send_message(chat_id, "📚 Що саме потрібно зробити?")
    bot.register_next_step_handler(msg, get_task)

def get_task(msg):
    chat_id = msg.chat.id
    user_data[chat_id]['task'] = msg.text
    bot.send_message(chat_id, "⏳ Коли дедлайн?")
    bot.register_next_step_handler(msg, get_deadline)

def get_deadline(msg):
    chat_id = msg.chat.id
    user_data[chat_id]['deadline'] = msg.text
    bot.send_message(chat_id, "📎 Прикріпи файл або натисни 'Пропустити'")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Пропустити")
    bot.send_message(chat_id, "Надішли файл (фото, PDF, DOC тощо)", reply_markup=markup)
    bot.register_next_step_handler(msg, get_file)

@bot.message_handler(content_types=['document', 'photo'])
def handle_files(msg):
    get_file(msg)  # Перекидаємо до логіки збору

def get_file(msg):
    chat_id = msg.chat.id
    if msg.content_type == 'document':
        file_id = msg.document.file_id
        user_data[chat_id]['file'] = file_id
    elif msg.content_type == 'photo':
        file_id = msg.photo[-1].file_id
        user_data[chat_id]['file'] = file_id
    else:
        user_data[chat_id]['file'] = None

    bot.send_message(chat_id, "📱 Введи контакт (Telegram або номер):")
    bot.register_next_step_handler(msg, get_contact)

def get_contact(msg):
    chat_id = msg.chat.id
    user_data[chat_id]['contact'] = msg.text

    # Перевірка та підтвердження
    data = user_data[chat_id]
    text = (
        f"🔍 Перевір замовлення:\n\n"
        f"👤 Ім’я: {data['name']}\n"
        f"📚 Завдання: {data['task']}\n"
        f"⏳ Дедлайн: {data['deadline']}\n"
        f"📞 Контакт: {data['contact']}\n\n"
        f"✅ Все правильно?"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Так, відправити", callback_data="confirm"))
    markup.add(types.InlineKeyboardButton("❌ Скасувати", callback_data="cancel"))
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "confirm":
        data = user_data.get(chat_id)
        if not data:
            return bot.send_message(chat_id, "⛔ Дані не знайдені.")

        text = (
            f"🆕 НОВЕ ЗАМОВЛЕННЯ\n\n"
            f"👤 Ім’я: {data['name']}\n"
            f"📚 Завдання: {data['task']}\n"
            f"⏳ Дедлайн: {data['deadline']}\n"
            f"📞 Контакт: {data['contact']}"
        )

        # Відправка адміну
        bot.send_message(ADMIN_ID, text)
        if data.get('file'):
            bot.send_document(ADMIN_ID, data['file'])

        bot.send_message(chat_id, "✅ Дякую! Замовлення відправлено.")
        user_data.pop(chat_id, None)  # очищення

    elif call.data == "cancel":
        bot.send_message(chat_id, "🚫 Замовлення скасовано.")
        user_data.pop(chat_id, None)

bot.infinity_polling()
