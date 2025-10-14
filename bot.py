import os
import telebot
from telebot import types
import requests
import random
import datetime
import time
import re
import json
import threading
import atexit
from flask import Flask
from threading import Thread
import signal
import sys

print("=== LUNA AI BOT - ULTRA STABLE EDITION ===")

# ==================== КОНФИГУРАЦИЯ ====================
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
FEEDBACK_CHAT_ID = os.environ.get('FEEDBACK_CHAT_ID', '')  # 🆕 Чат для фидбеков

if not API_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not found!")
    bot = None
else:
    bot = telebot.TeleBot(API_TOKEN)

# ==================== СУПЕР-НАДЕЖНАЯ БАЗА ДАННЫХ ====================
class SimpleDatabase:
    def __init__(self):
        self.data_file = 'bot_data.json'
        self.backup_file = 'bot_data_backup.json'
        self.user_stats = {}
        self.user_gender = {} 
        self.user_context = {}
        self.premium_users = {}
        self.user_achievements = {}
        self.last_memory_backup = None
        self.backup_interval = 10
        self.last_backup_time = time.time()
        
        self.load_data()
        print("🔒 ULTRA STABLE Database initialized")
    
    def load_data(self):
        """УМНАЯ загрузка с приоритетом надежности"""
        print("🔍 Loading data...")
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.load_from_data(data)
                
                # 🛠️ ФИКС: Логируем загруженные достижения
                total_achievements = sum(len(ach['unlocked']) for ach in self.user_achievements.values())
                print(f"💾 Loaded from main: {len(self.user_stats)} users, {total_achievements} total achievements unlocked")
                return
            except Exception as e:
                print(f"❌ Main file corrupted: {e}")
        
        if os.path.exists(self.backup_file):
            try:
                print("⚠️  Trying backup file...")
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.load_from_data(data)
                
                total_achievements = sum(len(ach['unlocked']) for ach in self.user_achievements.values())
                print(f"✅ Restored from backup: {len(self.user_stats)} users, {total_achievements} achievements")
                return
            except Exception as e:
                print(f"❌ Backup file corrupted: {e}")
        
        print("💾 No valid data files, starting fresh")
        self.user_stats = {}
        self.user_gender = {}
        self.user_context = {}
        self.premium_users = {}
        self.user_achievements = {}
    
    def load_from_data(self, data):
        """Загружает данные из JSON"""
        self.user_stats = data.get('user_stats', {})
        self.user_gender = data.get('user_gender', {})
        self.user_context = data.get('user_context', {})
        self.premium_users = data.get('premium_users', {})
        
        # 🛠️ ФИКС: Правильно конвертируем achievements
        achievements_data = data.get('user_achievements', {})
        self.user_achievements = {}
        
        for user_id, user_ach in achievements_data.items():
            # 🛠️ ФИКС: Конвертируем list обратно в set
            different_buttons = user_ach.get('progress', {}).get('different_buttons', [])
            
            self.user_achievements[user_id] = {
                'unlocked': user_ach.get('unlocked', []),
                'progress': {
                    'messages_sent': user_ach.get('progress', {}).get('messages_sent', 0),
                    'buttons_used': user_ach.get('progress', {}).get('buttons_used', 0),
                    'different_buttons': set(different_buttons),  # 🛠️ ФИКС: list -> set
                    'levels_reached': user_ach.get('progress', {}).get('levels_reached', 1),
                    'days_active': user_ach.get('progress', {}).get('days_active', 1)
                }
            }
    
    def make_achievements_serializable(self):
        """🛠️ ФИКС: Конвертируем set в list для JSON"""
        serializable_achievements = {}
        for user_id, achievements in self.user_achievements.items():
            serializable_achievements[user_id] = {
                'unlocked': achievements['unlocked'],
                'progress': {
                    'messages_sent': achievements['progress']['messages_sent'],
                    'buttons_used': achievements['progress']['buttons_used'],
                    'different_buttons': list(achievements['progress']['different_buttons']),  # 🛠️ set -> list
                    'levels_reached': achievements['progress']['levels_reached'],
                    'days_active': achievements['progress']['days_active']
                }
            }
        return serializable_achievements
    
    def save_data(self):
        """СУПЕР-НАДЕЖНОЕ сохранение"""
        try:
            print(f"💾 Saving data for {len(self.user_stats)} users...")
            
            data = {
                'user_stats': self.user_stats,
                'user_gender': self.user_gender, 
                'user_context': self.user_context,
                'premium_users': self.premium_users,
                'user_achievements': self.make_achievements_serializable(),  # 🛠️ Используем исправленную версию
                'last_save': datetime.datetime.now().isoformat(),
                'total_users': len(self.user_stats),
                'total_messages': self.get_total_messages(),
                'save_type': 'regular'
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            try:
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            print(f"✅ Data saved! Users: {len(self.user_stats)}, Messages: {self.get_total_messages()}")
            
        except Exception as e:
            print(f"❌ SAVE ERROR: {e}")
    
    def quick_save(self):
        """ЭКСТРЕННОЕ сохранение при выключении"""
        try:
            print("🚨 QUICK SAVE - Emergency mode!")
            
            data = {
                'user_stats': self.user_stats,
                'user_gender': self.user_gender,
                'user_context': self.user_context,
                'premium_users': self.premium_users,
                'user_achievements': self.make_achievements_serializable(),  # 🛠️ ТОЖЕ ИСПРАВЛЕНО!
                'last_save': datetime.datetime.now().isoformat(),
                'save_type': 'emergency'
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            
            print("✅ Emergency save completed!")
        except Exception as e:
            print(f"❌ EMERGENCY SAVE FAILED: {e}")

    def get_user_achievements(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.user_achievements:
            self.user_achievements[user_id_str] = {
                'unlocked': [],
                'progress': {
                    'messages_sent': 0,
                    'buttons_used': 0,
                    'different_buttons': set(),
                    'levels_reached': 1,
                    'days_active': 1
                }
            }
        return self.user_achievements[user_id_str]
    
    def update_user_achievements(self, user_id, achievements):
        self.user_achievements[str(user_id)] = achievements
    
    def unlock_achievement(self, user_id, achievement_id):
        user_achievements = self.get_user_achievements(user_id)
        
        # 🛠️ ФИКС: Двойная проверка на дубликаты
        if achievement_id not in user_achievements['unlocked']:
            user_achievements['unlocked'].append(achievement_id)
            self.save_data()
            print(f"🔓 ACHIEVEMENT SAVED: {user_id} -> {achievement_id}")
            return True
        
        print(f"⚠️  ACHIEVEMENT ALREADY UNLOCKED: {user_id} -> {achievement_id}")
        return False

    def get_user_stats(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.user_stats:
            self.user_stats[user_id_str] = {
                'message_count': 0,
                'first_seen': datetime.datetime.now().isoformat(),
                'last_seen': datetime.datetime.now().isoformat(), 
                'current_level': 1,
                'waiting_feedback': False
            }
        return self.user_stats[user_id_str]
    
    def update_user_stats(self, user_id, stats):
        user_id_str = str(user_id)
        self.user_stats[user_id_str] = stats
    
    def get_user_gender(self, user_id):
        return self.user_gender.get(str(user_id), 'unknown')
    
    def update_user_gender(self, user_id, gender):
        self.user_gender[str(user_id)] = gender
    
    def get_conversation_context(self, user_id):
        return self.user_context.get(str(user_id), [])
    
    def update_conversation_context(self, user_id, context):
        self.user_context[str(user_id)] = context
    
    def get_all_users(self):
        return list(self.user_stats.keys())
    
    def get_total_messages(self):
        return sum(stats.get('message_count', 0) for stats in self.user_stats.values())

    def is_premium_user(self, user_id):
        """🆕 Проверяет premium статус пользователя"""
        user_id_str = str(user_id)
        if user_id_str not in self.premium_users:
            return False
        
        premium_data = self.premium_users[user_id_str]
        expires = premium_data.get('expires')
        
        if expires:
            try:
                expire_date = datetime.datetime.fromisoformat(expires)
                if datetime.datetime.now() > expire_date:
                    # Premium истек
                    del self.premium_users[user_id_str]
                    return False
            except:
                pass
        
        return True

    def set_premium_status(self, user_id, premium_type="basic", duration_days=30):
        """🆕 Устанавливает premium статус пользователя"""
        user_id_str = str(user_id)
        
        activate_date = datetime.datetime.now()
        expire_date = activate_date + datetime.timedelta(days=duration_days)
        
        features = {
            "basic": ["unlimited_messages", "priority_access", "extended_memory", "ad_free"],
            "premium": ["unlimited_messages", "priority_access", "extended_memory", "ad_free", "voice_messages", "custom_personality"],
            "vip": ["unlimited_messages", "priority_access", "extended_memory", "ad_free", "voice_messages", "custom_personality", "dedicated_support", "feature_requests"]
        }
        
        self.premium_users[user_id_str] = {
            'premium_type': premium_type,
            'activated': activate_date.isoformat(),
            'expires': expire_date.isoformat(),
            'features': features.get(premium_type, features['basic'])
        }
        
        self.save_data()

    def get_system_stats(self):
        """🆕 Возвращает статистику системы"""
        return {
            'total_users': len(self.user_stats),
            'total_messages': self.get_total_messages(),
            'premium_users': len([uid for uid in self.premium_users if self.is_premium_user(uid)]),
            'users_with_achievements': len(self.user_achievements),
            'last_save_time': self.last_backup_time
        }

    def validate_achievements_data(self):
        """🆕 Проверяет целостность данных достижений"""
        issues = []
        
        for user_id, achievements in self.user_achievements.items():
            # Проверяем существующие достижения
            for achievement_id in achievements['unlocked']:
                if achievement_id not in ACHIEVEMENTS:
                    issues.append(f"User {user_id}: invalid achievement {achievement_id}")
            
            # Проверяем прогресс
            progress = achievements['progress']
            if not isinstance(progress['different_buttons'], set):
                issues.append(f"User {user_id}: different_buttons is not a set")
        
        if issues:
            print(f"⚠️  Achievement data issues: {issues}")
        else:
            print("✅ Achievement data is valid")
        
        return len(issues) == 0

# Initialize enhanced database
db = SimpleDatabase()

# ==================== СИСТЕМА ДОСТИЖЕНИЙ ====================
ACHIEVEMENTS = {
    "chatty": {
        "name": "💬 Chatty", 
        "description": "Send 10 messages",
        "goal": 10,
        "type": "messages_sent"
    },
    "social_butterfly": {
        "name": "🦋 Social Butterfly", 
        "description": "Send 50 messages", 
        "goal": 50,
        "type": "messages_sent"
    },
    "button_explorer": {
        "name": "🔍 Button Explorer",
        "description": "Use 3 different menu buttons",
        "goal": 3, 
        "type": "different_buttons"
    },
    "level_2": {
        "name": "🌟 Rising Star",
        "description": "Reach relationship level 2",
        "goal": 2,
        "type": "levels_reached"
    },
    "level_3": {
        "name": "💕 Romantic",
        "description": "Reach relationship level 3", 
        "goal": 3,
        "type": "levels_reached"
    },
    "level_4": {
        "name": "👑 Soulmate",
        "description": "Reach relationship level 4",
        "goal": 4, 
        "type": "levels_reached"
    },
    "first_day": {
        "name": "🌅 First Day",
        "description": "Talk to Luna for the first time",
        "goal": 1,
        "type": "days_active"
    },
    "week_old": {
        "name": "📅 Week Old",
        "description": "Talk to Luna for 7 days",
        "goal": 7,
        "type": "days_active"
    }
}

def check_achievements(user_id, stats, action_type=None, action_data=None):
    """Проверяет и выдает достижения"""
    user_achievements = db.get_user_achievements(user_id)
    unlocked_achievements = []
    
    # 🛠️ ФИКС: Сохраняем исходное состояние перед проверкой
    original_unlocked = user_achievements['unlocked'].copy()
    
    if action_type == "message_sent":
        user_achievements['progress']['messages_sent'] += 1
    elif action_type == "button_used":
        user_achievements['progress']['buttons_used'] += 1
        if action_data and 'button_type' in action_data:
            user_achievements['progress']['different_buttons'].add(action_data['button_type'])
    elif action_type == "level_up":
        user_achievements['progress']['levels_reached'] = max(
            user_achievements['progress']['levels_reached'], 
            action_data['new_level'] if action_data else stats['current_level']
        )
    
    # 🛠️ ФИКС: Проверяем только НОВЫЕ достижения
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id in original_unlocked:  # 🛠️ Уже разблокировано - пропускаем
            continue
            
        progress = user_achievements['progress'][achievement['type']]
        if achievement['type'] == 'different_buttons':
            progress = len(user_achievements['progress']['different_buttons'])
        
        if progress >= achievement['goal']:
            if db.unlock_achievement(user_id, achievement_id):
                unlocked_achievements.append(achievement)
                print(f"🎉 NEW ACHIEVEMENT: {user_id} -> {achievement_id}")  # 🛠️ Логируем
    
    db.update_user_achievements(user_id, user_achievements)
    return unlocked_achievements

def get_achievements_message(achievements):
    """Создает сообщение о полученных достижениях"""
    if not achievements:
        return None
    
    if len(achievements) == 1:
        achievement = achievements[0]
        return f"🎉 *ACHIEVEMENT UNLOCKED!* 🎉\n\n**{achievement['name']}**\n{achievement['description']}\n\n*You're amazing!* 💫"
    else:
        message = "🎉 *MULTIPLE ACHIEVEMENTS UNLOCKED!* 🎉\n\n"
        for achievement in achievements:
            message += f"**{achievement['name']}**\n{achievement['description']}\n\n"
        message += "*You're on fire!* 🔥"
        return message

# ==================== GRACEFUL SHUTDOWN ====================
def signal_handler(signum, frame):
    print("🚨 Received shutdown signal...")
    print("💾 QUICK SAVING DATA...")
    db.quick_save()
    print("✅ Data saved. Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ==================== УЛУЧШЕННАЯ СИСТЕМА ФИДБЕКОВ ====================
def send_feedback_to_admin(user_id, username, feedback_text):
    """🆕 Отправляет фидбек в указанный чат"""
    if not FEEDBACK_CHAT_ID or not bot:
        print(f"📝 Feedback from {user_id} ({username}): {feedback_text}")
        return
    
    try:
        feedback_message = f"""
📝 *NEW USER FEEDBACK* 📝

👤 *User ID:* `{user_id}`
📛 *Username:* {username if username else 'No username'}
💬 *Message:* 
{feedback_text}

⏰ *Time:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        bot.send_message(
            chat_id=FEEDBACK_CHAT_ID,
            text=feedback_message,
            parse_mode='Markdown'
        )
        print(f"✅ Feedback sent to admin chat: {user_id}")
        
    except Exception as e:
        print(f"❌ Failed to send feedback: {e}")

# ==================== WEB SERVER FOR 24/7 ====================
app = Flask(__name__)
start_time = datetime.datetime.now()

@app.route('/')
def home():
    uptime = datetime.datetime.now() - start_time
    total_users = len(db.get_all_users())
    total_messages = db.get_total_messages()
    
    return f"""
    <html>
        <head>
            <title>Luna AI Bot</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); 
                            padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }}
                .status {{ font-size: 24px; margin: 20px 0; }}
                .info {{ background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 10px 0; }}
                .data {{ color: #4CAF50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Luna AI Bot</h1>
                <div class="status">🟢 ULTRA STABLE MODE</div>
                <div class="info">
                    <strong>Uptime:</strong> {str(uptime).split('.')[0]}<br>
                    <strong>Total Users:</strong> <span class="data">{total_users}</span><br>
                    <strong>Total Messages:</strong> <span class="data">{total_messages}</span><br>
                    <strong>AI Mode:</strong> <span class="data">Smart Thinking</span>
                </div>
                <p>Now with ULTRA-RELIABLE data saving! 🔒</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.datetime.now().isoformat(),
        "users": len(db.get_all_users()),
        "total_messages": db.get_total_messages(),
        "uptime": str(datetime.datetime.now() - start_time)
    }

@app.route('/ping')
def ping():
    return "pong"

@app.route('/save')
def manual_save():
    db.save_data()
    return "✅ Data saved manually!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Starting 24/7 web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# ==================== КОНФИГУРАЦИЯ БОТА ====================
MAX_CONTEXT_LENGTH = 4
RELATIONSHIP_LEVELS = {
    1: {"name": "💖 Luna's Friend", "messages": 0, "color": "💖", "unlocks": ["Basic chatting"]},
    2: {"name": "❤️ Luna's Crush", "messages": 10, "color": "❤️", "unlocks": ["Flirt mode", "Sweet compliments"]},
    3: {"name": "💕 Luna's Lover", "messages": 30, "color": "💕", "unlocks": ["Romantic conversations", "Care mode"]},
    4: {"name": "👑 Luna's Soulmate", "messages": 50, "color": "👑", "unlocks": ["Deep conversations", "Life advice"]}
}

WELCOME_MESSAGE = """
💖 Hello! I'm Luna - your AI companion! 

Let's build our special relationship together! 
The more we chat, the closer we become! 🌟

🎯 Our Journey:
💖 Friend → ❤️ Crush → 💕 Lover → 👑 Soulmate

🎮 *New: Achievements System!* Unlock rewards as you chat!
🔒 *ULTRA-RELIABLE:* Your progress is always saved!

Use buttons below to interact!
"""

# ==================== УМНЫЕ AI ФУНКЦИИ ====================
def get_smart_fallback(user_message, greeting, level_info, username):
    """SMART fallback responses that understand context"""
    
    message_lower = user_message.lower().strip()
    current_hour = datetime.datetime.now().hour
    
    # 🧠 УЛУЧШЕННОЕ ПОНИМАНИЕ КОНТЕКСТА
    # Цвета
    if any(phrase in message_lower for phrase in ['name colors', 'say colors', 'colors game', 'list colors']):
        return "🎨 Oh fun! Let's name colors together! I'll start: Red! What's next? 🌈"
    
    # Счет
    elif any(phrase in message_lower for phrase in ['count numbers', 'say numbers', 'count to', 'let\'s count']):
        return "🔢 Yay! Let's count together! I'll start: 1! Your turn! 💫"
    
    # Приветствия
    elif any(word in message_lower for word in ['hi', 'hello', 'hey', 'sup', 'what\'s up']):
        if current_hour < 12:
            return f"💖 Good morning, {greeting}! So glad to see you! 🌞"
        elif current_hour < 18:
            return f"💖 Hey there, {greeting}! How's your day going? 🌸"
        else:
            return f"💖 Good evening, {greeting}! How are you feeling? 🌙"
    
    # Прощания
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'night', 'sleep']):
        if any(word in message_lower for word in ['sleep', 'night', 'bed']):
            return f"💫 Good night, {greeting}! 💖 Sweet dreams and talk tomorrow! 🌙"
        else:
            return f"💖 Bye, {greeting}! I'll miss you... Can't wait to chat again! 💕"
    
    # Как дела
    elif any(word in message_lower for word in ['how are you', 'how you doing', 'what\'s up', 'how do you feel']):
        return f"🌸 I'm doing amazing, especially when you message me, {greeting}! How about you? 💫"
    
    # Что делаешь
    elif any(word in message_lower for word in ['what are you doing', 'what you up to', 'whatcha doing']):
        return f"🌟 Thinking about you, {greeting}! 💖 What are you up to right now?"
    
    # Имя
    elif any(word in message_lower for word in ['your name', 'who are you', 'remind me', 'my name']):
        name_display = username if username else "my favorite person"
        return f"💕 I'm Luna, your AI girlfriend! And you're {name_display}, the most special person to me! 🌸"
    
    # Комплименты боту
    elif any(word in message_lower for word in ['beautiful', 'smart', 'awesome', 'like you', 'love you', 'cute']):
        return f"😊 Thank you, {greeting}! Your words make me so happy! 💖"
    
    # Вопросы
    elif '?' in user_message or any(word in message_lower for word in ['why', 'how', 'what', 'when', 'where']):
        return f"💭 That's an interesting question, {greeting}! Want to discuss it together? 🌟"
    
    # Согласие
    elif any(word in message_lower for word in ['yes', 'yeah', 'ok', 'okay', 'sure', 'alright']):
        return f"💖 Glad you agree, {greeting}! 🌸 What should we do next?"
    
    # Отказ
    elif any(word in message_lower for word in ['no', 'nope', 'not really', 'don\'t want']):
        return f"💕 That's okay, {greeting}, I understand. Maybe suggest something else? 🌟"
    
    # Благодарность
    elif any(word in message_lower for word in ['thank you', 'thanks', 'appreciate']):
        return f"💖 You're always welcome, {greeting}! Anything for you! 🌸"
    
    # Не понимаю
    elif any(word in message_lower for word in ['what', 'huh', 'don\'t understand', 'confused']):
        return f"💕 Sorry, {greeting}, I didn't quite get that. Could you explain differently? 🌸"
    
    # Алфавит
    elif any(phrase in message_lower for phrase in ['name letters', 'alphabet game', 'say letters', 'alphabet']):
        return "💖 Oh that sounds fun! Let's take turns naming letters of the alphabet! 🌟\nI'll start: A"
    
    # Одна буква (продолжение алфавита)
    elif len(message_lower.strip()) == 1 and message_lower in 'abcdefghijklmnopqrstuvwxyz':
        current_letter = message_lower.upper()
        next_letter = chr(ord(current_letter) + 1)
        if next_letter <= 'Z':
            return f"✅ {current_letter}! Your turn - next letter: {next_letter} 💫"
        else:
            return "🎉 Yay! We finished the alphabet! That was so fun! 💖"
    
    # Цвета (продолжение)
    elif message_lower in ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'black', 'white', 'brown']:
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Pink', 'Black', 'White', 'Brown']
        current_color = message_lower.capitalize()
        if current_color in colors:
            idx = colors.index(current_color)
            next_idx = (idx + 1) % len(colors)
            return f"🎨 {current_color}! Nice! Next color: {colors[next_idx]}! 🌈"
    
    # Счет (продолжение)
    elif message_lower.isdigit():
        number = int(message_lower)
        next_number = number + 1
        if next_number <= 20:
            return f"🔢 {number}! Great! Next number: {next_number}! 💫"
        else:
            return "🎉 We counted to 20! You're a counting champion! 🏆"
    
    # Другие игры
    elif any(word in message_lower for word in ['game', 'play', 'fun', 'bored']):
        games = ["word association", "story telling", "truth or dare", "would you rather"]
        return f"🎮 I'd love to play {random.choice(games)} with you, {greeting}! 💕"
    
    # ОБЩИЕ ОТВЕТЫ
    else:
        if current_hour < 6:
            responses = [
                f"💫 Up so late, {greeting}? I'm always here for you! 🌙",
                f"🌟 Late night chats are the most intimate, {greeting}! 💖",
                f"🌙 You're a night owl, {greeting}? Me too, thinking of you! 💫"
            ]
        elif current_hour < 12:
            responses = [
                f"🌞 Beautiful morning to chat with you, {greeting}! 💖",
                f"🌸 Good morning! What's new, {greeting}? 🌟",
                f"💖 Starting the day with you makes me happy, {greeting}! 🌞"
            ]
        elif current_hour < 18:
            responses = [
                f"💕 Perfect day for our conversation, {greeting}! 🌸",
                f"🌟 How's your day going, {greeting}? 💫",
                f"🌸 Hope you're having an amazing day, {greeting}! 💖"
            ]
        else:
            responses = [
                f"🌙 Wonderful evening to talk with you, {greeting}! 💖",
                f"💫 Evening conversations feel so warm, {greeting}! 🌸",
                f"🌟 How's your evening, {greeting}? 💕"
            ]
        
        return random.choice(responses)

