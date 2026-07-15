import telebot
import yt_dlp
import os

TOKEN = "8546862851:AAH7iEfIa2YH6valEM4AJ9yqhXYqCnFuOWc" # <- CAMBIA ESTO
bot = telebot.TeleBot(TOKEN) # <- ESTA LÍNEA ES LA QUE TE FALTA

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot iniciado!")

@bot.message_handler(commands=['menu'])
def menu(message):
    texto = """📜 MENÚ
start - Iniciar el bot
menu - Ver todos los comandos
tt - Descargar video de TikTok sin marca de agua
ttmp3 - Extraer solo el audio MP3 de TikTok"""
    bot.reply_to(message, texto)

@bot.message_handler(commands=['tt'])
def tt(message):
    try:
        url = message.text.split(" ", 1)[1]
    except:
        bot.reply_to(message, "❌ Uso: /tt https://...")
        return
    bot.reply_to(message, "⏳ Bajando video...")
    # aqui va tu codigo de tt

@bot.message_handler(commands=['ttmp3'])
def ttmp3(message):
    try:
        url = message.text.split(" ", 1)[1]
    except:
        bot.reply_to(message, "❌ Uso: /ttmp3 https://...")
        return

    bot.reply_to(message, "⏳ Extrayendo audio...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'tiktok_audio.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit(".", 1)[0] + ".mp3"

        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title', 'TikTok Audio'), performer=info.get('uploader', 'TikTok'))

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.polling() # <- ESTO TAMBIÉN ES IMPORTANTE
