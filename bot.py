import os, threading, http.server, socketserver, yt_dlp, time
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

# --- VİDEO İNDİRME MOTORU ---
def download_video_file(url):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        # Telegram'da oynatılması için mp4 formatı ve 480p/720p sınırı (Boyut çok büyümesin diye)
        'format': 'best[ext=mp4][filesize<50M]/bestaudio[ext=m4a]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'Video Sahnesi')

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 **MEYHANAFM VİDEO PLAYER**\n\n"
        "📺 Bir YouTube linki at, direkt burada oynatalım!\n"
        "🎥 Komutla kullanmak için: `/video [link]`"
    )

async def video_gonder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Eğer komutla (/video ...) geldiyse args kullan, yoksa direkt mesaj metnini al
    url = " ".join(context.args) if context.args else update.message.text

    if not ("youtube.com/" in url or "youtu.be/" in url):
        return # YouTube linki değilse işlem yapma

    m = await update.message.reply_text("📥 **Sahne hazırlanıyor, Telegram'a yükleniyor...**")
    
    try:
        file_path, title = download_video_file(url)
        
        with open(file_path, 'rb') as video_file:
            # Burası videoyu Telegram içinde oynatılacak şekilde gönderen kısım
            await update.message.reply_video(
                video=video_file, 
                caption=f"🎬 **{title}**\n\n🍻 Keyifli seyirler kanka!",
                supports_streaming=True # Video inerken izlenebilmesini sağlar
            )
        
        os.remove(file_path) # Sunucuda yer kaplamasın diye sil
        await m.delete()

    except Exception as e:
        print(f"Hata: {e}")
        await m.edit_text("❌ **Hata:** Video çok büyük olabilir (50MB sınırı) veya link hatalı.")

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('video', video_gonder))
    # Link atıldığında otomatik yakalaması için:
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), video_gonder))
    
    app.run_polling()
