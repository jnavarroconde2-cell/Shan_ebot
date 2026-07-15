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
            bot.send_message(msg.chat.id, "❌ Uso: /playaudio nombre de la canción\nEjemplo: /playaudio duki antes de ti")
            return
        
        bot.send_message(msg.chat.id, f"🔍 Buscando: {query}... Espera 10 seg")
        
        filename = f"{uuid.uuid4()}.mp3"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
            'socket_timeout': 15,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            title = info['entries'][0]['title'] if 'entries' in info else info['title']
        
        with open(filename, 'rb') as audio:
            bot.send_audio(msg.chat.id, audio=audio, title=title)
        os.remove(filename)
        bot.send_message(msg.chat.id, f"✅ Listo: {title}")
        
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Error: No se pudo descargar\nPrueba con otro nombre o pega el link de YouTube")
        print("Error:", e)

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.send_message(msg.chat.id, f"Me dijiste: {msg.text}")

print("Bot iniciado correctamente")
bot.infinity_polling()
