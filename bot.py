import logging
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# BOT AYARLARI
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'

# 1. BAŞLATMA KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Selam Kanka! MeyhanaFM 7/24 Full Paket Aktif!\n\n"
        "🤖 **Sohbet:** Bana bir şey yaz, seninle dertleşirim.\n"
        "🎨 **Resim:** /ciz [istediğin şey] yaz, senin için görsel yapayım.\n"
        "🎵 **Müzik:** /cal [şarkı ismi] yaz, müziği getireyim."
    )
    await update.message.reply_text(welcome_text)

# 2. SOHBET ÖZELLİĞİ (AI)
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    # Basit yapay zeka mantığı (Geliştirilebilir)
    if "nasılsın" in user_msg.lower():
        reply = "MeyhanaFM gibi 7/24 bomba gibiyim kanka, sen nasılsın?"
    elif "kimsin" in user_msg.lower():
        reply = "Ben senin 7/24 hizmetindeki asistanın MeyhanaFM botuyum!"
    else:
        reply = f"Dediğini anladım kanka: '{user_msg}'. Seninle her konuda konuşmaya hazırım!"
    await update.message.reply_text(reply)

# 3. RESİM OLUŞTURMA ÖZELLİĞİ
async def ciz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        return await update.message.reply_text("Ne çizmemi istersin? Örnek: /ciz modifiyeli araba")
    
    await update.message.reply_text(f"🎨 '{prompt}' hayal ediliyor, çiziyorum kanka...")
    # Buraya ücretsiz bir resim servis linki ekledik
    image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '_')}"
    await update.message.reply_photo(photo=image_url, caption=f"İşte senin için çizdiğim: {prompt}")

# 4. MÜZİK BULMA ÖZELLİĞİ
async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sarki = " ".join(context.args)
    if not sarki:
        return await update.message.reply_text("Hangi şarkıyı istersin? Örnek: /cal Blok3-Laf")
    
    await update.message.reply_text(f"🎵 '{sarki}' aranıyor... MeyhanaFM senin için buluyor.")
    # Örnek bir önizleme/arama linki (Geliştirilebilir)
    await update.message.reply_text(f"🎧 Şarkıyı buradan dinleyebilir/indirebilirsin: https://www.youtube.com/results?search_query={sarki.replace(' ', '+')}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    print("MeyhanaFM Tüm Özelliklerle Başlatıldı!")
    app.run_polling()
