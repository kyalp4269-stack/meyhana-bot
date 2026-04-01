import os, threading, http.server, socketserver, yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'

# RENDER İÇİN PORT AÇMA
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_web_server, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 MeyhanaFM Full Paket!\n🤖 Sohbet aktif.\n🎨 /ciz [metin]\n🎵 /cal [isim]\n📥 /mp3 [video linki]")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    if "selam" in msg: await update.message.reply_text("Selam kanka, MeyhanaFM emrinde!")
    elif "nasılsın" in msg: await update.message.reply_text("Bomba gibiyim kanka, sen nasılsın?")
    else: await update.message.reply_text("Dinliyorum kanka...")

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
    if "youtube.com/results" in url: return await update.message.reply_text("❌ Kanka bu arama linki. Bana direkt video linki at!")
    
    m = await update.message.reply_text("⏳ Ses çıkarılıyor...")
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            await update.message.reply_text(f"✅ Hazır! FFmpeg kısıtlaması nedeniyle direkt dosya yerine yüksek kaliteli ses linkini getirdim:\n\n🎧 [Buraya Tıkla ve Dinle/İndir]({audio_url})", parse_mode='Markdown')
            await m.delete()
    except:
        await update.message.reply_text("❌ Linkte bir sorun var veya video bulunamadı.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('mp3', mp3_indir))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    app.run_polling()
