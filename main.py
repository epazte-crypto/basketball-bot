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

bot = telebot.TeleBot(TOKEN)
processed_games = set()
total_analyzed = 0

# ============================================
# УДАЛЯЕМ ВЕБХУК (чтоб не было ошибки 409)
# ============================================
bot.remove_webhook()
time.sleep(1)

# ============================================
# НАСТРОЙКИ ВРЕМЕНИ (МСК)
# ============================================
def get_moscow_time():
    """Возвращает текущее московское время"""
    return datetime.now(timezone.utc) + timedelta(hours=3)

# ============================================
# ВСЕ САЙТЫ ДЛЯ ПАРСИНГА
# ============================================
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

SITES = [
    {
        'name': '⚡ FlashScore.kz',
        'url': 'https://www.flashscorekz.com/basketball/',
        'enabled': True
    },
    {
        'name': '📱 FlashScore.mobi',
        'url': 'https://www.flashscore.mobi/basketball/',
        'enabled': True
    },
    {
        'name': '🌍 FlashScore.com',
        'url': 'https://www.flashscore.com/basketball/',
        'enabled': True
    },
    {
        'name': '🇷🇺 FlashScore.ru',
        'url': 'https://www.flashscore.ru/basketball/',
        'enabled': True
    },
    {
        'name': '📊 Sport24',
        'url': 'https://sport24.ru/basketball',
        'enabled': True
    },
    {
        'name': '🏀 Sports.ru',
        'url': 'https://www.sports.ru/basketball/',
        'enabled': True
    }
]

