import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from telegram import Update

from bot import build_application
from db import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_app = build_application()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)

    await telegram_app.initialize()
    await telegram_app.start()

    webhook_url = os.getenv("WEBHOOK_URL", "").rstrip("/")
    if not webhook_url:
        logger.warning("WEBHOOK_URL is not set. Telegram webhook will not be configured.")
    else:
        webhook_endpoint = f"{webhook_url}/telegram/webhook"

        await telegram_app.bot.delete_webhook(drop_pending_updates=False)
        await telegram_app.bot.set_webhook(
            url=webhook_endpoint,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )

        info = await telegram_app.bot.get_webhook_info()
        logger.info(
            "Telegram webhook configured: url=%s pending=%s last_error=%s",
            info.url,
            info.pending_update_count,
            info.last_error_message,
        )

    yield

    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(title="Tatkal Ticket Telegram Bot", lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok", "service": "tatkal-ticket-telegram-bot"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/extension-demo", response_class=HTMLResponse)
async def extension_demo():
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Railway Booking Assistant - Deployed Demo</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; line-height: 1.5; }
    label { display: block; margin: 12px 0; }
    input, select { width: 100%; padding: 10px; box-sizing: border-box; }
    .note { padding: 12px; border: 1px solid #ccc; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>🚆 Deployed Booking Form Demo</h1>
  <p class="note">
    Learning demo only. The Chrome extension can fill these ordinary HTML
    fields after you explicitly click its button. This page does not automate
    IRCTC login, CAPTCHA, booking, or payment.
  </p>
  <label>Source <input id="source"></label>
  <label>Destination <input id="destination"></label>
  <label>Travel date <input id="travelDate" type="date"></label>
  <label>Train <input id="train"></label>
  <label>Boarding <input id="boarding"></label>
  <label>Quota
    <select id="quota">
      <option>GENERAL</option>
      <option>TATKAL</option>
      <option>PREMIUM TATKAL</option>
    </select>
  </label>
</body>
</html>
"""
    )


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        payload = await request.json()
        tg_update = Update.de_json(payload, telegram_app.bot)

        if tg_update is None:
            return {"ok": False, "error": "Invalid Telegram update"}

        await telegram_app.process_update(tg_update)
        return {"ok": True}

    except Exception:
        logger.exception("Telegram webhook processing failed")
        return {"ok": False, "error": "Webhook processing failed"}
