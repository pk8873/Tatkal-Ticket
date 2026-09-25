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


## Chrome extension learning demo

The repository also contains `chrome_extension_demo/`. It demonstrates how a Chrome Manifest V3 extension can fill a normal local HTML form after the user clicks **Fill Current Demo Page**.

### Run the local demo

1. Open a terminal in the cloned repository.
2. Run:
   `python -m http.server 8000 --directory chrome_extension_demo/demo`
3. Open `http://localhost:8000`.
4. Open Chrome and go to `chrome://extensions`.
5. Enable **Developer mode**.
6. Click **Load unpacked**.
7. Select the repository's `chrome_extension_demo` folder.
8. Open the extension popup.
9. Enter/save sample booking data.
10. Open the local demo and click **Fill Current Demo Page**.

This demo intentionally targets only localhost. It does not automate IRCTC, solve CAPTCHA, bypass anti-bot controls, submit bookings, or perform payments.

Chrome's Manifest V3 `scripting` API supports script injection with the appropriate permissions, but IRCTC's current terms prohibit automation/scripting software for its website/mobile app. Therefore the repository does not implement IRCTC-specific automatic form submission or CAPTCHA bypass.
