import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ توكن البوت الخاص بك
bot = telebot.TeleBot("8016457580:AAESe8slQYSMz1dQwmXFpkUS7mZmQswYd7k")

# ✅ قائمة المواد والمعاملات المحدثة لـ BEM
subjects = [
    ("اللغة العربية", 5),
    ("الرياضيات", 4),
    ("اللغة الفرنسية", 3),
    ("اللغة الإنجليزية", 2),
    ("الاجتماعيات", 3),
    ("التربية الإسلامية", 2),
    ("التربية المدنية", 1),
    ("العلوم الطبيعية", 2),
    ("العلوم الفيزيائية", 2),
    ("التربية البدنية", 1)
]

# 📦 تخزين بيانات المستخدم لحساب معدل الشهادة
user_bem_data = {}

# 🔘 أمر /start - ترحيب وزرين
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📘 حساب معدل مادة", callback_data="subject_moy"),
        InlineKeyboardButton("🎓 حساب معدل شهادة التعليم المتوسط", callback_data="bem_calc")
    )
    bot.send_message(
        message.chat.id,
        "👋 مرحبًا بك في بوت حساب المعدلات 🇩🇿\n"
        "تم تطوير هذا البوت بواسطة: *يوسف قيبوج*\n\n"
        "👇 اختر نوع الحساب:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 🔘 التحكم في الزرين
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "subject_moy":
        bot.send_message(call.message.chat.id, "📚 أدخل علامة الفرض:")
        bot.register_next_step_handler(call.message, get_devoir)
    elif call.data == "bem_calc":
        user_bem_data[call.message.chat.id] = {"marks": [], "step": 0}
        subject_name, _ = subjects[0]
        bot.send_message(call.message.chat.id, f"✍️ أدخل علامة {subject_name}:")

# ✅ حساب معدل مادة (العلاقة الخاصة)
def get_devoir(message):
    try:
        devoir = float(message.text)
        bot.send_message(message.chat.id, "🟨 أدخل علامة التقويم:")
        bot.register_next_step_handler(message, get_eval, devoir)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

def get_eval(message, devoir):
    try:
        eval_ = float(message.text)
        bot.send_message(message.chat.id, "📝 أدخل علامة الإختبار:")
        bot.register_next_step_handler(message, get_exam, devoir, eval_)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

def get_exam(message, devoir, eval_):
    try:
        exam = float(message.text)
        bot.send_message(message.chat.id, "⚖️ أدخل المعامل:")
        bot.register_next_step_handler(message, calc_subject_moy, devoir, eval_, exam)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

def calc_subject_moy(message, devoir, eval_, exam):
    try:
        coef = float(message.text)
        moyenne = ((((devoir + eval_) / 2) + (exam * 2)) / 3) * coef
        moyenne = round(moyenne, 2)
        bot.send_message(message.chat.id, f"✅ معدل المادة (مع المعامل): {moyenne}")
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

# ✅ حساب معدل شهادة التعليم المتوسط (BEM)
@bot.message_handler(func=lambda message: message.chat.id in user_bem_data)
def get_bem_marks(message):
    chat_id = message.chat.id
    try:
        mark = float(message.text)
        step = user_bem_data[chat_id]["step"]
        user_bem_data[chat_id]["marks"].append(mark)
        user_bem_data[chat_id]["step"] += 1

        if user_bem_data[chat_id]["step"] < len(subjects):
            next_subject, _ = subjects[user_bem_data[chat_id]["step"]]
            bot.send_message(chat_id, f"✍️ أدخل علامة {next_subject}:")
        else:
            total = 0
            total_coef = 0
            details = "📄 التفاصيل:\n"
            for i, (subj, coef) in enumerate(subjects):
                val = user_bem_data[chat_id]["marks"][i]
                details += f"• {subj}: {val} × {coef} = {val*coef}\n"
                total += val * coef
                total_coef += coef
            bem_avg = round(total / total_coef, 2)
            details += f"\n🎓 *معدل شهادة التعليم المتوسط* = *{bem_avg}*"
            bot.send_message(chat_id, details, parse_mode="Markdown")
            del user_bem_data[chat_id]
    except:
        bot.send_message(chat_id, "❌ أدخل رقمًا صالحًا.")

# 🚀 تشغيل البوت
bot.polling()