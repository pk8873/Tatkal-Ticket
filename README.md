# Tatkal Ticket Telegram Bot

A fast, simple Telegram booking assistant for Normal, Tatkal and Premium Tatkal railway workflows.

## Included

- Simple Telegram menu
- Normal / Tatkal / Premium Tatkal
- Source, destination and future-date validation
- Class selection
- Optional train and boarding station
- Up to 6 passengers in one booking
- Booking review before saving
- My Bookings
- Passenger profile storage
- One-click Open IRCTC & Continue button
- SQLite by default
- PostgreSQL support through DATABASE_URL
- FastAPI health endpoint
- Telegram webhook
- Render configuration

## Booking workflow

1. Start the bot.
2. Choose **New Booking**.
3. Enter route and travel date.
4. Choose Normal, Tatkal or Premium Tatkal.
5. Choose class.
6. Enter optional train/boarding station.
7. Add one or more passengers.
8. Review and save.
9. Open IRCTC from the Telegram button.
10. Complete IRCTC login, CAPTCHA, booking review and final payment yourself.

The bot is designed to reduce repetitive data entry while keeping authentication, CAPTCHA and payment under the user's control.

## Security boundary

This project does **not** bypass CAPTCHA, evade anti-bot controls, submit unattended payments, or store IRCTC passwords/payment credentials.

No software can guarantee ticket availability, successful booking, or millisecond ticket confirmation because IRCTC availability, authentication, CAPTCHA, queueing, website state and network conditions are external dependencies.

## Local

1. Create a Telegram bot with BotFather.
2. Set BOT_TOKEN in .env.
3. Install: `python -m pip install -r requirements.txt`
4. Run: `uvicorn app:app --reload`

## Render

Build command:

`pip install -r requirements.txt`

Start command:

`uvicorn app:app --host 0.0.0.0 --port $PORT`

Set:
- BOT_TOKEN
- WEBHOOK_URL

For persistent production data, use PostgreSQL and set DATABASE_URL.
