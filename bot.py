import telebot
import os

bot = telebot.TeleBot("TOKEN_BURAYA")

# Başlangıç Mesajı (Eski menü stilinde)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ **MEYHANAFM V3.5** ✨\n\n"
        "🎵 `/cal` - MP3 gönderir\n"
        "🎬 `/video` - Video gönderir\n"
        "📊 `/istatistik` - Durum raporu\n\n"
        "🍻 Link atman yeterli, otomatik MP3 yaparım!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# Video Komutu
@bot.message_handler(commands=['video'])
def handle_video(message):
    # Video indirme ve gönderme mantığını buraya ekle
    bot.reply_to(message, "Video işleniyor, lütfen bekleyin...")

# MP3 / Müzik Komutu
@bot.message_handler(commands=['cal'])
def handle_audio(message):
    # Ses indirme ve gönderme mantığını buraya ekle
    bot.reply_to(message, "Müzik hazırlanıyor...")

# Otomatik Link Algılama (Yalnızca link atıldığında)
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def auto_download(message):
    # Burada otomatik MP3 dönüştürme fonksiyonunu çağır
    bot.reply_to(message, "Link algılandı! MP3 olarak hazırlanıyor...")

bot.infinity_polling()
