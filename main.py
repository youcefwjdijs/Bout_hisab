import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("8016457580:AAESe8slQYSMz1dQwmXFpkUS7mZmQswYd7k")

# ✅ قائمة المواد
main_subjects = [
    "اللغة العربية",
    "اللغة الفرنسية",
    "الرياضيات",
    "اللغة الإنجليزية",
    "العلوم الطبيعية",
    "العلوم الفيزيائية",
    "التربية المدنية",
    "التربية الإسلامية",
    "الاجتماعيات",
    "التربية البدنية"
]

optional_subjects = [
    "الموسيقى",
    "الإعلام الآلي"
]

user_term_data = {}
user_year_data = {}

# ✅ أمر البدء
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📅 حساب معدل الفصل", callback_data="term_calc"),
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

# ✅ زر معدل العام
@bot.callback_query_handler(func=lambda call: call.data == "year_calc")
def handle_year_calc(call):
    chat_id = call.message.chat.id
    user_year_data[chat_id] = {"marks": [], "step": 1}
    bot.send_message(chat_id, "📅 أدخل معدل الفصل 1:")
    bot.register_next_step_handler(call.message, get_year_moy)

def get_year_moy(message):
    chat_id = message.chat.id
    try:
        mark = float(message.text.replace(',', '.'))
        if mark > 20:
            raise Exception("أعلى قيمة هي 20")
        data = user_year_data[chat_id]
        data["marks"].append(mark)
        data["step"] += 1

        if data["step"] <= 3:
            bot.send_message(chat_id, f"📅 أدخل معدل الفصل {data['step']}:")
            bot.register_next_step_handler(message, get_year_moy)
        else:
            avg = round(sum(data["marks"]) / 3, 2)
            bot.send_message(chat_id, f"✅ معدل السنة هو: {avg}")
            del user_year_data[chat_id]
    except:
        bot.send_message(chat_id, "❌ أدخل رقمًا صالحًا (أقل من أو يساوي 20).")
        bot.register_next_step_handler(message, get_year_moy)

# ✅ زر معدل الفصل
@bot.callback_query_handler(func=lambda call: call.data == "term_calc")
def handle_term_calc(call):
    chat_id = call.message.chat.id
    user_term_data[chat_id] = {
        "subject_index": 0,
        "subjects": main_subjects.copy(),
        "results": [],
        "coefs": [],
        "details": [],
        "optional_stage": 0
    }
    ask_for_mark(chat_id)

def ask_for_mark(chat_id):
    data = user_term_data[chat_id]
    if data["subject_index"] < len(data["subjects"]):
        subject = data["subjects"][data["subject_index"]]
        bot.send_message(chat_id, f"📚 أدخل القيم لمادة *{subject}* بهذا الشكل:\nفرض/تقويم/اختبار/معامل", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(chat_id, process_mark)
    else:
        ask_optional_subject(chat_id)

def process_mark(message):
    chat_id = message.chat.id
    data = user_term_data[chat_id]
    try:
        parts = message.text.replace(',', '.').strip().split('/')
        if len(parts) != 4:
            raise Exception("تنسيق غير صحيح")

        devoir, eval_, exam, coef = map(float, parts)
        if any(x > 20 for x in [devoir, eval_, exam]) or coef > 20:
            raise Exception("القيم لا يجب أن تتجاوز 20")

        moyenne_simple = (((devoir + eval_) / 2) + (exam * 2)) / 3
        moyenne = round(moyenne_simple * coef, 2)

        data["results"].append(moyenne)
        data["coefs"].append(coef)
        subject = data["subjects"][data["subject_index"]]
        data["details"].append(
            f"• {subject}: ((({devoir}+{eval_})/2 + {exam}×2)/3) × {coef} = {moyenne}"
        )
        data["subject_index"] += 1
        ask_for_mark(chat_id)
    except:
        bot.send_message(chat_id, "❌ أدخل القيم بشكل صحيح (أرقام لا تتجاوز 20): 12.5/14.25/15/4")
        bot.register_next_step_handler(message, process_mark)

def ask_optional_subject(chat_id):
    data = user_term_data[chat_id]
    if data["optional_stage"] == 0:
        bot.send_message(chat_id, "🎵 هل تريد إدخال علامة *الموسيقى*؟ (نعم/لا)", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_optional_response)
    elif data["optional_stage"] == 1:
        bot.send_message(chat_id, "💻 هل تريد إدخال علامة *الإعلام الآلي*؟ (نعم/لا)", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_optional_response)
    else:
        show_term_result(chat_id)

def handle_optional_response(message):
    chat_id = message.chat.id
    response = message.text.strip().lower()
    data = user_term_data[chat_id]

    if response == "نعم":
        data["subjects"].append(optional_subjects[data["optional_stage"]])
        ask_for_mark(chat_id)
    else:
        data["optional_stage"] += 1
        ask_optional_subject(chat_id)

def show_term_result(chat_id):
    data = user_term_data[chat_id]
    total = sum(data["results"])
    total_coef = sum(data["coefs"])
    final_avg = round(total / total_coef, 2)

    result_text = "📄 التفاصيل:\n"
    result_text += "\n".join(data["details"])
    result_text += f"\n\n🧮 مجموع (معدل × معامل) = {round(total, 2)}"
    result_text += f"\n⚖️ مجموع المعاملات = {total_coef}"
    result_text += f"\n\n✅ معدل الفصل = {final_avg}"

    bot.send_message(chat_id, result_text)
    del user_term_data[chat_id]

# ✅ تشغيل البوت
bot.polling()
