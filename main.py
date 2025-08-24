import logging
import random
from telegram import Update, ChatMember, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- CONFIG ---
BOT_TOKEN = "8142929033:AAEI-63s7Sp-a93GgeQppUGuTzsPUHqRVcE"
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
    if update.message.from_user.id not in [admin.user.id for admin in (await update.effective_chat.get_administrators())]:
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
    chat_id = context.job.chat_id if hasattr(context.job, "chat_id") else None
    if chat_id:
        # fancy big stylish font (Unicode)
        message = f"💞 𝓑𝓮𝓼𝓽 𝓒𝓸𝓾𝓹𝓵𝓮 𝓸𝓯 𝓽𝓱𝓮 𝓱𝓸𝓾𝓻 💞\n\n" \
                  f"❤️ <a href='tg://user?id={couple[0]}'>User 1</a> + <a href='tg://user?id={couple[1]}'>User 2</a> ❤️"

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(IMAGE_PATH),
            caption=message,
            parse_mode="HTML"
        )

async def set_hourly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start hourly job in current chat."""
    scheduler = context.application.job_queue.scheduler
    scheduler.add_job(
        choose_couple,
        "interval",
        hours=1,
        args=[context],
        kwargs={"chat_id": update.effective_chat.id},
        replace_existing=True,
        id=f"couple_{update.effective_chat.id}",
    )
    await update.message.reply_text("✅ Hourly couple selection started!")

# --- MAIN ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
scheduler = AsyncIOScheduler()
scheduler.start()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("sethourly", set_hourly))
app.add_handler(CommandHandler("setimage", set_image))
app.add_handler(MessageHandler(filters.ALL, register_user))

app.run_polling()