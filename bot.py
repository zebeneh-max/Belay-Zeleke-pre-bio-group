import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

# Customize these words for your Biology group.
PROHIBITED_WORDS = [
    "spamword1",
    "spamword2",
]

warnings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your Biology Group Moderator Bot. "
        "I help keep this group safe and educational."
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "BIOLOGY GROUP RULES\n"
        "1. Respect all members.\n"
        "2. No spam or advertisements.\n"
        "3. Keep discussions biology-related.\n"
        "4. No abusive language.\n"
        "5. Share reliable educational information."
    )

async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not user or not chat:
        return

    # Do not moderate administrators.
    member = await chat.get_member(user.id)
    if member.status in ("administrator", "creator"):
        return

    text = (message.text or message.caption or "").lower()

    if any(re.search(rf"\b{re.escape(word)}\b", text)
           for word in PROHIBITED_WORDS):
        try:
            await message.delete()
        except Exception:
            return

        key = (chat.id, user.id)
        warnings[key] = warnings.get(key, 0) + 1
        count = warnings[key]

        if count >= 3:
            await chat.ban_member(user.id, revoke_messages=False)
            await chat.send_message(
                f"{user.first_name} was removed after 3 warnings."
            )
        else:
            await chat.send_message(
                f"Warning {count}/3 for {user.first_name}. "
                "Please follow the group rules."
            )

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.CAPTION,
            moderate
        )
    )

    print("Biology Moderator Bot is running!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(level=logging.INFO)
    import asyncio
    import telegram

    asyncio.run(main())
