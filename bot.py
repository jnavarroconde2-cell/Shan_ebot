import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Hola soy Shan 😄 Gusto en conocerte\n¿Qué necesitas?\nUsa /menu o /ayuda para ver la lista de comandos")

@bot.message_handler(commands=['help', 'menu'])
def menu(msg):
    texto = """MENU DE COMANDOS

General:
/start - Iniciar el bot
/menu - Ver todos los comandos
/info - Info del bot
/ayuda - Ayuda

Utilidades:
/hola - Saludo
/ping - Ver si el bot responde
/owner - Contacto del creador del bot"""
    bot.reply_to(msg, texto)

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, "Soy @Shan_ebot\nCreado por ti\nActivo 24/7 en Railway ✅")

@bot.message_handler(commands=['ayuda'])
def ayuda(msg):
    bot.reply_to(msg, "¿Necesitas ayuda? Usa /menu para ver todos los comandos disponibles")

@bot.message_handler(commands=['hola'])
def hola(msg):
    bot.reply_to(msg, "Hola 👋 ¿Cómo estás?")

@bot.message_handler(commands=['ping'])
def ping(msg):
    bot.reply_to(msg, "Pong! 🏓 El bot está activo")

@bot.message_handler(commands=['owner'])
def owner(msg):
    bot.reply_to(msg, "Contacto del creador del bot:\n929 207 065")

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.reply_to(msg, f"Me dijiste: {msg.text}")

bot.infinity_polling()

import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    print("Comando start detectado") # Para debug en Railway
    bot.send_message(msg.chat.id, "Hola soy Shan 😄 Gusto en conocerte\n¿Qué necesitas?\nUsa /menu o /ayuda para ver la lista de comandos")

@bot.message_handler(commands=['help', 'menu'])
def menu(msg):
    texto = """MENU DE COMANDOS

General:
/start - Iniciar el bot
/menu - Ver todos los comandos
/info - Info del bot
/ayuda - Ayuda

Utilidades:
/hola - Saludo
/ping - Ver si el bot responde
/owner - Contacto del creador del bot"""
    bot.send_message(msg.chat.id, texto)

@bot.message_handler(commands=['info'])
def info(msg):
    bot.send_message(msg.chat.id, "Soy @Shan_ebot\nCreado por ti\nActivo 24/7 en Railway ✅")

@bot.message_handler(commands=['ayuda'])
def ayuda(msg):
    bot.send_message(msg.chat.id, "¿Necesitas ayuda? Usa /menu para ver todos los comandos disponibles")

@bot.message_handler(commands=['hola'])
def hola(msg):
    bot.send_message(msg.chat.id, "Hola 👋 ¿Cómo estás?")

@bot.message_handler(commands=['ping'])
def ping(msg):
    bot.send_message(msg.chat.id, "Pong! 🏓 El bot está activo")

@bot.message_handler(commands=['owner'])
def owner(msg):
    bot.send_message(msg.chat.id, "Contacto del creador del bot:\n929 207 065")

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.send_message(msg.chat.id, f"Me dijiste: {msg.text}")

print("Bot iniciado y escuchando...")
bot.infinity_polling()

import telebot
import os
import yt_dlp
import uuid

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Hola soy Shan 😄 Gusto en conocerte\n¿Qué necesitas?\nUsa /menu o /ayuda para ver la lista de comandos")

@bot.message_handler(commands=['help', 'menu'])
def menu(msg):
    texto = """MENU DE COMANDOS

General:
/start - Iniciar el bot
/menu - Ver todos los comandos
/info - Info del bot
/ayuda - Ayuda

Utilidades:
/hola - Saludo
/ping - Ver si el bot responde
/owner - Contacto del creador del bot

Descargas:
/playaudio <nombre> - Descargar audio de YouTube"""
    bot.send_message(msg.chat.id, texto)

@bot.message_handler(commands=['info'])
def info(msg):
    bot.send_message(msg.chat.id, "Soy @Shan_ebot\nCreado por ti\nActivo 24/7 en Railway ✅")

@bot.message_handler(commands=['ayuda'])
def ayuda(msg):
    bot.send_message(msg.chat.id, "¿Necesitas ayuda? Usa /menu para ver todos los comandos disponibles")

@bot.message_handler(commands=['hola'])
def hola(msg):
    bot.send_message(msg.chat.id, "Hola 👋 ¿Cómo estás?")

@bot.message_handler(commands=['ping'])
def ping(msg):
    bot.send_message(msg.chat.id, "Pong! 🏓 El bot está activo")

@bot.message_handler(commands=['owner'])
def owner(msg):
    bot.send_message(msg.chat.id, "Contacto del creador del bot:\n929 207 065")

@bot.message_handler(commands=['playaudio'])
def playaudio(msg):
    try:
        query = msg.text.replace('/playaudio', '').strip()
        if not query:
            bot.send_message(msg.chat.id, "Uso: /playaudio nombre de la canción")
            return
        
        bot.send_message(msg.chat.id, f"🔍 Buscando: {query}...")
        
        filename = f"{uuid.uuid4()}.mp3"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1', # Busca solo el primer resultado
            'extract_flat': False,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            title = info['entries'][0]['title'] if 'entries' in info else info['title']
        
        bot.send_audio(msg.chat.id, audio=open(filename, 'rb'), title=title)
        os.remove(filename)
        
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Error: No se pudo descargar\nIntenta con otro nombre")
        print(e)

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.send_message(msg.chat.id, f"Me dijiste: {msg.text}")

bot.infinity_polling()
