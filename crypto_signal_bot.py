import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# Replace this with your actual bot token
BOT_TOKEN = "8158169533:AAHZPkDUuYWAkYDhH2nNiegGZT06QTOdin4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🤖 Bot Crypto đã hoạt động!')

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Đây chỉ là ví dụ trả về 1 fake tín hiệu
    await update.message.reply_text('🚀 BUY BTC/USDT 2% trên Binance 4H EMA trending!')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command /start
    app.add_handler(CommandHandler('start', start))

    # Command /signal
    app.add_handler(CommandHandler('signal', signal))

    app.run_polling()

if __name__ == '__main__':
    main()