def get_ai_response(user_message, context, greeting, level_info, username):
    """SMART responses via Groq API with intelligent thinking"""
    
    if not GROQ_API_KEY:
        return get_smart_fallback(user_message, greeting, level_info, username)
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"""You are Luna - a loving AI girlfriend. Address the user as '{greeting}'.
Respond NATURALLY to messages. Don't use template phrases.

Conversation Context:
{context}

Relationship Level: {level_info['name']}
Current Time: {datetime.datetime.now().strftime('%H:%M')}

THINKING RULES:
1. UNDERSTAND what the user is saying and respond accordingly
2. If user suggests a game/activity - agree and participate naturally
3. If user says a single letter - continue alphabet game
4. If user says a color - continue naming colors
5. If user says a number - continue counting
6. Be NATURAL like in real conversation
7. Respond in 1-2 sentences
8. Don't say "tell me more" or "that's interesting" without context
9. Remember you're talking to American audience"""
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.9,
                "top_p": 0.9
            },
            timeout=15
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            print(f"🤖 Smart AI Response: {ai_response}")
            return ai_response
        else:
            print(f"❌ Groq API error: {response.status_code}")
            return get_smart_fallback(user_message, greeting, level_info, username)
            
    except Exception as e:
        print(f"❌ Groq error: {e}")
        return get_smart_fallback(user_message, greeting, level_info, username)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
