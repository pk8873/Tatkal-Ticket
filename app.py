import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
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

        # Replace any old/stale webhook configuration with this deployment URL.
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
