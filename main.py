import telebot
import requests
import time
import threading
from datetime import datetime, timedelta, timezone
import os

# ============================================
# ТВОИ ДАННЫЕ
# ============================================
TOKEN = '8264651710:AAECvnLSt6ME4A1IOy-GYDMwgdPpt-e1WFg'
CHAT_ID = '787312267'

# ============================================
# ПОЛНАЯ ОЧИСТКА ВСЕХ ПОДКЛЮЧЕНИЙ
# ============================================
print("🔄 Очистка вебхуков...")
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True"
response = requests.get(url)
print(f"   Статус: {response.status_code}")

time.sleep(2)

# ============================================
# ЗАПУСК БОТА
# ============================================
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(1)

processed = set()
total = 0

def get_time():
    return datetime.now(timezone.utc) + timedelta(hours=3)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Бот работает!\n/status - статистика\n/time - время")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, f"📊 Статистика: {total}")

@bot.message_handler(commands=['time'])
def time_cmd(message):
    bot.reply_to(message, f"🕐 МСК: {get_time().strftime('%H:%M:%S')}")

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(CHAT_ID, "🔔 Тест!")
    bot.reply_to(message, "✅ Отправлено")

print("\n" + "="*50)
print("🚀 БОТ ЗАПУЩЕН")
print(f"🕐 Время МСК: {get_time().strftime('%H:%M:%S')}")
print("="*50)

bot.infinity_polling()
