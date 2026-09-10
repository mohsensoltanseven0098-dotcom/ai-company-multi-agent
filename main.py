"""
سیستم چندعاملی شرکت مجازی هوش مصنوعی
ربات ادمین + ربات مدیریت + تولید محتوا
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==================== تنظیمات ====================
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "8625845458:AAEiIqKVNpTW_D-joBxkGU5nDB-Ai4z18Ww")
MANAGER_BOT_TOKEN = os.getenv("MANAGER_BOT_TOKEN", "8869889642:AAFFVyxS-Xnhb9V36VPCDSYJz2yeuubyzZE")
OWNER_ID = 310561750  # @MBK_1
CHANNEL_ID = "@mbkwebsite"

# ==================== لاگ ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== حافظه موقت ====================
orders = []
last_content_time = None

# ==================== پاسخ‌های آماده ====================
WELCOME_MSG = """سلام 👋
به شرکت مجازی هوش مصنوعی خوش اومدید.

ما خدمات زیر رو ارائه می‌دیم:
• ساخت سایت حرفه‌ای
• طراحی و توسعه اپلیکیشن
• کدنویسی و پروژه‌های نرم‌افزاری

برای ثبت سفارش کافیه بگید چه کاری می‌خواید انجام بدید.
"""

ORDER_RECEIVED = """✅ سفارش شما ثبت شد.

شماره پیگیری: #{order_id}
بخش مربوطه در حال بررسی هست.
به زودی نتیجه رو اعلام می‌کنیم.
"""

# ==================== ربات ادمین (ارتباط با مشتری) ====================
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MSG)

async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text or ""
    
    # ثبت سفارش ساده
    order_id = len(orders) + 1001
    orders.append({
        "id": order_id,
        "user_id": user.id,
        "username": user.username,
        "name": user.first_name,
        "text": text,
        "time": datetime.now().isoformat()
    })
    
    # جواب به مشتری
    await update.message.reply_text(ORDER_RECEIVED.format(order_id=order_id))
    
    # گزارش به مدیر
    manager_bot = Bot(token=MANAGER_BOT_TOKEN)
    report = f"""📩 سفارش جدید دریافت شد

شماره: #{order_id}
از: {user.first_name} (@{user.username or 'بدون یوزرنیم'})
آیدی: {user.id}

پیام:
{text}
"""
    try:
        await manager_bot.send_message(chat_id=OWNER_ID, text=report)
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش: {e}")

# ==================== ربات مدیریت (ارتباط با صاحب) ====================
async def manager_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("دسترسی مجاز نیست.")
        return
    await update.message.reply_text(
        "✅ ربات مدیریت فعال است.\n\n"
        "دستورات موجود:\n"
        "/status - وضعیت شرکت\n"
        "/orders - لیست سفارشات\n"
        "/post - ارسال محتوا به کانال\n"
        "/help - راهنما"
    )

async def manager_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    msg = f"""📊 وضعیت شرکت

• سفارشات ثبت‌شده: {len(orders)}
• ربات ادمین: فعال
• کانال: {CHANNEL_ID}
• زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    await update.message.reply_text(msg)

async def manager_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not orders:
        await update.message.reply_text("هنوز سفارشی ثبت نشده.")
        return
    
    text = "📋 آخرین سفارشات:\n\n"
    for o in orders[-10:]:
        text += f"#{o['id']} - {o['name']}: {o['text'][:50]}...\n"
    await update.message.reply_text(text)

async def manager_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    admin_bot = Bot(token=ADMIN_BOT_TOKEN)
    content = f"""✨ محتوای جدید شرکت

ما تخصص‌مون ساخت سایت و اپلیکیشن با کیفیت بالاست.

برای سفارش به ربات پیام بدید:
@Adghjxjjugikyhjjnbot

🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    try:
        await admin_bot.send_message(chat_id=CHANNEL_ID, text=content)
        await update.message.reply_text("✅ محتوا در کانال منتشر شد.")
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

async def manager_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("دسترسی مجاز نیست.")
        return
    await update.message.reply_text(
        "دستور دریافت شد. از دستورات زیر استفاده کنید:\n"
        "/status /orders /post /help"
    )

# ==================== تولید محتوا دوره‌ای ====================
async def periodic_content(context: ContextTypes.DEFAULT_TYPE):
    admin_bot = Bot(token=ADMIN_BOT_TOKEN)
    contents = [
        "🚀 تخصص ما ساخت سایت‌های مدرن و سریع هست.\nبرای سفارش به ربات پیام بدید.",
        "💡 اپلیکیشن موبایل حرفه‌ای می‌خواید؟ ما آماده‌ایم.\n@Adghjxjjugikyhjjnbot",
        "⚙️ کدنویسی تمیز و قابل نگهداری، اصل کار ماست.",
        "📱 از ایده تا محصول نهایی، کنار شما هستیم.",
        "🎯 کیفیت + سرعت + پشتیبانی = نتیجه کار ما"
    ]
    import random
    text = random.choice(contents) + f"\n\n🕒 {datetime.now().strftime('%H:%M')}"
    try:
        await admin_bot.send_message(chat_id=CHANNEL_ID, text=text)
        logger.info("محتوای دوره‌ای ارسال شد")
    except Exception as e:
        logger.error(f"خطا در ارسال محتوا: {e}")

# ==================== راه‌اندازی ====================
def main():
    # ربات ادمین
    admin_app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    admin_app.add_handler(CommandHandler("start", admin_start))
    admin_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_message))
    
    # ربات مدیریت
    manager_app = Application.builder().token(MANAGER_BOT_TOKEN).build()
    manager_app.add_handler(CommandHandler("start", manager_start))
    manager_app.add_handler(CommandHandler("status", manager_status))
    manager_app.add_handler(CommandHandler("orders", manager_orders))
    manager_app.add_handler(CommandHandler("post", manager_post))
    manager_app.add_handler(CommandHandler("help", manager_start))
    manager_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manager_message))
    
    # Job برای تولید محتوا هر ۳۰ دقیقه
    job_queue = admin_app.job_queue
    if job_queue:
        job_queue.run_repeating(periodic_content, interval=1800, first=10)
    
    logger.info("سیستم چندعاملی در حال اجرا...")
    
    # اجرای همزمان دو ربات
    async def run_both():
        await asyncio.gather(
            admin_app.initialize(),
            manager_app.initialize(),
        )
        await admin_app.start()
        await manager_app.start()
        await admin_app.updater.start_polling()
        await manager_app.updater.start_polling()
        # نگه داشتن برنامه
        await asyncio.Event().wait()
    
    asyncio.run(run_both())

if __name__ == "__main__":
    main()
