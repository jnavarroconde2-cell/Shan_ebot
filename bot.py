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
