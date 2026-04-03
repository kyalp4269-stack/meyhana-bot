import os, threading, http.server, socketserver, yt_dlp, time, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- AYARLAR ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'

settings = {
    "total_messages": 0,
    "start_time": time.time()
}

# --- WEB SERVER (RENDER İÇİN) ---
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers()
            self.wfile.write(b"MeyhanaFM Aktif!")
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()

# --- MEDYA MOTORU ---
def download_media(query, is_video=False):
    if not os.path.exists('downloads'): os.makedirs('downloads')
    if not query.startswith("http"): query = f"ytsearch1:{query}"

    ydl_opts = {
        'format': 'best[ext=mp4][filesize<50M]/best' if is_video else 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True, 'no_warnings': True, 'noplaylist': True,
    }

    if not is_video:
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info: info = info['entries'][0]
        path = ydl.prepare_filename(info)
        if not is_video:
            path = os.path.splitext(path)[0] + ".mp3"
        return path, info.get('title', 'Medya')

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"     ✨ **MEYHANAFM V4.5** ✨\n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"🎵 `/cal` - Şarkıyı MP3 olarak atar\n"
        f"🎥 `/video` - Sahneyi gruba atar (Burada izle)\n"
        f"📊 `/istatistik` - Bot raporu\n\n"
        f"🍻 **Link atman yeterli, otomatik MP3 yaparım!**"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def medya_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    is_video = text.startswith('/video')
    query = " ".join(context.args) if context.args else text

    if not query or query.startswith('/start') or query.startswith('/istatistik'): return

    m = await update.message.reply_text("📥 **Meyhaneci hazırlıyor, bekle kanka...**")
    try:
        file_path, title = download_media(query, is_video)
        with open(file_path, 'rb') as f:
            if is_video:
                await update.message.reply_video(video=f, caption=f"🎬 **{title}**", supports_streaming=True)
            else:
                await update.message.reply_audio(audio=f, title=title, caption="🍻 Şerefe!")
        os.remove(file_path)
        await m.delete()
    except Exception as e:
        await m.edit_text("❌ **Hata:** YouTube engellemiş olabilir veya dosya çok büyük.")

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int((time.time() - settings["start_time"]) / 60)
    await update.message.reply_text(f"📊 **MEYHANAFM DURUM**\n📩 Mesaj: `{settings['total_messages']}`\n⏱ Uptime: `{uptime} dk`", parse_mode='Markdown')

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    settings["total_messages"] += 1
    
    text = update.message.text.lower()
    if "youtube.com/" in text or "youtu.be/" in text:
        await medya_isleyici(update, context)
    elif "selam" in text:
        await update.message.reply_text(f"Selam kanka **{update.message.from_user.first_name}**! 🍻", parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(CommandHandler('cal', medya_isleyici))
    app.add_handler(CommandHandler('mp3', medya_isleyici))
    app.add_handler(CommandHandler('video', medya_isleyici))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_all))
    
    app.run_polling()
