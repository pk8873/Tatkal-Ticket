import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import build_application
from db import Base, engine

telegram_app = build_application()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    await telegram_app.initialize()
    await telegram_app.start()
    webhook_url = os.getenv("WEBHOOK_URL", "").rstrip("/")
    if webhook_url:
        await telegram_app.bot.set_webhook(f"{webhook_url}/telegram/webhook")
    yield
    await telegram_app.stop()
    await telegram_app.shutdown()

app = FastAPI(title="Tatkal Ticket Telegram Bot", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status":"ok","service":"tatkal-ticket-telegram-bot"}

@app.get("/health")
async def health():
    return {"status":"healthy"}

@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    from telegram import Update
    tg_update = Update.de_json(update, telegram_app.bot)
    await telegram_app.process_update(tg_update)
    return {"ok": True}
