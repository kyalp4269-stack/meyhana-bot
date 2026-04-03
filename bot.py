import os, threading, http.server, socketserver, yt_dlp, time, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- AYARLAR ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'

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

# --- GELİŞMİŞ İNDİRME FONKSİYONU ---
def download_media(query, is_video=False):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Eğer link değilse YouTube'da ara
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"

    ydl_opts = {
        # Video ise 720p veya altını seç (Dosya boyutu 50MB'ı geçmesin diye)
        'format': 'best[ext=mp4][filesize<50M]/bestaudio[ext=m4a]/best' if is_video else 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }

    if not is_video:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        
        filename = ydl.prepare_filename(info)
        
        if not is_video:
            base, _ = os.path.splitext(filename)
            filename = base + ".mp3"
            
        return filename, info.get('title', 'Medya')

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **MEYHANAFM V3.5** ✨\n\n"
        "🎵 `/cal` - MP3 gönderir\n"
        "🎥 `/video` - Video gönderir (Telegram'da izle)\n"
        "📊 `/istatistik` - Durum raporu\n\n"
        "🍻 Link atman yeterli, otomatik MP3 yaparım!"
    )

async def handles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Komut mu yoksa direkt mesaj/link mi kontrol et
    is_video = False
    if update.message.text.startswith('/video'):
        is_video = True
        query = " ".join(context.args)
    elif update.message.text.startswith(('/cal', '/mp3')):
        query = " ".join(context.args)
    else:
        query = update.message.text # Direkt link atıldıysa

    if not query: return

    m = await update.message.reply_text("⏳ **İşlem başladı, meyhaneci hazırlıyor...**")
    
    try:
        file_path, title = download_media(query, is_video)
        
        if not os.path.exists(file_path):
            raise Exception("Dosya oluşturulamadı.")

        with open(file_path, 'rb') as f:
            if is_video:
                await update.message.reply_video(video=f, caption=f"🎬 **{title}**\n@MeyhanaFM_bot")
            else:
                await update.message.reply_audio(audio=f, title=title)
        
        os.remove(file_path) # Temizlik
        await m.delete()

    except Exception as e:
        print(f"HATA: {e}")
        await m.edit_text(f"❌ **Hata oluştu!**\n\nOlası Sebepler:\n1. Dosya 50MB'dan büyük.\n2. Sunucuda FFmpeg yüklü değil.\n3. YouTube botu engelledi.")

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('cal', handles))
    app.add_handler(CommandHandler('mp3', handles))
    app.add_handler(CommandHandler('video', handles))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handles))
    
    app.run_polling()
