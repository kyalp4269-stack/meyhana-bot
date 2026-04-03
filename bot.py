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

def track_stats(command):
    settings["command_usage"][command] = settings["command_usage"].get(command, 0) + 1

# --- YARDIMCI FONKSİYONLAR (İndirme İşlemi) ---
def download_audio(query):
    # Eğer sorgu link değilse YouTube'da ara
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        # Liste ise ilk öğeyi al (arama sonuçları için)
        if 'entries' in info:
            info = info['entries'][0]
        
        filename = ydl.prepare_filename(info)
        # Uzantıyı mp3 olarak düzeltiyoruz çünkü postprocessor çeviriyor
        base, _ = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        return mp3_filename, info.get('title', 'Ses Dosyası')

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("start")
    user = update.effective_user
    welcome_text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"     ✨ **MEYHANAFM V2.5** ✨\n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Selam **{user.first_name}**, hoş geldin!\n\n"
        f"🎵 `/cal [isim/link]` - Müzik İndir & Dinle\n"
        f"📥 `/mp3 [link]` - YouTube MP3 İndir\n"
        f"📊 `/istatistik` - Bot Raporu\n\n"
        f"🍻 *Gruba link atman yeterli, gerisini bana bırak!*"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def cal_ve_indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        return await update.message.reply_text("🎵 **Hangi şarkıyı indirmemi istersin?**")
    
    m = await update.message.reply_text("📥 **MeyhanaFM senin için hazırlıyor...**")
    
    try:
        # İndirme klasörü yoksa oluştur
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        file_path, title = download_audio(query)
        
        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio, 
                title=title, 
                caption=f"✅ **{title}** hazır! Keyifli dinlemeler. 🍻",
                parse_mode='Markdown'
            )
        
        # Dosyayı gönderdikten sonra sil (Render hafızası dolmasın)
        os.remove(file_path)
        await m.delete()
        
    except Exception as e:
        print(f"Hata: {e}")
        await m.edit_text("❌ **Üzgünüm, bu içeriği indiremedim.**")

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int((time.time() - settings["start_time"]) / 60)
    await update.message.reply_text(f"📊 **MEYHANAFM DURUM**\n📩 Mesaj: `{settings['total_messages']}`\n⏱ Uptime: `{uptime} dk`", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    settings["total_messages"] += 1
    
    # Eğer mesaj bir YouTube linki içeriyorsa otomatik indir
    if "youtube.com/" in text or "youtu.be/" in text:
        # Komutsuz direkt link atıldığında cal_ve_indir fonksiyonunu tetikle
        context.args = [text]
        await cal_ve_indir(update, context)
    
    elif "selam" in text.lower():
        await update.message.reply_text(f"Selam kanka **{update.message.from_user.first_name}**! 🍻", parse_mode='Markdown')

if __name__ == '__main__':
    # Klasör kontrolü
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('cal', cal_ve_indir))
    app.add_handler(CommandHandler('mp3', cal_ve_indir))
    app.add_handler(CommandHandler('istatistik', istatistik))
    
    # Hem komutları hem de normal mesajları (linkleri) dinle
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