# ============================================
# ПАРСИНГ ВСЕХ САЙТОВ
# ============================================
def parse_all_sites():
    """Парсинг баскетбольных матчей со всех сайтов"""
    global total_analyzed
    found_matches = 0
    
    print(f"\n🔍 {get_moscow_time().strftime('%H:%M:%S')} МСК - НАЧАЛО ПРОВЕРКИ")
    print("="*60)
    
    for site in SITES:
        if not site['enabled']:
            continue
            
        try:
            print(f"   {site['name']}...", end=' ')
            response = requests.get(site['url'], headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Разные сайты могут использовать разные классы
                possible_classes = [
                    'event__match',
                    'match',
                    'live-match',
                    'scoreboard__match',
                    'basketball-match'
                ]
                
                matches = []
                for class_name in possible_classes:
                    matches = soup.find_all('div', class_=re.compile(class_name))
                    if matches:
                        break
                
                site_matches = 0
                for match in matches:
                    try:
                        # Парсим команды
                        home = (match.find('div', class_=re.compile('home')) or 
                               match.find('span', class_=re.compile('home')))
                        away = (match.find('div', class_=re.compile('away')) or 
                               match.find('span', class_=re.compile('away')))
                        
                        # Парсим счет
                        scores = match.find_all('span', class_=re.compile('score'))
                        
                        if home and away and len(scores) >= 2:
                            home_name = home.text.strip()[:30]
                            away_name = away.text.strip()[:30]
                            
                            # Извлекаем числа из счета
                            score_text = scores[0].text.strip()
                            score_numbers = re.findall(r'\d+', score_text)
                            
                            if len(score_numbers) >= 2:
                                home_score = int(score_numbers[0])
                                away_score = int(score_numbers[1])
                                
                                # Создаем ID матча
                                game_id = f"{home_name}_{away_name}_{get_moscow_time().strftime('%Y%m%d%H')}"
                                
                                if game_id not in processed_games:
                                    total = home_score + away_score
                                    
                                    # Проверяем что это 1-я четверть (сумма 20-80 очков)
                                    if 20 <= total <= 80:
                                        is_even = total % 2 == 0
                                        parity = "ЧЕТНАЯ 🟢" if is_even else "НЕЧЕТНАЯ 🔴"
                                        
                                        msg = (
                                            f"🏀 *{home_name} vs {away_name}*\n"
                                            f"━━━━━━━━━━━━━━━━━━━━\n"
                                            f"📊 *1-я ЧЕТВЕРТЬ ЗАВЕРШЕНА!*\n\n"
                                            f"┌─ {home_name}: {home_score}\n"
                                            f"└─ {away_name}: {away_score}\n"
                                            f"━━━━━━━━━━━━━━━━━━━━\n"
                                            f"📊 Всего очков: *{total}*\n"
                                            f"🎯 Результат: *{parity}*\n"
                                            f"━━━━━━━━━━━━━━━━━━━━\n"
                                            f"🕐 МСК: {get_moscow_time().strftime('%H:%M:%S')}"
                                        )
                                        
                                        bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                                        processed_games.add(game_id)
                                        total_analyzed += 1
                                        site_matches += 1
                                        print(f"\n         ✅ {home_name} vs {away_name}")
                                        
                    except Exception as e:
                        continue
                
                print(f" ({site_matches} матчей)")
                found_matches += site_matches
            else:
                print("❌")
                
        except Exception as e:
            print("❌")
        
        time.sleep(2)  # Пауза между сайтами
    
    print(f"📊 ИТОГО: найдено {found_matches} новых матчей")
    print(f"📈 Всего проанализировано: {total_analyzed}")

# ============================================
# КОМАНДЫ БОТА
# ============================================
@bot.message_handler(commands=['start'])
def start(message):
    current_time = get_moscow_time()
    bot.reply_to(message, 
        f"🏀 *БАСКЕТБОЛЬНЫЙ МОНИТОР*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Парсинг 6 сайтов\n"
        f"✅ Проверка каждые 2 минуты\n\n"
        f"📊 *Команды:*\n"
        f"• /status - статистика\n"
        f"• /sites - список сайтов\n"
        f"• /test - тест уведомления\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 МСК: {current_time.strftime('%H:%M:%S')}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['sites'])
def sites(message):
    sites_list = "\n".join([f"• {s['name']}" for s in SITES if s['enabled']])
    bot.reply_to(message, 
        f"🌐 *ОТСЛЕЖИВАЕМЫЕ САЙТЫ*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{sites_list}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ Проверка каждые 2 минуты",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['status'])
def status(message):
    current_time = get_moscow_time()
    bot.reply_to(message, 
        f"📊 *СТАТИСТИКА РАБОТЫ*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Проанализировано матчей: *{total_analyzed}*\n"
        f"📈 В базе данных: {len(processed_games)}\n"
        f"🌐 Активных сайтов: {len([s for s in SITES if s['enabled']])}\n"
        f"🕐 МСК: {current_time.strftime('%H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['test'])
def test(message):
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
# ОСНОВНОЙ ЦИКЛ (КАЖДЫЕ 2 МИНУТЫ)
# ============================================
def monitoring_loop():
    """Проверка всех сайтов каждые 2 минуты"""
    while True:
        try:
            parse_all_sites()
            print(f"\n⏰ Следующая проверка через 2 минуты...")
            print("-"*60)
            time.sleep(120)
        except Exception as e:
            print(f"❌ Ошибка в цикле: {e}")
            time.sleep(60)

# ============================================
# ЗАПУСК
# ============================================
if __name__ == "__main__":
    # Запускаем мониторинг в фоне
    monitor_thread = threading.Thread(target=monitoring_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    print("\n" + "="*60)
    print("🏀 БАСКЕТБОЛЬНЫЙ МОНИТОР v6.0")
    print("="*60)
    print(f"🚀 Запуск: {get_moscow_time().strftime('%Y-%m-%d %H:%M:%S')} МСК")
    print("🌐 Сайтов для парсинга: 6")
    print("⏰ Интервал проверки: 2 минуты")
    print("="*60)
    print("\n✅ Команды в Telegram:")
    print("   /start  - приветствие")
    print("   /status - статистика")
    print("   /sites  - список сайтов")
    print("   /test   - тест уведомления")
    print("="*60)
    
    # Запускаем бота
    bot.infinity_polling()
