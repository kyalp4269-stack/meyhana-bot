import os, threading, http.server, socketserver, yt_dlp, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. MADDE: ADMIN VE AYARLAR ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'
ADMIN_ID = 6363063544  # Kendi Telegram ID'ni buraya yazabilirsin

settings = {
    "total_messages": 0,
    "users": set(),
    "command_usage": {},
    "start_time": time.time()
}

# --- 4. MADDE: SÜREKLİLİK (RENDER WEB SERVER) ---
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"MeyhanaFM Aktif!")
            
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"🌍 Web server {PORT} portunda calisiyor...")
        httpd.serve_forever()

# --- 2. MADDE: İSTATİSTİK TAKİBİ ---
def track_stats(command):
    settings["command_usage"][command] = settings["command_usage"].get(command, 0) + 1

# --- 3. MADDE: GÖRSEL VE KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("start")
    user = update.effective_user
    welcome_text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"     ✨ **MEYHANAFM V2.0** ✨\n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Selam **{user.first_name}**, hoş geldin!\n"
        f"🎧 Senin için grubu şenlendirmeye geldim.\n\n"
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
    if not p: return await update.message.reply_text("🤔 **Ne çizmemi istersin?**", parse_mode='Markdown')
    m = await update.message.reply_text("🎨 **Hayalin fırçaya dökülüyor...**")
    try:
        await update.message.reply_photo(f"https://pollinations.ai/p/{p}", caption=f"✨ İşte sonucun: *{p}*", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Resim oluşturulamadı.")
    await m.delete()

async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("cal")
    s = " ".join(context.args)
    if not s: return await update.message.reply_text("🎵 **Hangi şarkıyı arıyoruz?**", parse_mode='Markdown')
    
    m = await update.message.reply_text("🔍 **MeyhanaFM Arşivi Taranıyor...**")
    search_url = f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}"
    keyboard = [[InlineKeyboardButton("▶️ Oynat / Dinle", url=search_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎵 **MÜZİK PLAYER**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎧 **Parça:** `{s}`\n"
        f"👤 **İsteyen:** {update.effective_user.first_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━", 
        reply_markup=reply_markup, parse_mode='Markdown'
    )
    await m.delete()

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int((time.time() - settings["start_time"]) / 60)
    stats_text = (
        f"📊 **MEYHANAFM DURUM RAPORU**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📩 **Toplam Mesaj:** `{settings['total_messages']}`\n"
        f"👥 **Aktif Kişi:** `{len(settings['users'])}` kişi\n"
        f"⏱ **Bot Uyanık:** `{uptime} dk`"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    settings["total_messages"] += 1
    settings["users"].add(update.message.from_user.id)
    
    msg = update.message.text.lower()
    if "selam" in msg:
        await update.message.reply_text(f"Selam kanka **{update.message.from_user.first_name}**! 🍻", parse_mode='Markdown')

if __name__ == '__main__':
    # Web sunucusunu başlat
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Botu kur
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 MeyhanaFM V2.0 Yayında!")
    app.run_polling()
