import telebot
import yt_dlp
import os

TOKEN = "8546862851:AAE25jmlZ2dskHBDRO9UcOz2F41K8lPXJ2U"
bot = telebot.TeleBot(TOKEN)

# 1. /start - Iniciar el bot
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot iniciado! Escribe /menu para ver todos los comandos")

# 2. /menu - Ver todos los comandos
@bot.message_handler(commands=['menu'])
def menu(message):
    texto = """
**SHANE BOT - MENÚ DE COMANDOS**

**Generales:**
/start - Iniciar el bot
/menu - Ver todos los comandos
/info - Info del bot
/ayuda - Ayuda
/hola - Saludo
/ping - Ver si el bot responde
/owner - Contacto del creador del bot

**Descargas:**
/playaudio [link] - Descargar audio de YouTube en MP3
/tt [link] - Descargar videos de TikTok/TikTok Lite sin marca de agua
/ttmp3 [link] - Extraer solo el audio MP3 de un video de TikTok/TikTok Lite

Ejemplo: `/tt https://vm.tiktok.com/ZSXk...`
"""
    bot.reply_to(message, texto, parse_mode="Markdown")

# 3. /info - Info del bot
@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, "**Shane Bot v1.0**\nBot para descargar TikTok y YouTube\nHecho con yt-dlp + ffmpeg", parse_mode="Markdown")

# 4. /ayuda - Ayuda
@bot.message_handler(commands=['ayuda'])
def ayuda(message):
    bot.reply_to(message, "¿Necesitas ayuda?\nSolo mándame un comando del /menu con un link y yo hago el resto")

# 5. /hola - Saludo
@bot.message_handler(commands=['hola'])
def hola(message):
    bot.reply_to(message, "¡Hola! ¿Qué tal? Usa /menu para ver qué puedo hacer")

# 6. /ping - Ver si el bot responde
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "Pong! El bot está activo ✅")

# 7. /owner - Contacto del creador
@bot.message_handler(commands=['owner'])
def owner(message):
    bot.reply_to(message, "**Creador:** DANTE\nContacto: 929 207 065")

# 8. /playaudio - Descargar audio de YouTube
@bot.message_handler(commands=['playaudio'])
def playaudio(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            bot.reply_to(message, "❌ **Uso:** `/playaudio https://youtube.com/...`", parse_mode="Markdown")
            return
        url = partes[1]
        bot.reply_to(message, "Bajando audio de YouTube...")
        
        ydl_opts = {'format': 'bestaudio/best','outtmpl': 'audio.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
        bot.send_audio(message.chat.id, open(filename, 'rb'), title=info['title'])
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# 9. /tt - Descargar videos de TikTok sin marca de agua
@bot.message_handler(commands=['tt'])
def tt(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            bot.reply_to(message, "❌ **Uso:** `/tt https://vm.tiktok.com/...`", parse_mode="Markdown")
            return
        url = partes[1]
        bot.reply_to(message, "Bajando video de TikTok sin marca de agua...")
        
        ydl_opts = {'format': 'best[ext=mp4]','outtmpl': 'video.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        bot.send_video(message.chat.id, open(filename, 'rb'), caption=info['title'])
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# 10. /ttmp3 - Extraer solo audio MP3 de TikTok
@bot.message_handler(commands=['ttmp3'])
def ttmp3(message):
    try:
        partes = message.text.split()
        if len(partes) < 2:
            bot.reply_to(message, "❌ **Uso:** `/ttmp3 https://vm.tiktok.com/...`", parse_mode="Markdown")
            return
        url = partes[1]
        bot.reply_to(message, "Extrayendo audio de TikTok...")
        
        ydl_opts = {'format': 'bestaudio/best','outtmpl': 'audio.%(ext)s','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
        bot.send_audio(message.chat.id, open(filename, 'rb'), title=info['title'])
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.polling()
