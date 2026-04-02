import os, threading, http.server, socketserver, yt_dlp, time, random, requests
from io import BytesIO
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

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("start")
    user = update.effective_user
    welcome_text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"     ✨ **MEYHANAFM V2.0** ✨\n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Selam **{user.first_name}**, hoş geldin!\n\n"
        f"🎨 `/ciz` - Hayalini resme dök\n"
        f"🎵 `/cal` - Müzik/Video Player\n"
        f"📥 `/mp3` - YouTube MP3 İndir\n"
        f"📊 `/istatistik` - Grup Raporu\n\n"
        f"✨ *Kurucu:* **Alperen KAYA**"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def ciz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("ciz")
    p = "+".join(context.args)
    if not p: return await update.message.reply_text("🤔 **Ne çizmemi istersin?**")
    
    m = await update.message.reply_text("🎨 **Hayalin fırçaya dökülüyor...**")
    seed = random.randint(1, 999999)
    # URL'yi doğrudan göndermek yerine dosyayı indirip gönderiyoruz
    image_url = f"https://pollinations.ai/p/{p}?width=1024&height=1024&seed={seed}&nologo=true"
    
    try:
        response = requests.get(image_url, timeout=20)
        if response.status_code == 200:
            image_file = BytesIO(response.content)
            await update.message.reply_photo(photo=image_file, caption=f"✨ Sonuç: *{p.replace('+', ' ')}*", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Resim servisi yanıt vermedi.")
    except:
        await update.message.reply_text("❌ Bir hata oluştu.")
    await m.delete()

async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("cal")
    s = " ".join(context.args)
    if not s: return await update.message.reply_text("🎵 **Hangi şarkıyı arıyoruz?**")
    
    m = await update.message.reply_text("🔍 **MeyhanaFM Arşivi Taranıyor...**")
    search_url = f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}"
    keyboard = [[InlineKeyboardButton("▶️ Oynat / Dinle", url=search_url)]]
    await update.message.reply_text(f"🎵 **Parça:** `{s}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    await m.delete()

async def mp3_indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("mp3")
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("❌ **YouTube linki vermen lazım!**")
    # MP3 indirme linki (Geri eklendi)
    await update.message.reply_text(f"📡 [Buraya Tıklayarak MP3 İndir](https://www.youtubepp.com/watch?v={url.split('=')[-1] if '=' in url else ''})", parse_mode='Markdown')

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int((time.time() - settings["start_time"]) / 60)
    await update.message.reply_text(f"📊 **MEYHANAFM DURUM**\n📩 Mesaj: `{settings['total_messages']}`\n⏱ Uptime: `{uptime} dk`", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    settings["total_messages"] += 1
    settings["users"].add(update.message.from_user.id)
    if "selam" in update.message.text.lower():
        await update.message.reply_text(f"Selam kanka **{update.message.from_user.first_name}**! 🍻", parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('mp3', mp3_indir))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
