import telebot
import os
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hola! Soy Shan_ebot 🤖\n¿Qué necesitas?")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/start - Iniciar\n/help - Ayuda")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, "Me dijiste: " + message.text)

bot.polling(none_stop=True)
