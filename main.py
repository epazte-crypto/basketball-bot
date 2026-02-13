import telebot
import requests
from bs4 import BeautifulSoup
import time
import threading
from datetime import datetime, timedelta
import re
import os

# ============================================
# ТВОИ ДАННЫЕ
# ============================================
TOKEN = '8264651710:AAECvnLSt6ME4A1IOy-GYDMwgdPpt-e1WFg'
CHAT_ID = '787312267'

bot = telebot.TeleBot(TOKEN)
processed_games = set()
total_analyzed = 0

# ============================================
# НАСТРОЙКИ ВРЕМЕНИ (МСК +3)
# ============================================
def get_moscow_time():
    return datetime.utcnow() + timedelta(hours=3)

# ============================================
# ПАРСИНГ FLASHSCORE (РАБОЧАЯ ВЕРСИЯ)
# ============================================
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def parse_flashscore():
    """Парсинг live матчей с FlashScore"""
    global total_analyzed
    
    try:
        url = "https://www.flashscorekz.com/basketball/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем все матчи
            matches = soup.find_all('div', class_='event__match')
            
            for match in matches:
                try:
                    # Парсим команды
                    home = match.find('div', class_='event__homeParticipant')
                    away = match.find('div', class_='event__awayParticipant')
                    
                    # Парсим счет
                    scores = match.find_all('span', class_='event__score')
                    
                    if home and away and len(scores) >= 2:
                        home_name = home.text.strip()
                        away_name = away.text.strip()
                        
                        home_score = int(scores[0].text.strip())
                        away_score = int(scores[1].text.strip())
                        
                        # Создаем ID матча
                        game_id = f"{home_name}_{away_name}_{get_moscow_time().strftime('%Y%m%d%H')}"
                        
                        if game_id not in processed_games:
                            total = home_score + away_score
                            
                            # Проверяем что это 1-я четверть (сумма 20-70 очков)
                            if 20 <= total <= 70:
                                is_even = total % 2 == 0
                                parity = "ЧЕТНАЯ 🟢" if is_even else "НЕЧЕТНАЯ 🔴"
                                
                                msg = (
                                    f"🏀 *{home_name} vs {away_name}*\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📊 *1-я ЧЕТВЕРТЬ ЗАВЕРШЕНА!*\n\n"
                                    f"┌─ {home_name}\n"
                                    f"│ vs\n"
                                    f"└─ {away_name}\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📈 Счет: *{home_score}:{away_score}*\n"
                                    f"📊 Всего очков: *{total}*\n"
                                    f"🎯 Результат: *{parity}*\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🕐 МСК: {get_moscow_time().strftime('%H:%M:%S')}"
                                )
                                
                                bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                                processed_games.add(game_id)
                                total_analyzed += 1
                                print(f"✅ {home_name} vs {away_name} - {parity}")
                                
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"Ошибка FlashScore: {e}")

# ============================================
# КОМАНДЫ БОТА
# ============================================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🏀 *БАСКЕТБОЛЬНЫЙ МОНИТОР*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ Парсинг FlashScore\n"
        "✅ Время: Московское\n\n"
        "📊 *Команды:*\n"
        "• /status - статистика\n"
        "• /test - тест уведомления\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, 
        f"📊 *СТАТИСТИКА РАБОТЫ*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Проанализировано матчей: *{total_analyzed}*\n"
        f"📈 В базе данных: {len(processed_games)}\n"
        f"🕐 МСК: {get_moscow_time().strftime('%H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['test'])
def test(message):
    # Тестовый матч
    test_time = get_moscow_time()
    msg = (
        "🏀 *ТЕСТОВОЕ УВЕДОМЛЕНИЕ*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *1-я ЧЕТВЕРТЬ ЗАВЕРШЕНА!*\n\n"
        "ЦСКА vs Зенит\n"
        "Счет: 24:22\n"
        "Всего очков: *46*\n"
        "Результат: *ЧЕТНАЯ 🟢*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 МСК: {test_time.strftime('%H:%M:%S')}"
    )
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
    bot.reply_to(message, "✅ Тестовое уведомление отправлено!")

# ============================================
# ОСНОВНОЙ ЦИКЛ
# ============================================
def monitoring_loop():
    """Проверка каждые 2 минуты"""
    print("\n" + "="*60)
    print("🏀 БАСКЕТБОЛЬНЫЙ МОНИТОР")
    print("="*60)
    print(f"🚀 Старт: {get_moscow_time().strftime('%Y-%m-%d %H:%M:%S')} МСК")
    print("⏰ Интервал: 2 минуты")
    print("="*60)
    
    while True:
        try:
            print(f"\n🔍 {get_moscow_time().strftime('%H:%M:%S')} МСК - Проверка...")
            parse_flashscore()
            print(f"📊 Всего матчей: {total_analyzed}")
            print(f"⏰ Следующая через 2 минуты...")
            time.sleep(120)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(60)

# ============================================
# ЗАПУСК
# ============================================
if __name__ == "__main__":
    thread = threading.Thread(target=monitoring_loop)
    thread.daemon = True
    thread.start()
    
    print("\n🚀 Бот запущен!")
    print(f"✅ Время МСК: {get_moscow_time().strftime('%H:%M:%S')}")
    print("✅ Команды: /start, /status, /test")
    print("="*60)
    
    bot.infinity_polling()
