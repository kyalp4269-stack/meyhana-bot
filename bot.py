import logging
import asyncio
import os
import yt_dlp
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# BOT AYARLARI
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'

# RENDER HATA VERMESİN DİYE KÜÇÜK BİR KAPI (PORT) AÇALIM
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_web_server, daemon=True).start()

# 1. BAŞLATMA KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 MeyhanaFM Full Paket Aktif!\n\n"
        "🤖 **Sohbet:** Yaz bana, konuşalım kanka.\n"
        "🎨 **Resim:** /ciz [istediğin şey]\n"
        "🎵 **Müzik Bul:** /cal [şarkı adı]\n"
        "📥 **MP3 İndir:** /mp3 [YouTube linki]"
    )
    await update.message.reply_text(welcome_text)

# 2. SOHBET
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    if "nasılsın" in user_msg: reply = "7/24 bulutlarda nöbetteyim kanka, bomba gibiyim!"
    elif "selam" in user_msg: reply = "Selam kanka, MeyhanaFM emrinde!"
    else: reply = f"Anlıyorum kanka... MeyhanaFM her zaman yanında!"
    await update.message.reply_text(reply)

# 3. RESİM ÇİZ
async def ciz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt: return await update.message.reply_text("Ne çizeyim kanka? Örnek: /ciz araba")
    image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '_')}"
    await update.message.reply_photo(photo=image_url, caption=f"🎨 İşte hayalin: {prompt}")

# 4. MÜZİK BUL
async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sarki = " ".join(context.args)
    if not sarki: return await update.message.reply_text("Hangi şarkı kanka?")
    link = f"https://www.youtube.com/results?search_query={sarki.replace(' ', '+')}"
    await update.message.reply_text(f"🎵 Şarkıyı burada buldum kanka: {link}")

# 5. MP3 YAPMA (YENİ GÜÇ!)
async def mp3_indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("Link nerde kanka? /mp3 [link]")
    
    durum = await update.message.reply_text("⏳ MeyhanaFM şarkıyı MP3'e çeviriyor, beklemede kal...")
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
        await update.message.reply_audio(audio=open(filename, 'rb'), caption=f"✅ {info['title']} hazır!")
        os.remove(filename)
        await durum.delete()
    except:
        await update.message.reply_text("❌ MP3 yaparken bir hata çıktı kanka.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('mp3', mp3_indir))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    app.run_polling()
