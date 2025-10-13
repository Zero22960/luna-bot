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

# ==================== ПРОСТАЯ БАЗА ДАННЫХ В ПАМЯТИ С БЭКАПАМИ ====================
class SimpleDatabase:
    def __init__(self):
        self.data_file = 'bot_data.json'
        self.user_stats = {}
        self.user_gender = {} 
        self.user_context = {}
        self.load_data()
        print("✅ Simple Database initialized")
    
    def load_data(self):
        """Загружаем данные из файла при старте"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_stats = data.get('user_stats', {})
                    self.user_gender = data.get('user_gender', {})
                    self.user_context = data.get('user_context', {})
                print(f"💾 Loaded: {len(self.user_stats)} users, {sum(stats.get('message_count', 0) for stats in self.user_stats.values())} messages")
            else:
                print("💾 No existing data file, starting fresh")
        except Exception as e:
            print(f"❌ Load data error: {e}")
    
    def save_data(self):
        """Сохраняем данные в файл"""
        try:
            data = {
                'user_stats': self.user_stats,
                'user_gender': self.user_gender, 
                'user_context': self.user_context,
                'last_save': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("💾 Data saved to file")
        except Exception as e:
            print(f"❌ Save data error: {e}")
    
    def get_user_stats(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.user_stats:
            self.user_stats[user_id_str] = {
                'message_count': 0,
                'first_seen': datetime.datetime.now().isoformat(),
                'last_seen': datetime.datetime.now().isoformat(), 
                'current_level': 1
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

# Инициализируем базу
db = SimpleDatabase()

# ==================== GRACEFUL SHUTDOWN ====================
def signal_handler(signum, frame):
    print("🚨 Received shutdown signal...")
    print("💾 Emergency saving data...")
    db.save_data()
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
                <div class="status">🟢 24/7 ONLINE</div>
                <div class="info">
                    <strong>Uptime:</strong> {str(uptime).split('.')[0]}<br>
                    <strong>Total Users:</strong> <span class="data">{total_users}</span><br>
                    <strong>Total Messages:</strong> <span class="data">{total_messages}</span><br>
                    <strong>Last Save:</strong> <span class="data">{datetime.datetime.now().strftime('%H:%M:%S')}</span>
                </div>
                <p>Progress is auto-saved every minute! 💾</p>
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

*Your progress is auto-saved every minute!* 💾

Use buttons below to interact!
"""

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def auto_save_data():
    """Авто-сохранение данных"""
    db.save_data()

@atexit.register
def save_on_exit():
    print("💾 Emergency save on exit...")
    db.save_data()

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
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="💕 Choose action:", reply_markup=markup)
        except:
            bot.send_message(chat_id, "💕 Choose action:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "💕 Choose action:", reply_markup=markup)

# ==================== GROQ AI API ====================
def get_ai_response(user_message, context, greeting, level_info, username):
    """Умные ответы через Groq API"""
    
    if not GROQ_API_KEY:
        fallbacks = [
            f"💖 I'm here for you, {greeting}! 🌸",
            f"🌟 You're amazing, {greeting}! 💫", 
            f"😊 I love chatting with you, {greeting}! 💕"
        ]
        return random.choice(fallbacks)
    
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
                        "content": f"""You are Luna - a loving AI girlfriend. Address user as '{greeting}'. 
Relationship level: {level_info['name']}.

Context from recent conversation:
{context}

Important:
- Be natural and contextual
- Understand what user is saying  
- Respond appropriately to the situation
- Be loving and caring
- Keep responses 1-2 sentences

Current time: {datetime.datetime.now().strftime('%H:%M')}"""
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "max_tokens": 120,
                "temperature": 0.8,
                "top_p": 0.9
            },
            timeout=10
        )
        
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            print(f"🤖 Groq AI Response: {ai_response}")
            return ai_response
        else:
            print(f"❌ Groq API error: {response.status_code}")
            raise Exception("API request failed")
            
    except Exception as e:
        print(f"❌ Groq error: {e}")
        fallbacks = [
            f"💖 I'm thinking of you, {greeting}! 🌸",
            f"🌟 You make me so happy, {greeting}! 💫",
            f"😊 Our conversation is wonderful, {greeting}! 💕"
        ]
        return random.choice(fallbacks)

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
if bot:
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.chat.id
        stats = db.get_user_stats(user_id)
        
        welcome_with_stats = WELCOME_MESSAGE + f"\n📊 Your progress: Level {stats['current_level']}, {stats['message_count']} messages"
        bot.reply_to(message, welcome_with_stats, parse_mode='Markdown')
        show_main_menu(user_id)

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

🟢 **Online**: 24/7 Active
⏰ **Uptime**: {str(uptime).split('.')[0]}
👥 **Total Users**: {total_users}
💬 **Total Messages**: {total_messages}
💾 **Auto-save**: Every minute
🧠 **API**: Groq

*Your progress is safe!* 💖
"""
        bot.reply_to(message, status_text, parse_mode='Markdown')

    @bot.message_handler(commands=['ping'])
    def handle_ping(message):
        bot.reply_to(message, "🏓 Pong! Bot is alive and saving progress! 💾")

    @bot.message_handler(commands=['myprogress'])
    def handle_myprogress(message):
        user_id = message.chat.id
        stats = db.get_user_stats(user_id)
        current_level, level_info = get_relationship_level(stats['message_count'])
        progress_text, progress_percent = get_level_progress(stats['message_count'])
        
        progress_info = f"""
