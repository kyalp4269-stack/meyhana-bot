import logging
import sympy
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'

async def start(u, c):
    await u.message.reply_text("👋 MeyhanaFM 7/24 Aktif!")

async def hesapla(u, c):
    try:
        islem = " ".join(c.args)
        if not islem: return await u.message.reply_text("İşlem yaz kanka.")
        sonuc = sympy.sympify(islem)
        await u.message.reply_text(f"✅ Sonuç: {sonuc}")
    except:
        await u.message.reply_text("Hata!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('hesapla', hesapla))
    app.run_polling()
