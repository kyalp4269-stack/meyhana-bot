import os, threading, http.server, socketserver, yt_dlp, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# --- AYARLAR ---
TOKEN = '8775448432:AAEI553SIDjcBZuTfrX6jpFSswVGbZzS7f8'
ADMIN_ID = 0 

settings = {
    "total_messages": 0,
    "users": set(),
    "command_usage": {},
    "start_time": time.time()
}

def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_web_server, daemon=True).start()

def track_stats(command):
    settings["command_usage"][command] = settings["command_usage"].get(command, 0) + 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("start")
    user = update.effective_user
    welcome_text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"     ✨ **MEYHANAFM V2.0** ✨\n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Selam **{user.first_name}**, MeyhanaFM'e hoş geldin!\n"
        f"🎨 `/ciz` - Hayalini resme dök\n"
        f"🎵 `/cal` - Şarkı ara\n"
        f"📊 `/istatistik` - Durum raporu\n\n"
        f"✨ *Kurucu:* **Alperen KAYA**"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def ciz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("ciz")
    p = "+".join(context.args)
    if not p: return await update.message.reply_text("🤔 **Ne çizmemi istersin?**", parse_mode='Markdown')
    m = await update.message.reply_text("🎨 **Çiziyorum...**")
    await update.message.reply_photo(f"https://pollinations.ai/p/{p}", caption=f"✨ Sonuç: *{p}*", parse_mode='Markdown')
    await m.delete()

async def cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_stats("cal")
    s = " ".join(context.args)
    if not s: return await update.message.reply_text("🎵 **Şarkı adı?**", parse_mode='Markdown')
    search_url = f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}"
    await update.message.reply_text(f"🔍 **'{s}'** için sonuçlar:\n📺 [İzle/Dinle]({search_url})", parse_mode='Markdown')

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int((time.time() - settings["start_time"]) / 60)
    stats_text = (
        f"📊 **MEYHANAFM ANALİZ**\n"
        f"📩 Mesaj: `{settings['total_messages']}`\n"
        f"👥 Kişi: `{len(settings['users'])}` kişi\n"
        f"⏱ Uyanık: `{uptime} dk`"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    settings["total_messages"] += 1
    settings["users"].add(update.message.from_user.id)
    if "selam" in update.message.text.lower():
        await update.message.reply_text(f"Selam kanka **{update.message.from_user.first_name}**! 🍻", parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ciz', ciz))
    app.add_handler(CommandHandler('cal', cal))
    app.add_handler(CommandHandler('istatistik', istatistik))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🚀 MeyhanaFM Yayında!")
    app.run_polling()
