import telebot
import os
import yt_dlp
import uuid

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Hola soy Shan 😄 Gusto en conocerte\nUsa /menu para ver comandos")

@bot.message_handler(commands=['help', 'menu'])
def menu(msg):
    texto = """MENU DE COMANDOS

General:
/start - Iniciar el bot
/menu - Ver todos los comandos
/info - Info del bot

Utilidades:
/hola - Saludo
/ping - Ver si el bot responde
/owner - Contacto del creador

Descargas:
/playaudio <nombre o link> - Descargar audio de YouTube"""
    bot.send_message(msg.chat.id, texto)

@bot.message_handler(commands=['info'])
def info(msg):
    bot.send_message(msg.chat.id, "Soy @Shan_ebot\nActivo 24/7 en Railway ✅")

@bot.message_handler(commands=['hola'])
def hola(msg):
    bot.send_message(msg.chat.id, "Hola 👋 ¿Cómo estás?")

@bot.message_handler(commands=['ping'])
def ping(msg):
    bot.send_message(msg.chat.id, "Pong! 🏓 El bot está activo")

@bot.message_handler(commands=['owner'])
def owner(msg):
    bot.send_message(msg.chat.id, "Contacto del creador:\n929 207 065")

@bot.message_handler(commands=['playaudio'])
def playaudio(msg):
    query = msg.text.replace('/playaudio', '').strip()
    if not query:
        bot.send_message(msg.chat.id, "❌ Uso: /playaudio nombre de la canción\nEjemplo: /playaudio funk tonta")
        return
    
    wait_msg = bot.send_message(msg.chat.id, f"🔍 Buscando: {query}...")
    
    try:
        filename = f"{uuid.uuid4()}.mp3"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'cookiefile': 'cookies.txt', # <-- ESTO ES LA CLAVE
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
            'extractor_retries': 3,
            'socket_timeout': 15,
            'geo_bypass': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            title = info['entries'][0]['title'] if 'entries' in info else info['title']
        
        bot.delete_message(msg.chat.id, wait_msg.message_id)
        bot.send_message(msg.chat.id, f"⬇️ Enviando: {title}")
        
        with open(filename, 'rb') as audio:
            bot.send_audio(msg.chat.id, audio=audio, title=title)
        os.remove(filename)
        
    except Exception as e:
        bot.delete_message(msg.chat.id, wait_msg.message_id)
        bot.send_message(msg.chat.id, f"❌ Error al descargar\nRevisa que `cookies.txt` esté subido")
        print("Error:", e)

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.send_message(msg.chat.id, f"Me dijiste: {msg.text}")

print("Bot iniciado correctamente")
bot.infinity_polling()
