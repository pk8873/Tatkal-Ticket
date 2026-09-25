# Tatkal Ticket Telegram Bot

A Telegram booking-assistant built from scratch for the workflow represented by Railway-automation.

Included:
- Telegram /start menu
- New booking wizard
- Source, destination and date
- Tatkal / Premium Tatkal
- Class
- Optional train number and boarding station
- Passenger details
- Review and save
- SQLite by default
- PostgreSQL support through DATABASE_URL
- My Bookings
- FastAPI health endpoint
- Telegram webhook
- Render configuration

Workflow boundary:
This bot does not automate CAPTCHA solving, bypass anti-bot controls, submit unattended payments, or store IRCTC passwords. After saving a booking request, the user opens IRCTC and completes CAPTCHA, authentication and final payment themselves.

Local:
1. Create a Telegram bot with BotFather.
2. Set BOT_TOKEN in .env.
3. Install: python -m pip install -r requirements.txt
4. Run: uvicorn app:app --reload

Render:
Build: pip install -r requirements.txt
Start: uvicorn app:app --host 0.0.0.0 --port $PORT
Set BOT_TOKEN and WEBHOOK_URL.
For persistent data, use PostgreSQL and set DATABASE_URL.

No software can guarantee ticket availability, successful booking, or uninterrupted operation because external availability, authentication, CAPTCHA, UI and network conditions can change.
