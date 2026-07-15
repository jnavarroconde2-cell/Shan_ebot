import telebot
import yt_dlp
import os

TOKEN = "8546862851:AAH7iEfIa2YH6valEM4AJ9yqhXYqCnFuOWc" # El token de @BotFather
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot iniciado!")

@bot.message_handler(commands=['menu'])
def menu(message):
    texto = """start - Iniciar el bot
menu - Ver todos los comandos
info - Info del bot
ayuda - Ayuda
hola - Saludo
ping - Ver si el bot responde
owner - Contacto del creador del bot
playaudio - Descargar audio de YouTube
tt - Descargar videos de TikTok/TikTok Lite sin marca de agua
Uso: /tt https://vm.tiktok.com/ABC123/"""
    bot.reply_to(message, texto)

@bot.message_handler(commands=['tt'])
def tt(message):
    try:
        url = message.text.split(" ", 1)[1]
    except:
        bot.reply_to(message, "❌ Manda el link así: /tt https://vm.tiktok.com/...")
        return

    bot.reply_to(message, "⏳ Bajando TikTok sin marca de agua...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'tiktok.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"✅ {info.get('title', 'TikTok')}")

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.polling()