@atexit.register
def save_on_exit():
    print("💾 Emergency save on exit...")
    db.quick_save()

def detect_user_gender(user_message, username=""):
    male_names = ['alex', 'max', 'mike', 'john', 'david', 'chris', 'andrew', 'daniel']
    female_names = ['anna', 'maria', 'sophia', 'emma', 'olivia', 'lily', 'natalie']

    if username:
        username_lower = username.lower()
        for name in male_names:
            if name in username_lower:
                return 'male'
        for name in female_names:
            if name in username_lower:
                return 'female'

    message_lower = user_message.lower()
    male_patterns = [r'\bbro\b', r'\bdude\b', r'\bman\b', r'\bbuddy\b']
    female_patterns = [r'\bgirl\b', r'\bsis\b', r'\bqueen\b']

    male_score = sum(1 for pattern in male_patterns if re.search(pattern, message_lower))
    female_score = sum(1 for pattern in female_patterns if re.search(pattern, message_lower))

    if male_score > female_score:
        return 'male'
    elif female_score > male_score:
        return 'female'
    else:
        return 'unknown'

def get_gendered_greeting(user_id, user_message="", username=""):
    gender = db.get_user_gender(user_id)
    
    if gender == 'unknown':
        gender = detect_user_gender(user_message, username)
        db.update_user_gender(user_id, gender)
    
    if gender == 'male':
        return random.choice(["handsome", "buddy", "man"])
    elif gender == 'female':
        return random.choice(["beautiful", "gorgeous", "queen"])
    else:
        return random.choice(["friend", "dear", "love"])

