import telebot
import os

TOKEN = '8264651710:AAECvnLSt6ME4A1IOy-GYDMwgdPpt-e1WFg'
CHAT_ID = '787312267'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Бот работает!")

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(CHAT_ID, "🔔 Тест!")
    bot.reply_to(message, "✅ Отправлено!")

print("Бот запущен!")
bot.polling()
