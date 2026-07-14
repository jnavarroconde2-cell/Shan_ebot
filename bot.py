import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Hola! Soy @Shan_ebot 🤖\n\nUsa /menu para ver todos los comandos que tengo")

@bot.message_handler(commands=['menu'])
def menu(msg):
    texto = """**MENU DE COMANDOS**

start - Iniciar el bot
menu - Ver todos los comandos
info - Info del bot
ayuda - Ayuda
hola - Saludo
"""
    bot.reply_to(msg, texto, parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, "Soy @Shan_ebot\nCreado por ti\nActivo 24/7 en Railway ✅")

@bot.message_handler(commands=['ayuda'])
def ayuda(msg):
    bot.reply_to(msg, "¿Necesitas ayuda? Usa /menu para ver todos los comandos disponibles")

@bot.message_handler(commands=['hola'])
def hola(msg):
    bot.reply_to(msg, "Hooola 👋 ¿Cómo estás?")

@bot.message_handler(func=lambda m: True)
def eco(msg):
    bot.reply_to(msg, f"Recibí: {msg.text}\nUsa /menu para ver comandos")

bot.infinity_polling()
