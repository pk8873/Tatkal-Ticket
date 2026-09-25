import json
import os
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from db import Booking, PassengerProfile, SessionLocal

BOT_TOKEN = os.environ["BOT_TOKEN"]
IRCTC_URL = "https://www.irctc.co.in/nget/train-search"

(
    SOURCE, DESTINATION, DATE, QUOTA, CLASS, TRAIN, BOARDING,
    PASSENGER_NAME, PASSENGER_AGE, PASSENGER_GENDER, PASSENGER_BERTH,
    PASSENGER_MORE, CONFIRM,
) = range(13)


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚆 New Booking", callback_data="new")],
        [InlineKeyboardButton("👤 Passenger Profiles", callback_data="profiles")],
        [InlineKeyboardButton("📋 My Bookings", callback_data="bookings")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ])


def irctc_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open IRCTC & Continue", url=IRCTC_URL)],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="home")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🚆 Railway Booking Assistant\n\n"
        "Normal और Tatkal दोनों के लिए booking details तैयार करें।\n"
        "Bot आपकी details save करेगा और IRCTC पर आगे बढ़ने में मदद करेगा।\n\n"
        "🔐 CAPTCHA, login और final payment हमेशा आपके control में रहेंगे।",
        reply_markup=menu(),
    )


async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🏠 Main Menu", reply_markup=menu())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("❌ Booking cancelled.", reply_markup=menu())
    return ConversationHandler.END


