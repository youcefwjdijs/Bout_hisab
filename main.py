import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("8016457580:AAESe8slQYSMz1dQwmXFpkUS7mZmQswYd7k")

# ✅ بيانات شهادة التعليم المتوسط BEM
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

# تخزين مؤقت لبيانات المستخدمين
user_bem_data = {}
user_term_data = {}
user_year_data = {}

# ✅ واجهة البداية
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📘 حساب معدل مادة", callback_data="subject_moy"),
        InlineKeyboardButton("🎓 حساب معدل شهادة التعليم المتوسط", callback_data="bem_calc")
    )
    markup.row(
        InlineKeyboardButton("📅 حساب معدل فصلي", callback_data="term_calc"),
        InlineKeyboardButton("📆 حساب معدل العام", callback_data="year_calc")
    )
    bot.send_message(
        message.chat.id,
        "👋 مرحبًا بك في بوت حساب المعدلات 🇩🇿\n"
        "تم تطوير هذا البوت بواسطة: *يوسف قيبوج*\n\n"
        "👇 اختر نوع الحساب:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ✅ التحكم في الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    chat_id = call.message.chat.id
    if call.data == "subject_moy":
        bot.send_message(chat_id, "📚 أدخل علامة الفرض:")
        bot.register_next_step_handler(call.message, get_devoir)
    elif call.data == "bem_calc":
        user_bem_data[chat_id] = {"marks": [], "step": 0}
        subject_name, _ = subjects[0]
        bot.send_message(chat_id, f"✍️ أدخل علامة {subject_name}:")
    elif call.data == "term_calc":
        bot.send_message(chat_id, "📌 كم عدد المواد في هذا الفصل؟")
        bot.register_next_step_handler(call.message, get_term_subject_count)
    elif call.data == "year_calc":
        user_year_data[chat_id] = {"marks": [], "step": 1}
        bot.send_message(chat_id, "📅 أدخل معدل الفصل الأول:")

# ✅ حساب معدل مادة
def get_devoir(message):
    try:
        devoir = float(message.text)
        bot.send_message(message.chat.id, "🟨 أدخل علامة التقويم:")
        bot.register_next_step_handler(message, get_eval, devoir)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صحيحًا.")

def get_eval(message, devoir):
    try:
        eval_ = float(message.text)
        bot.send_message(message.chat.id, "📝 أدخل علامة الإختبار:")
        bot.register_next_step_handler(message, get_exam, devoir, eval_)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صحيحًا.")

def get_exam(message, devoir, eval_):
    try:
        exam = float(message.text)
        bot.send_message(message.chat.id, "⚖️ أدخل المعامل:")
        bot.register_next_step_handler(message, calc_subject_moy, devoir, eval_, exam)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صحيحًا.")

def calc_subject_moy(message, devoir, eval_, exam):
    try:
        coef = float(message.text)
        moyenne = ((((devoir + eval_) / 2) + (exam * 2)) / 3) * coef
        moyenne = round(moyenne, 2)
        bot.send_message(message.chat.id, f"✅ معدل المادة (مع المعامل): {moyenne}")
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صحيحًا.")

# ✅ حساب معدل BEM
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
        bot.send_message(chat_id, "❌ أدخل رقمًا صحيحًا.")

# ✅ حساب معدل فصلي
def get_term_subject_count(message):
    try:
        count = int(message.text)
        user_term_data[message.chat.id] = {"count": count, "step": 0, "notes": [], "coefs": []}
        bot.send_message(message.chat.id, f"✏️ أدخل علامة المادة رقم 1:")
        bot.register_next_step_handler(message, get_term_note)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صحيحًا.")

def get_term_note(message):
    try:
        note = float(message.text)
        user_term_data[message.chat.id]["notes"].append(note)
        bot.send_message(message.chat.id, f"⚖️ أدخل المعامل:")
        bot.register_next_step_handler(message, get_term_coef)
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

def get_term_coef(message):
    try:
        coef = float(message.text)
        data = user_term_data[message.chat.id]
        data["coefs"].append(coef)
        data["step"] += 1
        if data["step"] < data["count"]:
            bot.send_message(message.chat.id, f"✏️ أدخل علامة المادة رقم {data['step']+1}:")
            bot.register_next_step_handler(message, get_term_note)
        else:
            total = sum(n * c for n, c in zip(data["notes"], data["coefs"]))
            coef_total = sum(data["coefs"])
            result = round(total / coef_total, 2)
            bot.send_message(message.chat.id, f"📅 معدل الفصل هو: {result}")
            del user_term_data[message.chat.id]
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

# ✅ حساب معدل السنة
@bot.message_handler(func=lambda message: message.chat.id in user_year_data)
def get_year_moy(message):
    try:
        moy = float(message.text)
        data = user_year_data[message.chat.id]
        data["marks"].append(moy)
        data["step"] += 1

        if data["step"] <= 3:
            bot.send_message(message.chat.id, f"📅 أدخل معدل الفصل {data['step']}:")
        else:
            result = round(sum(data["marks"]) / 3, 2)
            bot.send_message(message.chat.id, f"📆 معدل السنة هو: {result}")
            del user_year_data[message.chat.id]
    except:
        bot.send_message(message.chat.id, "❌ أدخل رقمًا صالحًا.")

# ✅ تشغيل البوت
bot.polling()
