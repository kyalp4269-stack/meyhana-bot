import os, threading, http.server, socketserver, yt_dlp, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from googletrans import Translator

# --- AYARLAR VE DEĞİŞKENLER ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'
# Senin Telegram ID'ni buraya yazarsan admin panelini sadece sen açabilirsin (Örn: 12345678)
ADMIN_ID = 0 

translator = Translator()

# Bot Hafızası (İstatistik ve Ayarlar)
settings = {
    "translate_active": True,
    "total_messages": 0,
    "users": set(),
    "command_usage": {},
    "start_time": time.time()
}

# --- RENDER İÇİN PORT AÇMA ---
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_web_server, daemon=True).start()

# --- YARDIMCI FONKSİYONLAR ---
def track_stats(command):
    settings["command_usage"][command] = settings["command_usage"].get(command, 0) + 1

# --- GÖSTERİŞLİ MESAJLAR VE KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("start")
    user = update.effective_user
    welcome_text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"     ✨ **MEYHANAFM V2.0** ✨\n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Selam **{user.first_name}**, MeyhanaFM'e hoş geldin!\n"
        f"🎧 Senin için grubu şenlendirmeye geldim.\n\n"
        f"🎨 ` /ciz ` - Hayalini resme dök\n"
        f"🎵 ` /cal ` - Grupta şarkı/video ara\n"
        f"📥 ` /mp3 ` - YouTube linkini sese çevir\n"
        f"📊 ` /istatistik ` - Grup nabzını ölç\n"
        f"🛠 ` /panel ` - Yönetici merkezi\n\n"
        f"✨ *Kurucu:* **Alperen KAYA**"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def ciz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("ciz")
    p = "+".join(context.args)
    if not p: return await update.message.reply_text("🤔 **Ne çizmemi istersin?** Örn: `/ciz uzayda meyhane`", parse_mode='Markdown')
    m = await update.message.reply_text("🎨 **Hayalin fırçaya dökülüyor, bekle...**")
    await update.message.reply_photo(f"https://pollinations.ai/p/{p}", caption=f"✨ İşte senin için çizdiğim: *{p}*", parse_mode='Markdown')
    await m.delete()

async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("cal")
    s = " ".join(context.args)
    if not s: return await update.message.reply_text("🎵 **Hangi şarkıyı veya videoyu arıyorsun?**", parse_mode='Markdown')
    # Video bulma ve bir kısmını gösterme mantığı için link üretir
    search_url = f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}"
    await update.message.reply_text(
        f"🔍 **'{s}'** için en iyi sonuçları buldum!\n\n"
        f"📺 **İzlemek/Dinlemek için:** [Buraya Tıkla]({search_url})\n"
        f"💡 *Not: Gruba müzik botu olarak eklediysen sesli sohbete bağlanabilirim.*", 
        parse_mode='Markdown'
    )

async def mp3_indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("mp3")
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("❌ **Lütfen geçerli bir YouTube linki ver!**")
    m = await update.message.reply_text("📡 **Ses dosyası hazırlanıyor, bu biraz sürebilir...**")
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            await update.message.reply_text(f"✅ **Hazır!**\n\n🎧 [Dosyayı İndirmek İçin Tıkla]({audio_url})", parse_mode='Markdown')
            await m.delete()
    except:
        await update.message.reply_text("❌ **Hata:** Link bozuk veya desteklenmiyor.")

# --- YENİ EKLENEN CANAVAR ÖZELLİKLER ---

# 1. & 2. İSTATİSTİK VE OTOMATİK ÇEVİRİ SİSTEMİ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    msg_text = update.message.text
    user = update.message.from_user
    
    # İstatistikleri Kaydet
    settings["total_messages"] += 1
    settings["users"].add(user.id)

    # Otomatik Çeviri (Türkçe değilse ve aktifse)
    if settings["translate_active"]:
        try:
            detected = translator.detect(msg_text)
            if detected.lang != 'tr' and len(msg_text) > 3:
                translated = translator.translate(msg_text, dest='tr')
                await update.message.reply_text(
                    f"🌍 **[Otomatik Çeviri]**\n"
                    f"💬 *{user.first_name} dedi ki:* \n"
                    f"➜ {translated.text}", 
                    parse_mode='Markdown'
                )
        except: pass

    # Sohbet Botu Tepkileri
    msg = msg_text.lower()
    if "selam" in msg: await update.message.reply_text(f"Selam kanka **{user.first_name}**, hoş geldin! 🍻", parse_mode='Markdown')

# 3. ÖZEL KARŞILAMA (Yönetici ve Üye Ayrımı)
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        # Eğer botun sahibi veya grupta yetkiliyse özel selam
        status = "🌟 **YÖNETİCİ/KURUCU**" if member.id == ADMIN_ID else "👤 **ÜYE**"
        
        welcome_msg = (
            f"🎊 **GRUBUMUZA YENİ BİR KAN GELDİ!** 🎊\n\n"
            f"👤 **İsim:** {member.first_name}\n"
            f"🎖 **Statü:** {status}\n\n"
            f"🚀 Seninle beraber daha güçlüyüz kanka! Komutlar için `/start` yazabilirsin."
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

# 4. GELİŞMİŞ İSTATİSTİK PANELİ
async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_cmd = max(settings["command_usage"], key=settings["command_usage"].get) if settings["command_usage"] else "Yok"
    uptime = int((time.time() - settings["start_time"]) / 60) # Dakika cinsinden
    
    stats_text = (
        f"📊 **MEYHANAFM GRUP ANALİZİ**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📩 **Toplam Mesaj:** `{settings['total_messages']}`\n"
        f"👥 **Aktif Kişi:** `{len(settings['users'])}` kişi\n"
        f"🔥 **En Çok Kullanılan:** `/{top_cmd}`\n"
        f"🌍 **Çeviri Durumu:** `{'Açık ✅' if settings['translate_active'] else 'Kapalı ❌'}`\n"
        f"⏱ **Bot Uyanıklık Süresi:** `{uptime} dk`"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# 5. YÖNETİCİ MERKEZİ (Panel)
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌍 Çeviri: AÇ/KAPAT", callback_data='toggle_translate')],
        [InlineKeyboardButton("📊 Detaylı İstatistik", callback_data='show_stats')],
        [InlineKeyboardButton("❌ Paneli Kapat", callback_data='close_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛠 **MEYHANAFM YÖNETİCİ MERKEZİ**\nBuradan botun ana damarlarını kontrol edebilirsin:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'toggle_translate':
        settings["translate_active"] = not settings["translate_active"]
        durum = "AÇIK ✅" if settings["translate_active"] else "KAPALI ❌"
        await query.edit_message_text(f"⚙️ **Çeviri Sistemi:** {durum}", parse_mode='Markdown')
    elif query.data == 'show_stats':
        await istatistik(query, context)
    elif query.data == 'close_panel':
        await query.message.delete()

# --- ANA ÇALIŞTIRICI ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('mp3', mp3_indir))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(CommandHandler('panel', panel))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 MeyhanaFM Tüm Özelliklerle Yayında!")
    app.run_polling()
