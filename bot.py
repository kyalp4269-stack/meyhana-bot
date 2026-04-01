import os, threading, http.server, socketserver, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from googletrans import Translator

# --- AYARLAR VE DEĞİŞKENLER ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'
translator = Translator()

# Bot Ayarları (Kapatılınca sıfırlanmaması için ileride veritabanına bağlanabilir)
settings = {
    "translate_active": True,
    "total_messages": 0,
    "users": set()
}

# --- RENDER İÇİN PORT AÇMA ---
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_web_server, daemon=True).start()

# --- ESKİ ÖZELLİKLER (KORUNANLAR) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **MeyhanaFM Full Paket!**\n"
        "🤖 Sohbet ve Müzik İstasyonu aktif.\n\n"
        "🎨 `/ciz [metin]` - Hayalini resmet\n"
        "🎵 `/cal [isim]` - Şarkı ara\n"
        "📥 `/mp3 [link]` - YouTube'dan ses al\n"
        "📊 `/istatistik` - Botun durumu\n"
        "⚙️ `/panel` - Yönetici ayarları"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def ciz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = "+".join(context.args)
    if not p: return await update.message.reply_text("Ne çizeyim?")
    await update.message.reply_photo(f"https://pollinations.ai/p/{p}", caption="🎨 İşte hayalin!")

async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = "+".join(context.args)
    if not s: return await update.message.reply_text("Hangi şarkı?")
    await update.message.reply_text(f"🎵 Şarkıyı burada buldum: https://www.youtube.com/results?search_query={s}")

async def mp3_indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url: return await update.message.reply_text("❌ Link vermen lazım!")
    m = await update.message.reply_text("⏳ Ses çıkarılıyor...")
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            await update.message.reply_text(f"✅ Hazır!\n🎧 [Buraya Tıkla ve İndir]({audio_url})", parse_mode='Markdown')
            await m.delete()
    except:
        await update.message.reply_text("❌ Linkte bir sorun var.")

# --- YENİ ÖZELLİKLER (EKLENENLER) ---

# 1. OTOMATİK ÇEVİRİ VE SOHBET
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    user_id = update.message.from_user.id
    
    # İstatistik Güncelleme
    settings["total_messages"] += 1
    settings["users"].add(user_id)

    # Otomatik Çeviri (Sadece yönetici açmışsa ve dil Türkçe değilse)
    if settings["translate_active"]:
        try:
            detected = translator.detect(msg_text)
            if detected.lang != 'tr':
                translated = translator.translate(msg_text, dest='tr')
                await update.message.reply_text(f"🌍 **Çeviri:** {translated.text}", parse_mode='Markdown')
        except:
            pass # Çeviri hatası olursa botu durdurma

    # Eski Sohbet Özelliği
    msg = msg_text.lower()
    if "selam" in msg: await update.message.reply_text("Selam kanka, MeyhanaFM emrinde!")
    elif "nasılsın" in msg: await update.message.reply_text("Bomba gibiyim kanka, sen nasılsın?")

# 2. GÖSTERİŞLİ KARŞILAMA
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🌟 Aramıza hoş geldin **{member.first_name}**! \nMeyhanaFM'e neşe kattın. Komutları görmek için /start yazabilirsin.", parse_mode='Markdown')

# 3. İSTATİSTİK PANELİ
async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 **MeyhanaFM Durum Raporu**\n"
        f"📩 Toplam Mesaj: {settings['total_messages']}\n"
        f"👥 Aktif Kullanıcı: {len(settings['users'])}\n"
        f"🌐 Çeviri Modu: {'✅ AÇIK' if settings['translate_active'] else '❌ KAPALI'}"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

# 4. YÖNETİCİ PANELİ (Aç/Kapat)
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Basit güvenlik: Sadece sen (veya adminler) kullanabilsin diye kontrol eklenebilir
    keyboard = [
        [InlineKeyboardButton("🌍 Çeviri: AÇ/KAPAT", callback_data='toggle_translate')],
        [InlineKeyboardButton("❌ Paneli Kapat", callback_data='close_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛠 **Yönetici Kontrol Merkezi:**", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'toggle_translate':
        settings["translate_active"] = not settings["translate_active"]
        durum = "AÇIK" if settings["translate_active"] else "KAPALI"
        await query.edit_message_text(f"⚙️ Çeviri özelliği şu an: **{durum}**", parse_mode='Markdown')
    elif query.data == 'close_panel':
        await query.message.delete()

# --- ANA ÇALIŞTIRICI ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutlar
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('mp3', mp3_indir))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(CommandHandler('panel', panel))
    
    # Karşılama ve Mesaj Yönetimi
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Buton İşlemleri
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 MeyhanaFM Yayında!")
    app.run_polling()