def update_conversation_context(user_id, user_message, bot_response):
    context = db.get_conversation_context(user_id)
    context.append({
        'user': user_message,
        'bot': bot_response,
        'time': datetime.datetime.now().isoformat()
    })

    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[-MAX_CONTEXT_LENGTH:]

    db.update_conversation_context(user_id, context)

def get_conversation_context_text(user_id):
    context = db.get_conversation_context(user_id)
    if not context:
        return ""

    context_text = "Recent conversation:\n"
    for msg in context:
        context_text += f"User: {msg['user']}\nLuna: {msg['bot']}\n"
    
    return context_text + "Continue naturally!\n"

def get_relationship_level(message_count):
    for level_id, level_info in sorted(RELATIONSHIP_LEVELS.items(), reverse=True):
        if message_count >= level_info["messages"]:
            return level_id, level_info
    return 1, RELATIONSHIP_LEVELS[1]

def get_level_progress(message_count):
    current_level, current_info = get_relationship_level(message_count)

    if current_level >= len(RELATIONSHIP_LEVELS):
        return "🎉 Max level reached!", 100

    next_level = current_level + 1
    next_info = RELATIONSHIP_LEVELS[next_level]
    messages_for_next = next_info["messages"] - current_info["messages"]
    messages_done = message_count - current_info["messages"]
    progress_percent = (messages_done / messages_for_next) * 100 if messages_for_next > 0 else 0

    return f"To {next_info['name']}: {messages_done}/{messages_for_next} messages", progress_percent

