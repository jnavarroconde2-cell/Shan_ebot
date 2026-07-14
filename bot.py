import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Hola soy Shan 😄 Gusto en conocerte\n¿Qué necesitas? Usa /menu o /ayuda para ver la lista de comandos")

@bot.message_handler(commands=['help', 'menu'])
def menu(msg):
    texto = """SHANE BOT - COMANDOS
General: /start /help /menu /info
Saludos: /hola
Ayuda: /ayuda"""
    bot.reply_to(msg, texto)

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, "Soy @Shan_ebot\nCreado por ti\nActivo 24/7 en Railway ✅")

@bot.message_handler(commands=['ayuda'])
def ayuda(msg):
    bot.reply_to(msg, "¿Necesitas ayuda? Usa /menu para ver todos los comandos disponibles")

@bot.message_handler(commands=['hola'])
def hola(msg):
    bot.reply_to(msg, "Me dijiste: /hola")

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.reply_to(msg, f"Me dijiste: {msg.text}")

bot.infinity_polling()
