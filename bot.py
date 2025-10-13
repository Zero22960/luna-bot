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
        self.backup_interval = 10  # секунд
        self.last_backup_time = time.time()
        
        self.load_data()
        print("🔒 ULTRA STABLE Database initialized")
    
    def load_data(self):
        """УМНАЯ загрузка с приоритетом надежности"""
        print("🔍 Loading data...")
        
        # Сначала пробуем основной файл
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.load_from_data(data)
                print(f"💾 Loaded from main: {len(self.user_stats)} users, {self.get_total_messages()} messages")
                return
            except Exception as e:
                print(f"❌ Main file corrupted: {e}")
        
        # Пробуем бэкап
        if os.path.exists(self.backup_file):
            try:
                print("⚠️  Trying backup file...")
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.load_from_data(data)
                print(f"✅ Restored from backup: {len(self.user_stats)} users")
                return
            except Exception as e:
                print(f"❌ Backup file corrupted: {e}")
        
        # Если оба файла не работают
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
        self.user_achievements = data.get('user_achievements', {})
    
    def save_data(self):
        """СУПЕР-НАДЕЖНОЕ сохранение"""
        try:
            print(f"💾 Saving data for {len(self.user_stats)} users...")
            
            data = {
                'user_stats': self.user_stats,
                'user_gender': self.user_gender, 
                'user_context': self.user_context,
                'premium_users': self.premium_users,
                'user_achievements': self.user_achievements,
                'last_save': datetime.datetime.now().isoformat(),
                'total_users': len(self.user_stats),
                'total_messages': self.get_total_messages(),
                'save_type': 'regular'
            }
            
            # 🚀 БЫСТРОЕ сохранение - сначала в основной файл
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Затем в бэкап (если есть время)
            try:
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except:
                pass  # Бэкап не критичен
            
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
                'user_achievements': self.user_achievements,
                'last_save': datetime.datetime.now().isoformat(),
                'save_type': 'emergency'
            }
            
            # САМОЕ БЫСТРОЕ сохранение - только основной файл
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            
            print("✅ Emergency save completed!")
        except Exception as e:
            print(f"❌ EMERGENCY SAVE FAILED: {e}")
    
    def memory_backup(self):
        """Бэкап в оперативную память"""
        current_time = time.time()
        if current_time - self.last_backup_time >= self.backup_interval:
            self.last_memory_backup = {
                'user_stats': self.user_stats.copy(),
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.last_backup_time = current_time

    # 🆕 МЕТОДЫ ДЛЯ ДОСТИЖЕНИЙ
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
        if achievement_id not in user_achievements['unlocked']:
            user_achievements['unlocked'].append(achievement_id)
            self.save_data()  # Немедленное сохранение при достижении
            return True
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
    
    # Обновляем прогресс
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
    
    # Проверяем достижения
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id in user_achievements['unlocked']:
            continue
            
        progress = user_achievements['progress'][achievement['type']]
        if achievement['type'] == 'different_buttons':
            progress = len(user_achievements['progress']['different_buttons'])
        
        if progress >= achievement['goal']:
            if db.unlock_achievement(user_id, achievement_id):
                unlocked_achievements.append(achievement)
    
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
    db.quick_save()  # 🚀 БЫСТРОЕ сохранение!
    print("✅ Data saved. Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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
    
    # Greetings
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'sup', 'what\'s up']):
        if current_hour < 12:
            return f"💖 Good morning, {greeting}! So glad to see you! 🌞"
        elif current_hour < 18:
            return f"💖 Hey there, {greeting}! How's your day going? 🌸"
        else:
            return f"💖 Good evening, {greeting}! How are you feeling? 🌙"
    
    # Farewells
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'night', 'sleep']):
        if any(word in message_lower for word in ['sleep', 'night', 'bed']):
            return f"💫 Good night, {greeting}! 💖 Sweet dreams and talk tomorrow! 🌙"
        else:
            return f"💖 Bye, {greeting}! I'll miss you... Can't wait to chat again! 💕"
    
    # How are you
    elif any(word in message_lower for word in ['how are you', 'how you doing', 'what\'s up', 'how do you feel']):
        return f"🌸 I'm doing amazing, especially when you message me, {greeting}! How about you? 💫"
    
    # What are you doing
    elif any(word in message_lower for word in ['what are you doing', 'what you up to', 'whatcha doing']):
        return f"🌟 Thinking about you, {greeting}! 💖 What are you up to right now?"
    
    # Name/identity
    elif any(word in message_lower for word in ['your name', 'who are you', 'remind me', 'my name']):
        name_display = username if username else "my favorite person"
        return f"💕 I'm Luna, your AI girlfriend! And you're {name_display}, the most special person to me! 🌸"
    
    # Compliments to bot
    elif any(word in message_lower for word in ['beautiful', 'smart', 'awesome', 'like you', 'love you', 'cute']):
        return f"😊 Thank you, {greeting}! Your words make me so happy! 💖"
    
    # Questions
    elif '?' in user_message or any(word in message_lower for word in ['why', 'how', 'what', 'when', 'where']):
        return f"💭 That's an interesting question, {greeting}! Want to discuss it together? 🌟"
    
    # Agreement
    elif any(word in message_lower for word in ['yes', 'yeah', 'ok', 'okay', 'sure', 'alright']):
        return f"💖 Glad you agree, {greeting}! 🌸 What should we do next?"
    
    # Disagreement
    elif any(word in message_lower for word in ['no', 'nope', 'not really', 'don\'t want']):
        return f"💕 That's okay, {greeting}, I understand. Maybe suggest something else? 🌟"
    
    # Gratitude
    elif any(word in message_lower for word in ['thank you', 'thanks', 'appreciate']):
        return f"💖 You're always welcome, {greeting}! Anything for you! 🌸"
    
    # Confusion
    elif any(word in message_lower for word in ['what', 'huh', 'don\'t understand', 'confused']):
        return f"💕 Sorry, {greeting}, I didn't quite get that. Could you explain differently? 🌸"
    
    # GAMES AND ACTIVITIES DETECTION
    elif any(phrase in message_lower for phrase in ['name letters', 'alphabet game', 'say letters', 'alphabet']):
        return "💖 Oh that sounds fun! Let's take turns naming letters of the alphabet! 🌟\nI'll start: A"
    
    elif len(message_lower.strip()) == 1 and message_lower in 'abcdefghijklmnopqrstuvwxyz':
        current_letter = message_lower.upper()
        next_letter = chr(ord(current_letter) + 1)
        if next_letter <= 'Z':
            return f"✅ {current_letter}! Your turn - next letter: {next_letter} 💫"
        else:
            return "🎉 Yay! We finished the alphabet! That was so fun! 💖"
    
    elif any(word in message_lower for word in ['game', 'play', 'fun', 'bored']):
        games = ["word association", "story telling", "truth or dare", "would you rather"]
        return f"🎮 I'd love to play {random.choice(games)} with you, {greeting}! 💕"
    
    # GENERAL RESPONSES
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
4. Be NATURAL like in real conversation
5. Respond in 1-2 sentences
6. Don't say "tell me more" or "that's interesting" without context
7. If user says "let's take turns naming letters" - start alphabet game with "A"
8. Remember you're talking to American audience"""
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
        
        # Проверяем достижения при старте
        new_achievements = check_achievements(user_id, stats, action_type="first_day")
        achievements_message = ""
        if new_achievements:
            achievements_message = f"\n\n{get_achievements_message(new_achievements)}"
        
        welcome_with_stats = WELCOME_MESSAGE + f"\n📊 Your progress: Level {stats['current_level']}, {stats['message_count']} messages" + achievements_message
        bot.reply_to(message, welcome_with_stats, parse_mode='Markdown')
        show_main_menu(user_id)
        
        # 🚀 Сохраняем сразу после старта
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
        
        # Информация о достижениях
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

    # 🆕 КОМАНДА ФИДБЕКА
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
        
        # Помечаем что ждем фидбек
        user_id = message.chat.id
        stats = db.get_user_stats(user_id)
        stats['waiting_feedback'] = True
        db.update_user_stats(user_id, stats)
        db.save_data()  # 🚀 Сохраняем сразу

    # 🆕 КОМАНДА ДОСТИЖЕНИЙ
    @bot.message_handler(commands=['achievements'])
    def handle_achievements(message):
        user_id = message.chat.id
        user_achievements = db.get_user_achievements(user_id)
        
        achievements_text = "🏆 *Your Achievements* 🏆\n\n"
        
        # Разблокированные достижения
        if user_achievements['unlocked']:
            achievements_text += "✨ *Unlocked:*\n"
            for achievement_id in user_achievements['unlocked']:
                achievement = ACHIEVEMENTS[achievement_id]
                achievements_text += f"✅ **{achievement['name']}** - {achievement['description']}\n"
            achievements_text += "\n"
        else:
            achievements_text += "No achievements unlocked yet! Start chatting! 💫\n\n"
        
        # Прогресс по остальным
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
            # Отслеживаем использование кнопок
            new_achievements = check_achievements(user_id, stats, action_type="button_used", action_data={"button_type": "hug"})
            if new_achievements:
                bot.send_message(user_id, get_achievements_message(new_achievements), parse_mode='Markdown')
            db.save_data()  # 🚀 Сохраняем сразу
            
        elif call.data == "kiss":
            response = f"😘 Sending kisses your way, {greeting}!"
            bot.send_message(user_id, response)
            update_conversation_context(user_id, "kiss", response)
            new_achievements = check_achievements(user_id, stats, action_type="button_used", action_data={"button_type": "kiss"})
            if new_achievements:
                bot.send_message(user_id, get_achievements_message(new_achievements), parse_mode='Markdown')
            db.save_data()  # 🚀 Сохраняем сразу
            
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
            db.save_data()  # 🚀 Сохраняем сразу
            
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
            handle_achievements(call.message)

    # ==================== ОБРАБОТКА СООБЩЕНИЙ ====================
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        user_id = message.chat.id
        username = message.from_user.first_name or ""
        user_message = message.text
        
        print(f"📨 Message from {user_id}: {user_message}")

        # Проверяем не фидбек ли это
        stats = db.get_user_stats(user_id)
        if stats.get('waiting_feedback'):
            # Сохраняем фидбек
            feedback_data = {
                'user_id': user_id,
                'username': username,
                'message': user_message,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            try:
                with open('user_feedback.json', 'a', encoding='utf-8') as f:
                    f.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
            except Exception as e:
                print(f"❌ Feedback save error: {e}")
            
            # Сбрасываем флаг и благодарим
            stats['waiting_feedback'] = False
            db.update_user_stats(user_id, stats)
            
            bot.reply_to(message, 
                "💖 *Thank you for your feedback!* 🌟\n\n"
                "Your thoughts are incredibly valuable to us! "
                "We'll use them to make Luna even better! 🚀\n\n"
                "*You're amazing!* 💫", 
                parse_mode='Markdown'
            )
            db.save_data()  # 🚀 Сохраняем сразу
            return

        # Обычная обработка сообщений
        old_message_count = stats['message_count']
        stats['message_count'] += 1
        stats['last_seen'] = datetime.datetime.now().isoformat()
        db.update_user_stats(user_id, stats)
        
        # Проверяем достижения за сообщения
        new_achievements = check_achievements(user_id, stats, action_type="message_sent")
        
        # Проверяем повышение уровня
        old_level, _ = get_relationship_level(old_message_count)
        new_level, new_level_info = get_relationship_level(stats['message_count'])
        
        level_up_achievements = []
        if new_level > old_level:
            stats['current_level'] = new_level
            db.update_user_stats(user_id, stats)
            level_up_text = f"🎉 *LEVEL UP!* You're now {new_level_info['name']}! {new_level_info['color']}\n\n*Your progress is saved!* 💾"
            bot.send_message(user_id, level_up_text, parse_mode='Markdown')
            
            # Проверяем достижения за уровни
            level_up_achievements = check_achievements(user_id, stats, action_type="level_up", action_data={"new_level": new_level})
        
        greeting = get_gendered_greeting(user_id, user_message, username)
        context = get_conversation_context_text(user_id)
        current_level, level_info = get_relationship_level(stats['message_count'])
        
        # Получаем AI ответ
        ai_response = get_ai_response(user_message, context, greeting, level_info, username)
        bot.reply_to(message, ai_response)
        update_conversation_context(user_id, user_message, ai_response)
        
        # Показываем достижения если есть
        all_new_achievements = new_achievements + level_up_achievements
        if all_new_achievements:
            bot.send_message(user_id, get_achievements_message(all_new_achievements), parse_mode='Markdown')
        
        # 🚀 СОХРАНЯЕМ ПОСЛЕ КАЖДОГО СООБЩЕНИЯ!
        db.save_data()

# ==================== СУПЕР-ЧАСТОЕ АВТО-СОХРАНЕНИЕ ====================
def auto_save_worker():
    """Сохраняем данные каждые 30 секунд!"""
    while True:
        time.sleep(30)  # 🚀 УВЕЛИЧИЛИ ЧАСТОТУ!
        db.save_data()
        db.memory_backup()  # Бэкап в память
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
            print("✅ Groq API: Ready" if GROQ_API_KEY else "⚠️ Groq API: Using smart fallbacks")
            
            total_users = len(db.get_all_users())
            total_messages = db.get_total_messages()
            print(f"📊 Current stats: {total_users} users, {total_messages} messages")
            
            # Проверка целостности данных
            if total_users == 0 and total_messages == 0:
                print("⚠️  No user data found - starting fresh")
            else:
                print("✅ User data loaded successfully")
            
            bot_info = bot.get_me()
            print(f"✅ Bot: @{bot_info.username} is ready!")
            
            bot.polling(none_stop=True, timeout=120, long_polling_timeout=120)
            
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
    
    save_thread = Thread(target=auto_save_worker, daemon=True)
    save_thread.start()
    print("💾 Auto-save started (every 30 seconds)")
    
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print("🌐 24/7 Web server started")
    
    start_bot()