async def new_booking(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data.clear()
    context.user_data["passengers"] = []
    await q.message.reply_text("1/12 🚉 Source station/code भेजें:")
    return SOURCE


async def source(update, context):
    value = update.message.text.strip().upper()
    if len(value) < 2:
        await update.message.reply_text("Valid source station/code भेजें:")
        return SOURCE
    context.user_data["source"] = value
    await update.message.reply_text("2/12 🏁 Destination station/code भेजें:")
    return DESTINATION


async def destination(update, context):
    value = update.message.text.strip().upper()
    if len(value) < 2:
        await update.message.reply_text("Valid destination station/code भेजें:")
        return DESTINATION
    context.user_data["destination"] = value
    await update.message.reply_text("3/12 📅 Travel date भेजें (DD/MM/YYYY):")
    return DATE


async def travel_date(update, context):
    value = update.message.text.strip()
    try:
        dt = datetime.strptime(value, "%d/%m/%Y")
        if dt.date() < datetime.now().date():
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Date गलत है. Future date DD/MM/YYYY में भेजें.")
        return DATE

    context.user_data["travel_date"] = value
    kb = [[
        InlineKeyboardButton("🟢 Normal", callback_data="quota:General"),
        InlineKeyboardButton("🟠 Tatkal", callback_data="quota:Tatkal"),
    ], [
        InlineKeyboardButton("🔵 Premium Tatkal", callback_data="quota:Premium Tatkal"),
    ]]
    await update.message.reply_text("4/12 🎫 Quota चुनें:", reply_markup=InlineKeyboardMarkup(kb))
    return QUOTA


async def quota(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["quota"] = q.data.split(":", 1)[1]

    rows = [
        [InlineKeyboardButton(x, callback_data=f"class:{x}") for x in ["1A", "2A", "3A"]],
        [InlineKeyboardButton(x, callback_data=f"class:{x}") for x in ["SL", "CC", "EC"]],
    ]
    await q.message.reply_text("5/12 💺 Class चुनें:", reply_markup=InlineKeyboardMarkup(rows))
    return CLASS


async def travel_class(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["travel_class"] = q.data.split(":", 1)[1]
    await q.message.reply_text("6/12 🚆 Train number (optional) भेजें, या SKIP लिखें:")
    return TRAIN


async def train(update, context):
    value = update.message.text.strip()
    context.user_data["train_no"] = None if value.upper() == "SKIP" else value
    await update.message.reply_text("7/12 🚉 Boarding station (optional) भेजें, या SKIP लिखें:")
    return BOARDING


async def boarding(update, context):
    value = update.message.text.strip()
    context.user_data["boarding_station"] = None if value.upper() == "SKIP" else value.upper()
    await update.message.reply_text(
        "8/12 👤 Passenger 1 का नाम भेजें.\n"
        "आप बाद में और passengers जोड़ सकते हैं."
    )
    return PASSENGER_NAME


async def passenger_name(update, context):
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("पूरा नाम भेजें:")
        return PASSENGER_NAME
    context.user_data["p_name"] = name
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
    rows = [
        [InlineKeyboardButton("Male", callback_data="gender:Male"),
         InlineKeyboardButton("Female", callback_data="gender:Female")],
        [InlineKeyboardButton("Other", callback_data="gender:Other")],
    ]
    await update.message.reply_text("Gender चुनें:", reply_markup=InlineKeyboardMarkup(rows))
    return PASSENGER_GENDER


async def passenger_gender(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["p_gender"] = q.data.split(":", 1)[1]

    rows = [
        [InlineKeyboardButton("No Preference", callback_data="berth:No Preference")],
        [InlineKeyboardButton("Lower", callback_data="berth:Lower"),
         InlineKeyboardButton("Middle", callback_data="berth:Middle")],
        [InlineKeyboardButton("Upper", callback_data="berth:Upper"),
         InlineKeyboardButton("Side Lower", callback_data="berth:Side Lower"),
         InlineKeyboardButton("Side Upper", callback_data="berth:Side Upper")],
    ]
    await q.message.reply_text("Berth preference:", reply_markup=InlineKeyboardMarkup(rows))
    return PASSENGER_BERTH


async def passenger_berth(update, context):
    q = update.callback_query
    await q.answer()
    berth = q.data.split(":", 1)[1]
    context.user_data["passengers"].append({
        "name": context.user_data["p_name"],
        "age": context.user_data["p_age"],
        "gender": context.user_data["p_gender"],
        "berth": berth,
    })

    rows = [[
        InlineKeyboardButton("➕ Add Passenger", callback_data="passenger:add"),
        InlineKeyboardButton("✅ Review", callback_data="review"),
    ]]
    await q.message.reply_text(
        f"Passenger {len(context.user_data['passengers'])} saved.",
        reply_markup=InlineKeyboardMarkup(rows),
    )
    return PASSENGER_MORE


async def passenger_more(update, context):
    q = update.callback_query
    await q.answer()

    if q.data == "passenger:add":
        if len(context.user_data.get("passengers", [])) >= 6:
            await q.message.reply_text("Maximum 6 passengers per booking.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Review", callback_data="review")]]
            ))
            return PASSENGER_MORE
        n = len(context.user_data["passengers"]) + 1
        await q.message.reply_text(f"Passenger {n} का पूरा नाम भेजें:")
        return PASSENGER_NAME

    return await review(update, context)


def review_text(d):
    lines = [
        "📋 BOOKING REVIEW",
        "",
        f"🚉 {d['source']} → {d['destination']}",
        f"📅 {d['travel_date']}",
        f"🎫 {d['quota']}",
        f"💺 {d['travel_class']}",
        f"🚆 Train: {d.get('train_no') or 'Any'}",
        f"🚉 Boarding: {d.get('boarding_station') or d['source']}",
        "",
        "👥 PASSENGERS",
    ]
    for i, p in enumerate(d["passengers"], 1):
        lines.append(f"{i}. {p['name']} | {p['age']} | {p['gender']} | {p['berth']}")
    return "\n".join(lines)


async def review(update, context):
    q = update.callback_query
    await q.answer()
    text = review_text(context.user_data)
    rows = [
        [InlineKeyboardButton("✅ Save Booking", callback_data="save")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]
    await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows))
    return CONFIRM


