import telebot
import requests
from bs4 import BeautifulSoup
import time
import threading
from datetime import datetime, timedelta, timezone
import re
import os

# ============================================
# ТВОИ ДАННЫЕ
# ============================================
TOKEN = '8264651710:AAECvnLSt6ME4A1IOy-GYDMwgdPpt-e1WFg'
CHAT_ID = '787312267'

# Очистка вебхуков
requests.post(f'https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True')
time.sleep(1)

bot = telebot.TeleBot(TOKEN)
processed_games = set()
total_analyzed = 0

# ============================================
# ВРЕМЯ
# ============================================
def get_moscow_time():
    return datetime.now(timezone.utc) + timedelta(hours=3)

# ============================================
# ПРОСТОЙ ПАРСИНГ
# ============================================
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def parse_simple():
    global total_analyzed
    print(f"\n🔍 {get_moscow_time().strftime('%H:%M:%S')} МСК")
    
    # Пробуем один сайт
    url = "https://www.flashscorekz.com/basketball/"
    
    try:
        print("   Загрузка FlashScore...", end=' ')
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            print("OK")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем все строки с матчами
            text = soup.get_text()
            print(f"   Текст страницы: {len(text)} символов")
            
            # Ищем счет (цифры:цифры)
            scores = re.findall(r'(\d+)[:-](\d+)', text)
            print(f"   Найдено счетов: {len(scores)}")
            
            # Покажем первые 5 найденных счетов
            for i, score in enumerate(scores[:5]):
                print(f"   Счет {i+1}: {score[0]}:{score[1]}")
                
        else:
            print(f"Ошибка {response.status_code}")
            
    except Exception as e:
        print(f"Ошибка: {e}")

# ============================================
# КОМАНДЫ
# ============================================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🏀 Бот в тестовом режиме")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, f"📊 Статистика: {total_analyzed}")

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(CHAT_ID, "🔔 Тест!")
    bot.reply_to(message, "✅ Отправлено")

@bot.message_handler(commands=['parse'])
def force_parse(message):
    """Принудительный парсинг"""
    parse_simple()
    bot.reply_to(message, "✅ Проверка выполнена, смотри логи")

# ============================================
# ЦИКЛ
# ============================================
def monitoring():
    while True:
        parse_simple()
        time.sleep(120)

thread = threading.Thread(target=monitoring)
thread.daemon = True
thread.start()

print("\n" + "="*50)
print("🚀 ТЕСТОВЫЙ РЕЖИМ")
print("="*50)
bot.infinity_polling()