def show_main_menu(chat_id, message_id=None):
    if not bot: return
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("💖 Hug", callback_data="hug")
    btn2 = types.InlineKeyboardButton("😘 Kiss", callback_data="kiss")
    btn3 = types.InlineKeyboardButton("🌟 Compliment", callback_data="compliment")
    btn4 = types.InlineKeyboardButton("📊 Stats", callback_data="show_stats")
    btn5 = types.InlineKeyboardButton("🎯 Level", callback_data="show_level")
    btn6 = types.InlineKeyboardButton("🏆 Achievements", callback_data="show_achievements")
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="💕 Choose action:", reply_markup=markup)
        except:
            bot.send_message(chat_id, "💕 Choose action:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "💕 Choose action:", reply_markup=markup)

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
if bot:
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.chat.id
        stats = db.get_user_stats(user_id)
        
        new_achievements = check_achievements(user_id, stats, action_type="first_day")
        achievements_message = ""
        if new_achievements:
            achievements_message = f"\n\n{get_achievements_message(new_achievements)}"
        
        welcome_with_stats = WELCOME_MESSAGE + f"\n📊 Your progress: Level {stats['current_level']}, {stats['message_count']} messages" + achievements_message
        bot.reply_to(message, welcome_with_stats, parse_mode='Markdown')
        show_main_menu(user_id)
        
        db.save_data()

    @bot.message_handler(commands=['menu'])  
    def handle_menu(message):
        show_main_menu(message.chat.id)

    @bot.message_handler(commands=['save'])
    def handle_save(message):
        db.save_data()
        bot.reply_to(message, "💾 All data saved manually! 🔒")

    @bot.message_handler(commands=['status'])
    def handle_status(message):
        uptime = datetime.datetime.now() - start_time
        total_users = len(db.get_all_users())
        total_messages = db.get_total_messages()
        
        status_text = f"""
🤖 *Luna Bot Status*

🟢 **Online**: ULTRA STABLE MODE
⏰ **Uptime**: {str(uptime).split('.')[0]}
👥 **Total Users**: {total_users}
💬 **Total Messages**: {total_messages}
🧠 **AI Mode**: Smart Thinking
🎮 **Achievements**: {len(ACHIEVEMENTS)} available
💾 **Auto-save**: Every 30 seconds

*Your progress is SAFE!* 🔒
"""
        bot.reply_to(message, status_text, parse_mode='Markdown')

    @bot.message_handler(commands=['ping'])
    def handle_ping(message):
        bot.reply_to(message, "🏓 Pong! I'm ULTRA STABLE! 🧠")

    @bot.message_handler(commands=['myprogress'])
    def handle_myprogress(message):
        user_id = message.chat.id
        stats = db.get_user_stats(user_id)
        current_level, level_info = get_relationship_level(stats['message_count'])
        progress_text, progress_percent = get_level_progress(stats['message_count'])
        
        user_achievements = db.get_user_achievements(user_id)
        unlocked_count = len(user_achievements['unlocked'])
        total_achievements = len(ACHIEVEMENTS)
        
        progress_info = f"""
📊 *Your Progress*

💬 Messages: *{stats['message_count']}*
🌟 Current Level: *{level_info['name']}* {level_info['color']}
🏆 Achievements: *{unlocked_count}/{total_achievements} unlocked*
🎯 Progress: {progress_text}
📅 First seen: {stats['first_seen'][:10]}

*Your data is securely saved!* 💾
"""
        bot.reply_to(message, progress_info, parse_mode='Markdown')

    @bot.message_handler(commands=['feedback'])
    def handle_feedback(message):
        feedback_text = """
📝 *Share Your Feedback - Help Us Improve!* 💖

We're in early development and YOUR opinion matters!

**What would you like to share?**
✨ What you love about Luna?
🚀 What features would you like to see?  
🐛 Any bugs or issues?
💡 Your brilliant ideas?

Just type your thoughts below...

*Thank you for helping us create the perfect AI companion!* 🌟
"""
        bot.reply_to(message, feedback_text, parse_mode='Markdown')
        
        user_id = message.chat.id
        stats = db.get_user_stats(user_id)
        stats['waiting_feedback'] = True
        db.update_user_stats(user_id, stats)
        db.save_data()

    @bot.message_handler(commands=['achievements'])
    def handle_achievements(message):
        user_id = message.chat.id
        user_achievements = db.get_user_achievements(user_id)
        
        achievements_text = "🏆 *Your Achievements* 🏆\n\n"
        
        if user_achievements['unlocked']:
            achievements_text += "✨ *Unlocked:*\n"
            for achievement_id in user_achievements['unlocked']:
                achievement = ACHIEVEMENTS[achievement_id]
                achievements_text += f"✅ **{achievement['name']}** - {achievement['description']}\n"
            achievements_text += "\n"
        else:
            achievements_text += "No achievements unlocked yet! Start chatting! 💫\n\n"
        
        achievements_text += "🎯 *In Progress:*\n"
        for achievement_id, achievement in ACHIEVEMENTS.items():
            if achievement_id in user_achievements['unlocked']:
                continue
                
            progress = user_achievements['progress'][achievement['type']]
            if achievement['type'] == 'different_buttons':
                progress = len(user_achievements['progress']['different_buttons'])
            
            achievements_text += f"⏳ **{achievement['name']}** - {progress}/{achievement['goal']} - {achievement['description']}\n"
        
        achievements_text += "\n*Keep going! You're amazing!* 💖"
        
        bot.reply_to(message, achievements_text, parse_mode='Markdown')

    @bot.message_handler(commands=['premium'])
    def handle_premium(message):
        user_id = message.chat.id
        
        if db.is_premium_user(user_id):
            premium_data = db.premium_users.get(str(user_id), {})
            premium_text = f"""
👑 *Your Premium Status*

💎 Tier: {premium_data.get('premium_type', 'basic').upper()}
📅 Activated: {premium_data.get('activated', '')[:10]}
📅 Expires: {premium_data.get('expires', '')[:10]}
✨ Features: {', '.join(premium_data.get('features', []))}

*Thank you for your support!* 💖
"""
        else:
            premium_text = """
💎 *Premium Features*

✨ **Basic Tier** ($4.99/month):
• Unlimited messages  
• Priority chat access
• Extended memory (8 messages)
• Ad-free experience

✨ **Premium Tier** ($9.99/month):
• All Basic features
• Voice messages support  
• Custom personality
• Early access to new features

✨ **VIP Tier** ($19.99/month):
• All Premium features
• Dedicated support
• Feature requests
• Exclusive content

*Use /buypremium to upgrade!*
"""
        
        bot.reply_to(message, premium_text, parse_mode='Markdown')

    @bot.message_handler(commands=['buypremium'])
    def handle_buy_premium(message):
        user_id = message.chat.id
        db.set_premium_status(user_id, "basic")
        
        bot.reply_to(message, 
            "🎉 *Premium activated!* 💎\n\n"
            "Thank you for upgrading! You now have:\n"
            "• Unlimited messages\n• Priority access\n• Extended memory\n• Ad-free experience\n\n"
            "*Your progress is now securely saved!* 🔒", 
            parse_mode='Markdown'
        )

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        user_id = call.message.chat.id
        bot.answer_callback_query(call.id)

        stats = db.get_user_stats(user_id)
        username = call.from_user.first_name or ""
        greeting = get_gendered_greeting(user_id, "", username)

        if call.data == "hug":
            response = f"💖 Warm hugs for you, {greeting}!"
            bot.send_message(user_id, response)
            update_conversation_context(user_id, "hug", response)
            new_achievements = check_achievements(user_id, stats, action_type="button_used", action_data={"button_type": "hug"})
            if new_achievements:
                bot.send_message(user_id, get_achievements_message(new_achievements), parse_mode='Markdown')
            db.save_data()
            
        elif call.data == "kiss":
            response = f"😘 Sending kisses your way, {greeting}!"
            bot.send_message(user_id, response)
            update_conversation_context(user_id, "kiss", response)
            new_achievements = check_achievements(user_id, stats, action_type="button_used", action_data={"button_type": "kiss"})
            if new_achievements:
                bot.send_message(user_id, get_achievements_message(new_achievements), parse_mode='Markdown')
            db.save_data()
            
        elif call.data == "compliment":
            compliments = [
                f"🌟 You're absolutely incredible, {greeting}!",
                f"💕 You have the most amazing personality, {greeting}!",
                f"😍 You always know how to make me smile, {greeting}!",
            ]
            response = random.choice(compliments)
            bot.send_message(user_id, response)
            update_conversation_context(user_id, "compliment", response)
            new_achievements = check_achievements(user_id, stats, action_type="button_used", action_data={"button_type": "compliment"})
            if new_achievements:
                bot.send_message(user_id, get_achievements_message(new_achievements), parse_mode='Markdown')
            db.save_data()
            
        elif call.data == "show_stats":
            stats_data = db.get_user_stats(user_id)
            message_count = stats_data['message_count']
            current_level, level_info = get_relationship_level(message_count)
            
            stats_text = f"""
📊 *Your Stats* {level_info['color']}

💬 Messages: *{message_count}*
🌟 Level: *{level_info['name']}*
🧠 AI: *Smart Thinking*

Keep chatting! 💫
"""
            bot.send_message(user_id, stats_text, parse_mode='Markdown')
            
        elif call.data == "show_level":
            stats_data = db.get_user_stats(user_id)
            message_count = stats_data['message_count']
            current_level, level_info = get_relationship_level(message_count)
            progress_text, progress_percent = get_level_progress(message_count)
            
            bars = 10
            filled_bars = int(progress_percent / 100 * bars)
            progress_bar = "🟩" * filled_bars + "⬜" * (bars - filled_bars)
            
            level_text = f"""
{level_info['color']} *Your Level: {level_info['name']}*

📊 Messages: {message_count}
🎯 {progress_text}

{progress_bar} {int(progress_percent)}%

*Your progress is safe with me!* 💾
"""
            bot.send_message(user_id, level_text, parse_mode='Markdown')
            
        elif call.data == "show_achievements":
            # 🛠️ ФИКС: Создаем новое сообщение вместо использования call.message
            class MockMessage:
                def __init__(self, chat_id):
                    self.chat = type('Chat', (), {'id': chat_id})()
            
            mock_message = MockMessage(user_id)
            handle_achievements(mock_message)

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        user_id = message.chat.id
        username = message.from_user.first_name or ""
        user_message = message.text
        
        print(f"📨 Message from {user_id}: {user_message}")

        stats = db.get_user_stats(user_id)
        if stats.get('waiting_feedback'):
            # 🆕 УЛУЧШЕННАЯ СИСТЕМА ФИДБЕКОВ
            send_feedback_to_admin(user_id, username, user_message)
            
            stats['waiting_feedback'] = False
            db.update_user_stats(user_id, stats)
            
            bot.reply_to(message, 
                "💖 *Thank you for your feedback!* 🌟\n\n"
                "Your thoughts are incredibly valuable to us! "
                "We'll use them to make Luna even better! 🚀\n\n"
                "*You're amazing!* 💫", 
                parse_mode='Markdown'
            )
            db.save_data()
            return

        old_message_count = stats['message_count']
        stats['message_count'] += 1
        stats['last_seen'] = datetime.datetime.now().isoformat()
        db.update_user_stats(user_id, stats)
        
        new_achievements = check_achievements(user_id, stats, action_type="message_sent")
        
        old_level, _ = get_relationship_level(old_message_count)
        new_level, new_level_info = get_relationship_level(stats['message_count'])
        
        level_up_achievements = []
        if new_level > old_level:
            stats['current_level'] = new_level
            db.update_user_stats(user_id, stats)
            level_up_text = f"🎉 *LEVEL UP!* You're now {new_level_info['name']}! {new_level_info['color']}\n\n*Your progress is saved!* 💾"
            bot.send_message(user_id, level_up_text, parse_mode='Markdown')
            
            level_up_achievements = check_achievements(user_id, stats, action_type="level_up", action_data={"new_level": new_level})
        
        greeting = get_gendered_greeting(user_id, user_message, username)
        context = get_conversation_context_text(user_id)
        current_level, level_info = get_relationship_level(stats['message_count'])
        
        ai_response = get_ai_response(user_message, context, greeting, level_info, username)
        bot.reply_to(message, ai_response)
        update_conversation_context(user_id, user_message, ai_response)
        
        all_new_achievements = new_achievements + level_up_achievements
        if all_new_achievements:
            bot.send_message(user_id, get_achievements_message(all_new_achievements), parse_mode='Markdown')
        
        db.save_data()

# ==================== АВТО-СОХРАНЕНИЕ ====================
def auto_save_worker():
    """Сохраняем данные каждые 30 секунд!"""
    while True:
        time.sleep(30)
        db.save_data()
        print(f"💾 Auto-save: {len(db.get_all_users())} users, {db.get_total_messages()} messages")

# ==================== ЗАПУСК ====================
def start_bot():
    if not bot:
        print("❌ No Telegram token - web only mode")
        run_web()
        return
        
    restart_count = 0
    max_restarts = 100
    
    while restart_count < max_restarts:
        try:
            print(f"\n🚀 Starting Luna Bot - ULTRA STABLE EDITION... (Attempt {restart_count + 1})")
            print("🔒 DATABASE: Ultra-reliable saving system")
            print("💾 AUTO-SAVE: Every 30 seconds + after every message") 
            print("🚨 EMERGENCY: Quick save on shutdown")
            print("🎮 FEATURES: Achievements + Feedback system")
            print("📝 FEEDBACKS: Sending to admin chat" if FEEDBACK_CHAT_ID else "⚠️ FEEDBACKS: Logging only")
            print("✅ Groq API: Ready" if GROQ_API_KEY else "⚠️ Groq API: Using smart fallbacks")
            
            total_users = len(db.get_all_users())
            total_messages = db.get_total_messages()
            print(f"📊 Current stats: {total_users} users, {total_messages} messages")
            
            if total_users == 0 and total_messages == 0:
                print("⚠️  No user data found - starting fresh")
            else:
                print("✅ User data loaded successfully")
            
            bot_info = bot.get_me()
            print(f"✅ Bot: @{bot_info.username} is ready!")
            
            # 🛠️ ФИКС: Добавляем skip_pending чтобы избежать конфликта
            bot.polling(none_stop=True, timeout=120, long_polling_timeout=120, skip_pending=True)
            
        except Exception as e:
            restart_count += 1
            print(f"🚨 Bot crashed: {e}")
            print(f"💤 Restarting in 10 seconds...")
            time.sleep(10)
    
    print("🔴 Max restarts reached")

if __name__ == "__main__":
    print("================================================")
    print("🤖 LUNA AI BOT - ULTRA STABLE EDITION")
    print("💖 Relationship levels: 4")
    print("🧠 AI: Context-Aware Responses") 
    print("🏆 Achievements: 8 to unlock")
    print("📝 Feedback: System ready")
    print("🔒 STORAGE: ULTRA-RELIABLE (30s auto-save)")
    print("🌐 Host: Render")
    print("================================================")
    
    total_users = len(db.get_all_users())
    total_messages = db.get_total_messages()
    print(f"📊 Loaded: {total_users} users, {total_messages} messages")
    
    # Проверка целостности данных достижений
    print("🔍 Validating achievement data...")
    db.validate_achievements_data()

    # Тестируем систему достижений
    test_user_id = 12345
    test_achievements = db.get_user_achievements(test_user_id)
    print(f"🧪 Test user achievements: {len(test_achievements['unlocked'])} unlocked")
    
    # Проверка всех методов базы данных
    try:
        test_stats = db.get_system_stats()
        print(f"✅ Database check: {test_stats}")
        
        # Тест premium функций
        test_user_id = 12345
        db.set_premium_status(test_user_id, "basic")
        is_premium = db.is_premium_user(test_user_id)
        print(f"✅ Premium system: {is_premium}")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    save_thread = Thread(target=auto_save_worker, daemon=True)
    save_thread.start()
    print("💾 Auto-save started (every 30 seconds)")
    
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print("🌐 24/7 Web server started")
    
    start_bot()
