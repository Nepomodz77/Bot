import logging
import random
import os
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
IMAGE_PATH = "couple.jpg"  # default image
members = set()

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- Functions ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I will choose the Best Couple every hour ❤️")

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store active members (only in groups)."""
    if update.message.chat.type in ["group", "supergroup"]:
        user = update.message.from_user
        members.add(user.id)

async def set_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admins can set couple image by replying with a photo."""
    global IMAGE_PATH
    admins = [admin.user.id for admin in await update.effective_chat.get_administrators()]
    if update.message.from_user.id not in admins:
        await update.message.reply_text("Only admins can change the image!")
        return
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]
        file = await photo.get_file()
        IMAGE_PATH = "couple.jpg"
        await file.download_to_drive(IMAGE_PATH)
        await update.message.reply_text("✅ Couple image updated!")

async def choose_couple(context: ContextTypes.DEFAULT_TYPE):
    """Randomly choose a couple every hour."""
    if len(members) < 2:
        return
    couple = random.sample(list(members), 2)
    chat_id = context.job.chat_id

    message = (
        f"💞 𝓑𝓮𝓼𝓽 𝓒𝓸𝓾𝓹𝓵𝓮 𝓸𝓯 𝓽𝓱𝓮 𝓱𝓸𝓾𝓻 💞\n\n"
        f"❤️ <a href='tg://user?id={couple[0]}'>User 1</a> + <a href='tg://user?id={couple[1]}'>User 2</a> ❤️"
    )

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=InputFile(IMAGE_PATH),
        caption=message,
        parse_mode="HTML"
    )

async def set_hourly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start hourly job in current chat."""
    chat_id = update.effective_chat.id
    context.job_queue.run_repeating(
        choose_couple,
        interval=3600,  # every hour
        first=10,       # first run after 10 sec
        chat_id=chat_id,
        name=f"couple_{chat_id}"
    )
    await update.message.reply_text("✅ Hourly couple selection started!")

# --- MAIN ---
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("sethourly", set_hourly))
app.add_handler(CommandHandler("setimage", set_image))
app.add_handler(MessageHandler(filters.ALL, register_user))

app.run_polling()