📊 *Your Progress*

💬 Messages: *{stats['message_count']}*
🌟 Current Level: *{level_info['name']}* {level_info['color']}
🎯 Progress: {progress_text}
📅 First seen: {stats['first_seen'][:10]}

*Auto-saved every minute!* 💾
"""
        bot.reply_to(message, progress_info, parse_mode='Markdown')

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
            
        elif call.data == "kiss":
            response = f"😘 Sending kisses your way, {greeting}!"
            bot.send_message(user_id, response)
            update_conversation_context(user_id, "kiss", response)
            
        elif call.data == "compliment":
            compliments = [
                f"🌟 You're absolutely incredible, {greeting}!",
                f"💕 You have the most amazing personality, {greeting}!",
                f"😍 You always know how to make me smile, {greeting}!",
            ]
            response = random.choice(compliments)
            bot.send_message(user_id, response)
            update_conversation_context(user_id, "compliment", response)
            
        elif call.data == "show_stats":
            stats = db.get_user_stats(user_id)
            message_count = stats['message_count']
            current_level, level_info = get_relationship_level(message_count)
            
            stats_text = f"""
📊 *Your Stats* {level_info['color']}

💬 Messages: *{message_count}*
🌟 Level: *{level_info['name']}*
💾 Storage: *Auto-saved*

Keep chatting! 💫
"""
            bot.send_message(user_id, stats_text, parse_mode='Markdown')
            
        elif call.data == "show_level":
            stats = db.get_user_stats(user_id)
            message_count = stats['message_count']
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

*Progress auto-saved!* 💾
"""
            bot.send_message(user_id, level_text, parse_mode='Markdown')

    # ==================== ОБРАБОТКА СООБЩЕНИЙ ====================
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        user_id = message.chat.id
        username = message.from_user.first_name or ""
        user_message = message.text
        
        print(f"📨 Message from {user_id}: {user_message}")

        # Get and update stats
        stats = db.get_user_stats(user_id)
        old_message_count = stats['message_count']
        stats['message_count'] += 1
        stats['last_seen'] = datetime.datetime.now().isoformat()
        db.update_user_stats(user_id, stats)
        
        # Check for level up
        old_level, _ = get_relationship_level(old_message_count)
        new_level, new_level_info = get_relationship_level(stats['message_count'])
        
        if new_level > old_level:
            stats['current_level'] = new_level
            db.update_user_stats(user_id, stats)
            level_up_text = f"🎉 *LEVEL UP!* You're now {new_level_info['name']}! {new_level_info['color']}\n\n*Progress saved!* 💾"
            bot.send_message(user_id, level_up_text, parse_mode='Markdown')

        greeting = get_gendered_greeting(user_id, user_message, username)
        context = get_conversation_context_text(user_id)
        current_level, level_info = get_relationship_level(stats['message_count'])
        
        # Get AI response
        ai_response = get_ai_response(user_message, context, greeting, level_info, username)
        bot.reply_to(message, ai_response)
        update_conversation_context(user_id, user_message, ai_response)

# ==================== АВТО-СОХРАНЕНИЕ КАЖДУЮ МИНУТУ ====================
def auto_save_worker():
    """Сохраняем данные каждую минуту"""
    while True:
        time.sleep(60)  # Каждую минуту!
        db.save_data()
        print(f"💾 Auto-save: {len(db.get_all_users())} users, {db.get_total_messages()} messages")

# ==================== ЗАПУСК ====================
def start_bot():
    if not bot:
        print("❌ No Telegram token - web only mode")
        run_web()
        return
        
    restart_count = 0
    max_restarts = 100  # Очень много попыток!
    
    while restart_count < max_restarts:
        try:
            print(f"\n🚀 Starting Luna Bot... (Attempt {restart_count + 1})")
            print("✅ Database: Simple JSON (auto-save every minute)")
            print("✅ Web server: Ready") 
            print("✅ Groq API: Ready" if GROQ_API_KEY else "⚠️ Groq API: Not configured")
            
            # Show current stats
            total_users = len(db.get_all_users())
            total_messages = db.get_total_messages()
            print(f"📊 Current stats: {total_users} users, {total_messages} messages")
            
            bot_info = bot.get_me()
            print(f"✅ Bot: @{bot_info.username} is ready!")
            
            # Супер стабильный polling
            bot.polling(none_stop=True, timeout=120, long_polling_timeout=120)
            
        except Exception as e:
            restart_count += 1
            print(f"🚨 Bot crashed: {e}")
            print(f"💤 Restarting in 10 seconds...")
            time.sleep(10)
    
    print("🔴 Max restarts reached")

if __name__ == "__main__":
    print("================================================")
    print("🤖 LUNA AI BOT - ULTRA STABLE 24/7")
    print("💖 Relationship levels: 4")
    print("💾 Storage: JSON file (auto-save every 60s)")
    print("🧠 AI: Groq API") 
    print("🌐 Host: Render")
    print("================================================")
    
    # Show initial stats
    total_users = len(db.get_all_users())
    total_messages = db.get_total_messages()
    print(f"📊 Loaded: {total_users} users, {total_messages} messages")
    
    # Start auto-save каждую минуту!
    save_thread = Thread(target=auto_save_worker, daemon=True)
    save_thread.start()
    print("💾 Auto-save started (every 60 seconds)")
    
    # Start web server
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print("🌐 24/7 Web server started")
    
    # Start bot
    start_bot()
