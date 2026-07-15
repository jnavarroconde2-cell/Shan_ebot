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

import telebot
import yt_dlp
import os

TOKEN = "AQUI_VA_TU_TOKEN_DE_BOTFATHER" # <- PON TU TOKEN AQUI
bot = telebot.TeleBot(TOKEN)

def get_url(message):
    """Saca el link aunque venga con texto extra de reenviado"""
    parts = message.text.split()
    return parts[1] if len(parts) > 1 else None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot iniciado! Usa /menu para ver todo lo que puedo hacer")

@bot.message_handler(commands=['menu'])
def menu(message):
    texto = """📜 **MENÚ DE COMANDOS**

**Generales**
start - Iniciar el bot
menu - Ver todos los comandos
info - Info del bot
ayuda - Ayuda
hola - Saludo
ping - Ver si el bot responde
owner - Contacto del creador del bot

**Descargas**
playaudio - Descargar audio de YouTube
Uso: /playaudio https://youtube.com/...

tt - Descargar video de TikTok/TikTok Lite sin marca de agua
Uso: /tt https://vm.tiktok.com/...

ttmp3 - Extraer solo el audio MP3 de TikTok/TikTok Lite
Uso: /ttmp3 https://vm.tiktok.com/..."""
    bot.reply_to(message, texto)

@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, "🤖 Soy Shan_ebot\nCreado para descargar videos y audios de TikTok y YouTube")

@bot.message_handler(commands=['ayuda'])
def ayuda(message):
    bot.reply_to(message, "¿Necesitas ayuda? Solo manda /menu y usa los comandos como sale en el ejemplo.")

@bot.message_handler(commands=['hola'])
def hola(message):
    bot.reply_to(message, f"Hola {message.from_user.first_name} 👋 ¿Qué vamos a descargar hoy?")

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 Pong! El bot está vivo")

@bot.message_handler(commands=['owner'])
def owner(message):
    bot.reply_to(message, "👑 Creador: Tu bro\nContacto: @tu_usuario")

@bot.message_handler(commands=['playaudio'])
def playaudio(message):
    url = get_url(message)
    if not url:
        bot.reply_to(message, "❌ Uso: /playaudio https://youtube.com/...")
        return
    bot.reply_to(message, "⏳ Bajando audio de YouTube...")
    # Aquí puedes poner el código de yt-dlp para youtube si quieres

@bot.message_handler(commands=['tt'])
def tt(message):
    url = get_url(message)
    if not url:
        bot.reply_to(message, "❌ Uso: /tt https://vm.tiktok.com/...")
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
            bot.send_video(message.chat.id, video, caption=f"✅ {info.get('title', 'TikTok')} - @{info.get('uploader', 'TikTok')}")

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['ttmp3'])
def ttmp3(message):
    url = get_url(message)
    if not url:
        bot.reply_to(message, "❌ Uso: /ttmp3 https://vm.tiktok.com/...")
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

bot.polling()