async def save(update, context):
    q = update.callback_query
    await q.answer()
    d = context.user_data

    booking = Booking(
        telegram_id=str(q.from_user.id),
        username=q.from_user.username,
        source=d["source"],
        destination=d["destination"],
        travel_date=d["travel_date"],
        quota=d["quota"],
        travel_class=d["travel_class"],
        train_no=d.get("train_no"),
        boarding_station=d.get("boarding_station"),
        passengers=json.dumps(d["passengers"], ensure_ascii=False),
        status="READY_FOR_MANUAL_BOOKING",
    )

    db = SessionLocal()
    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        bid = booking.id
    finally:
        db.close()

    await q.message.reply_text(
        f"✅ Booking #{bid} saved.\n\n"
        "अब नीचे button से IRCTC खोलें। Saved details देखकर form भरें।\n"
        "CAPTCHA, login और final payment आप स्वयं complete करें।",
        reply_markup=irctc_button(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def my_bookings(update, context):
    q = update.callback_query
    await q.answer()
    db = SessionLocal()
    try:
        rows = (
            db.query(Booking)
            .filter_by(telegram_id=str(q.from_user.id))
            .order_by(Booking.id.desc())
            .limit(10)
            .all()
        )
        if not rows:
            await q.message.reply_text("कोई booking नहीं मिली.", reply_markup=menu())
            return

        lines = ["📋 MY BOOKINGS", ""]
        for b in rows:
            lines.append(
                f"#{b.id} | {b.source} → {b.destination} | "
                f"{b.travel_date} | {b.quota} | {b.status}"
            )
        await q.message.reply_text("\n".join(lines), reply_markup=menu())
    finally:
        db.close()


async def profiles(update, context):
    q = update.callback_query
    await q.answer()
    db = SessionLocal()
    try:
        rows = (
            db.query(PassengerProfile)
            .filter_by(telegram_id=str(q.from_user.id))
            .order_by(PassengerProfile.id.desc())
            .limit(20)
            .all()
        )
        if not rows:
            await q.message.reply_text(
                "👤 अभी कोई saved passenger profile नहीं है.\n"
                "Profiles feature का database तैयार है; booking wizard में details भरकर booking save करें.",
                reply_markup=menu(),
            )
            return

        lines = ["👤 PASSENGER PROFILES", ""]
        for p in rows:
            lines.append(f"#{p.id} — {p.name} | {p.age} | {p.gender} | {p.berth}")
        await q.message.reply_text("\n".join(lines), reply_markup=menu())
    finally:
        db.close()


async def help_cmd(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(
        "ℹ️ SIMPLE FLOW\n\n"
        "1️⃣ Route + date\n"
        "2️⃣ Normal / Tatkal / Premium Tatkal\n"
        "3️⃣ Class + train + boarding\n"
        "4️⃣ One or more passengers\n"
        "5️⃣ Review + Save\n"
        "6️⃣ Open IRCTC\n"
        "7️⃣ CAPTCHA, login और payment manually complete करें\n\n"
        "⚡ Bot async webhook पर चलता है, इसलिए Telegram responses fast रखे गए हैं।\n"
        "🔐 Bot CAPTCHA bypass, anti-bot evasion या unattended payment नहीं करता।",
        reply_markup=menu(),
    )


def build_application():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_booking, pattern="^new$")],
        states={
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, travel_date)],
            QUOTA: [CallbackQueryHandler(quota, pattern="^quota:")],
            CLASS: [CallbackQueryHandler(travel_class, pattern="^class:")],
            TRAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, train)],
            BOARDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, boarding)],
            PASSENGER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, passenger_name)],
            PASSENGER_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, passenger_age)],
            PASSENGER_GENDER: [CallbackQueryHandler(passenger_gender, pattern="^gender:")],
            PASSENGER_BERTH: [CallbackQueryHandler(passenger_berth, pattern="^berth:")],
            PASSENGER_MORE: [CallbackQueryHandler(passenger_more, pattern="^(passenger:add|review)$")],
            CONFIRM: [
                CallbackQueryHandler(review, pattern="^review$"),
                CallbackQueryHandler(save, pattern="^save$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(my_bookings, pattern="^bookings$"))
    app.add_handler(CallbackQueryHandler(profiles, pattern="^profiles$"))
    app.add_handler(CallbackQueryHandler(help_cmd, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(home, pattern="^home$"))
    return app
