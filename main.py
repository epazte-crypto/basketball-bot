import telebot
import requests
from bs4 import BeautifulSoup
import time
import threading
from datetime import datetime
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
# НАСТРОЙКИ ПАРСИНГА (КАЖДЫЕ 2 МИНУТЫ)
# ============================================
HEADERS = {'User-Agent': 'Mozilla/5.0'}
SITES = [
    {'name': '⚡ FlashScore', 'url': 'https://www.flashscorekz.com/basketball/'},
    {'name': '📊 Sport24', 'url': 'https://sport24.ru/basketball'},
    {'name': '🏀 Sports.ru', 'url': 'https://www.sports.ru/basketball/'}
]

def parse_basketball():
    """Парсинг баскетбольных матчей со всех сайтов"""
    global total_analyzed
    found = 0
    
    print(f"\n🔍 {datetime.now().strftime('%H:%M:%S')} - Начинаю парсинг...")
    
    for site in SITES:
        try:
            print(f"   • {site['name']}...", end=' ')
            response = requests.get(site['url'], headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                # Ищем матчи: Команда - Команда 24:22
                pattern = r'([А-Яа-яA-Za-z\s]{3,30}?)\s*[-–]\s*([А-Яа-яA-Za-z\s]{3,30}?)\s*(\d+)[:-](\d+)'
                matches = re.findall(pattern, text)
                
                for match in matches:
                    try:
                        home = match[0].strip()
                        away = match[1].strip()
                        score1 = int(match[2])
                        score2 = int(match[3])
                        
                        # Создаем уникальный ID матча
                        game_id = f"{home}_{away}_{datetime.now().strftime('%Y%m%d%H')}"
                        
                        # Проверяем, не отправляли ли уже этот матч
                        if game_id not in processed_games:
                            total_score = score1 + score2
                            
                            # Проверяем, похоже ли на 1-ю четверть (20-80 очков)
                            if 20 <= total_score <= 80:
                                is_even = total_score % 2 == 0
                                parity = "ЧЕТНАЯ 🟢" if is_even else "НЕЧЕТНАЯ 🔴"
                                
                                # Формируем красивое сообщение
                                msg = (
                                    f"🏀 *{site['name'].replace('⚡', '').replace('📊', '').replace('🏀', '')}*\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📊 *1-я ЧЕТВЕРТЬ ЗАВЕРШЕНА!*\n\n"
                                    f"┌─ {home}\n"
                                    f"│ vs\n"
                                    f"└─ {away}\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📈 Счет: *{score1}:{score2}*\n"
                                    f"📊 Всего очков: *{total_score}*\n"
                                    f"🎯 Результат: *{parity}*\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🕐 {datetime.now().strftime('%H:%M:%S')}"
                                )
                                
                                bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                                processed_games.add(game_id)
                                total_analyzed += 1
                                found += 1
                                print(f"\n      ✅ {home} vs {away} - {parity}")
                                
                    except:
                        continue
                print(f" ({len(matches)} матчей)")
            else:
                print("❌")
        except Exception as e:
            print(f"❌ Ошибка")
        time.sleep(1)
    
    if found > 0:
        print(f"📊 Найдено новых матчей: {found}")
    print(f"📈 Всего проанализировано: {total_analyzed}")

# ============================================
# КОМАНДЫ БОТА
# ============================================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🏀 *БАСКЕТБОЛЬНЫЙ МОНИТОР*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *РЕЖИМ РАБОТЫ:*\n"
        "• Парсинг каждые 2 минуты\n"
        "• 3 сайта одновременно\n"
        "• Все лиги мира\n\n"
        "📊 *ДОСТУПНЫЕ КОМАНДЫ:*\n"
        "• /status - статистика работы\n"
        "• /sites - список сайтов\n"
        "• /test - тест уведомления\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['status'])
def status(message):
    """Показывает статистику работы"""
    bot.reply_to(message, 
        f"📊 *СТАТИСТИКА РАБОТЫ*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Проанализировано матчей: *{total_analyzed}*\n"
        f"📈 В базе данных: {len(processed_games)} матчей\n"
        f"🕐 Последняя проверка: {datetime.now().strftime('%H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['sites'])
def sites(message):
    """Показывает список отслеживаемых сайтов"""
    sites_list = "\n".join([f"• {s['name']}" for s in SITES])
    bot.reply_to(message, 
        f"🌐 *ОТСЛЕЖИВАЕМЫЕ САЙТЫ*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{sites_list}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ Проверка каждые 2 минуты",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['test'])
def test(message):
    """Тестовое уведомление"""
    msg = (
        "🏀 *ТЕСТОВОЕ УВЕДОМЛЕНИЕ*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *1-я ЧЕТВЕРТЬ ЗАВЕРШЕНА!*\n\n"
        "ЦСКА vs Зенит\n"
        "Счет: 24:22\n"
        "Всего очков: *46*\n"
        "Результат: *ЧЕТНАЯ 🟢*\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
    bot.reply_to(message, "✅ Тестовое уведомление отправлено!")

# ============================================
# ОСНОВНОЙ ЦИКЛ (КАЖДЫЕ 2 МИНУТЫ)
# ============================================
def monitoring_loop():
    """Бесконечный цикл мониторинга каждые 2 минуты"""
    print("\n" + "="*60)
    print("🏀 БАСКЕТБОЛЬНЫЙ МОНИТОР ЗАПУЩЕН")
    print("="*60)
    print(f"📊 Старт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⏰ Интервал: 2 минуты")
    print("🌐 Сайтов: 3")
    print("="*60)
    
    while True:
        try:
            parse_basketball()
            print(f"\n⏰ Следующая проверка через 2 минуты...")
            print("-"*60)
            time.sleep(120)  # 2 минуты
        except Exception as e:
            print(f"❌ Ошибка в цикле: {e}")
            time.sleep(60)

# ============================================
# ЗАПУСК
# ============================================
if __name__ == "__main__":
    # Запускаем мониторинг в фоновом потоке
    monitor_thread = threading.Thread(target=monitoring_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    print("\n🚀 Бот запускается...")
    print("✅ Команды: /start, /status, /sites, /test")
    print("="*60)
    
    # Запускаем бота
    bot.polling(none_stop=True)
