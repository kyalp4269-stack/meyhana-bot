import os, threading, http.server, socketserver, yt_dlp, time, random, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- AYARLAR ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'
ADMIN_ID = 6363063544 

settings = {
    "total_messages": 0,
    "users": set(),
    "command_usage": {},
    "start_time": time.time()
}

# --- WEB SERVER (RENDER İÇİN) ---
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"MeyhanaFM Aktif!")
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()

# --- İNDİRME MOTORU ---
def download_content(query, is_video=False):
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_video else 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    if not is_video:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info: info = info['entries'][0]
        filename = ydl.prepare_filename(info)
        
        if not is_video:
            base, _ = os.path.splitext(filename)
            filename = base + ".mp3"
            
        return filename, info.get('title', 'Dosya')

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"✨ **MEYHANAFM V3.0** ✨\n\n"
        f"🎵 `/cal` veya `/mp3` - Şarkıyı gruba atar\n"
        f"🎥 `/video` - Videoyu gruba atar (Telegram'da izle)\n"
        f"📊 `/istatistik` - Bot Durumu\n\n"
        f"🍻 **Sadece link atman da yeterli!**"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def medya_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE, is_video=False):
    query = " ".join(context.args)
    if not query and update.message.text: 
        query = update.message.text # Komutsuz link atıldıysa
    
    if not query: return
    
    m = await update.message.reply_text("📥 **MeyhanaFM indiriyor, bekle kanka...**")
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        file_path, title = download_content(query, is_video)
        
        with open(file_path, 'rb') as f:
            if is_video:
                await update.message.reply_video(video=f, caption=f"🎬 **{title}**")
            else:
                await update.message.reply_audio(audio=f, title=title, caption="🍻 Şerefe!")
        
        os.remove(file_path)
        await m.delete()
    except Exception as e:
        await m.edit_text(f"❌ **Hata:** Sunucuda `ffmpeg` eksik olabilir veya link hatalı.")

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int((time.time() - settings["start_time"]) / 60)
    await update.message.reply_text(f"📊 Mesaj: `{settings['total_messages']}` | Uptime: `{uptime} dk`", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    settings["total_messages"] += 1
    text = update.message.text
    
    if "youtube.com/" in text or "youtu.be/" in text:
        await medya_isleyici(update, context, is_video=False) # Otomatik MP3
    elif "selam" in text.lower():
        await update.message.reply_text(f"Selam **{update.message.from_user.first_name}**! 🍻", parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('cal', lambda u, c: medya_isleyici(u, c, False)))
    app.add_handler(CommandHandler('mp3', lambda u, c: medya_isleyici(u, c, False)))
    app.add_handler(CommandHandler('video', lambda u, c: medya_isleyici(u, c, True)))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
