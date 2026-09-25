import os, json
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, ContextTypes, filters
from db import SessionLocal, Booking

BOT_TOKEN = os.environ["BOT_TOKEN"]
IRCTC_URL = "https://www.irctc.co.in/nget/train-search"
SOURCE, DESTINATION, DATE, QUOTA, CLASS, TRAIN, BOARDING, PASSENGER_NAME, PASSENGER_AGE, PASSENGER_GENDER, PASSENGER_BERTH, CONFIRM = range(12)

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚆 New Tatkal Booking", callback_data="new")],
        [InlineKeyboardButton("📋 My Bookings", callback_data="bookings")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🚆 Tatkal Ticket Assistant\n\n"
        "मैं booking details collect करके manual IRCTC booking के लिए तैयार करता हूँ।\n"
        "CAPTCHA और final payment आपके control में रहेंगे।", reply_markup=menu()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("❌ Booking cancelled.", reply_markup=menu())
    return ConversationHandler.END

async def new_booking(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data.clear()
    await q.message.reply_text("1/10 🚉 Source station/code भेजें:")
    return SOURCE

async def source(update, context):
    context.user_data["source"] = update.message.text.strip().upper()
    await update.message.reply_text("2/10 🏁 Destination station/code भेजें:")
    return DESTINATION

async def destination(update, context):
    context.user_data["destination"] = update.message.text.strip().upper()
    await update.message.reply_text("3/10 📅 Travel date भेजें (DD/MM/YYYY):")
    return DATE

async def travel_date(update, context):
    value = update.message.text.strip()
    try:
        datetime.strptime(value, "%d/%m/%Y")
    except ValueError:
        await update.message.reply_text("❌ Format गलत है. उदाहरण: 15/10/2026")
        return DATE
    context.user_data["travel_date"] = value
    kb = [[InlineKeyboardButton("Tatkal", callback_data="quota:Tatkal"), InlineKeyboardButton("Premium Tatkal", callback_data="quota:Premium Tatkal")]]
    await update.message.reply_text("4/10 🎫 Quota चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    return QUOTA

async def quota(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["quota"] = q.data.split(":", 1)[1]
    kb = [[InlineKeyboardButton(x, callback_data=f"class:{x}") for x in ["1A", "2A", "3A"]],
          [InlineKeyboardButton(x, callback_data=f"class:{x}") for x in ["SL", "CC", "EC"]]]
    await q.message.reply_text("5/10 💺 Class चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    return CLASS

async def travel_class(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["travel_class"] = q.data.split(":", 1)[1]
    await q.message.reply_text("6/10 🚆 Train number (optional) भेजें, या SKIP लिखें:")
    return TRAIN

async def train(update, context):
    value = update.message.text.strip()
    context.user_data["train_no"] = None if value.upper() == "SKIP" else value
    await update.message.reply_text("7/10 🚉 Boarding station (optional) भेजें, या SKIP लिखें:")
    return BOARDING

async def boarding(update, context):
    value = update.message.text.strip()
    context.user_data["boarding_station"] = None if value.upper() == "SKIP" else value.upper()
    context.user_data["passengers"] = []
    await update.message.reply_text("8/10 👤 Passenger 1 का पूरा नाम भेजें:")
    return PASSENGER_NAME

async def passenger_name(update, context):
    context.user_data["p_name"] = update.message.text.strip()
    if len(context.user_data["p_name"]) < 2:
        await update.message.reply_text("नाम सही से भेजें:")
        return PASSENGER_NAME
    await update.message.reply_text("Passenger age भेजें:")
    return PASSENGER_AGE

async def passenger_age(update, context):
    try:
        age = int(update.message.text.strip())
        if not 1 <= age <= 120:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Age 1-120 के बीच भेजें:")
        return PASSENGER_AGE
    context.user_data["p_age"] = age
    kb = [[InlineKeyboardButton("Male", callback_data="gender:Male"), InlineKeyboardButton("Female", callback_data="gender:Female")],
          [InlineKeyboardButton("Other", callback_data="gender:Other")]]
    await update.message.reply_text("Gender चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    return PASSENGER_GENDER

async def passenger_gender(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["p_gender"] = q.data.split(":", 1)[1]
    kb = [[InlineKeyboardButton("No Preference", callback_data="berth:No Preference")],
          [InlineKeyboardButton("Lower", callback_data="berth:Lower"), InlineKeyboardButton("Middle", callback_data="berth:Middle")],
          [InlineKeyboardButton("Upper", callback_data="berth:Upper"), InlineKeyboardButton("Side Lower", callback_data="berth:Side Lower"), InlineKeyboardButton("Side Upper", callback_data="berth:Side Upper")]]
    await q.message.reply_text("Berth preference:", reply_markup=InlineKeyboardMarkup(kb))
    return PASSENGER_BERTH

async def passenger_berth(update, context):
    q = update.callback_query
    await q.answer()
    berth = q.data.split(":", 1)[1]
    context.user_data["passengers"] = [{
        "name": context.user_data["p_name"],
        "age": context.user_data["p_age"],
        "gender": context.user_data["p_gender"],
        "berth": berth
    }]
    await q.message.reply_text("Passenger saved. नीचे Review दबाएँ.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Review Booking", callback_data="review")]]))
    return CONFIRM

async def review(update, context):
    q = update.callback_query
    await q.answer()
    d = context.user_data
    p = d["passengers"][0]
    text = (
        "📋 Booking Review\n\n"
        f"From: {d['source']}\nTo: {d['destination']}\nDate: {d['travel_date']}\n"
        f"Quota: {d['quota']}\nClass: {d['travel_class']}\n"
        f"Train: {d.get('train_no') or 'Any'}\nBoarding: {d.get('boarding_station') or d['source']}\n\n"
        f"Passenger: {p['name']}\nAge: {p['age']}\nGender: {p['gender']}\nBerth: {p['berth']}"
    )
    kb = [[InlineKeyboardButton("✅ Save Booking", callback_data="save"), InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    return CONFIRM

async def save(update, context):
    q = update.callback_query
    await q.answer()
    d = context.user_data
    booking = Booking(
        telegram_id=str(q.from_user.id), username=q.from_user.username,
        source=d["source"], destination=d["destination"], travel_date=d["travel_date"],
        quota=d["quota"], travel_class=d["travel_class"], train_no=d.get("train_no"),
        boarding_station=d.get("boarding_station"), passengers=json.dumps(d["passengers"]),
        status="READY_FOR_MANUAL_BOOKING"
    )
    db = SessionLocal()
    try:
        db.add(booking); db.commit(); db.refresh(booking); bid = booking.id
    finally:
        db.close()
    await q.message.reply_text(
        f"✅ Booking request #{bid} saved.\n\n"
        "अब IRCTC पर यही details भरें। CAPTCHA manually complete करें और payment स्वयं approve करें।\n\n"
        + IRCTC_URL, reply_markup=menu()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def my_bookings(update, context):
    q = update.callback_query
    await q.answer()
    db = SessionLocal()
    try:
        rows = db.query(Booking).filter_by(telegram_id=str(q.from_user.id)).order_by(Booking.id.desc()).limit(10).all()
        if not rows:
            await q.message.reply_text("कोई booking नहीं मिली.", reply_markup=menu()); return
        lines = ["📋 Your Bookings", ""]
        for b in rows:
            lines.append(f"#{b.id} — {b.source} → {b.destination} — {b.travel_date} — {b.status}")
        await q.message.reply_text("\n".join(lines), reply_markup=menu())
    finally:
        db.close()

async def help_cmd(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(
        "ℹ️ Flow:\n1. Route/date/quota/class\n2. Passenger details\n3. Review & save\n"
        "4. Open IRCTC\n5. CAPTCHA और final payment manually complete करें\n\n"
        "Bot IRCTC password, CAPTCHA answer या payment approval store नहीं करता।", reply_markup=menu()
    )

def build_application():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_booking, pattern="^new$")],
        states={
            SOURCE:[MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
            DESTINATION:[MessageHandler(filters.TEXT & ~filters.COMMAND, destination)],
            DATE:[MessageHandler(filters.TEXT & ~filters.COMMAND, travel_date)],
            QUOTA:[CallbackQueryHandler(quota, pattern="^quota:")],
            CLASS:[CallbackQueryHandler(travel_class, pattern="^class:")],
            TRAIN:[MessageHandler(filters.TEXT & ~filters.COMMAND, train)],
            BOARDING:[MessageHandler(filters.TEXT & ~filters.COMMAND, boarding)],
            PASSENGER_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND, passenger_name)],
            PASSENGER_AGE:[MessageHandler(filters.TEXT & ~filters.COMMAND, passenger_age)],
            PASSENGER_GENDER:[CallbackQueryHandler(passenger_gender, pattern="^gender:")],
            PASSENGER_BERTH:[CallbackQueryHandler(passenger_berth, pattern="^berth:")],
            CONFIRM:[CallbackQueryHandler(review, pattern="^review$"), CallbackQueryHandler(save, pattern="^save$"), CallbackQueryHandler(cancel, pattern="^cancel$")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(my_bookings, pattern="^bookings$"))
    app.add_handler(CallbackQueryHandler(help_cmd, pattern="^help$"))
    return app
