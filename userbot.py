import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from flask import Flask
from threading import Thread

# ===== API টোকেন (Environment Variable থেকে নিবে) =====
API_ID = int(os.environ.get('API_ID', 33678168))
API_HASH = os.environ.get('API_HASH', '3e2a43d930ac6ff982ef50d4f6857751')

# ===== টার্গেট লিস্ট (এডিট করে দিলাম) =====
TARGETS = [
    {'type': 'phone', 'target': '+8801922498942', 'msg': 'Please khoma kore dew\nKhoma korba ki na bolbo\nI am sorry'},
    {'type': 'username', 'target': 'Gonitbujina', 'msg': 'Farhan tui ki valo hobi na, tui ekta gay'},
    {'type': 'username', 'target': 'Spondon100', 'msg': 'Kire ki koros mama ar poris na'},
    {'type': 'phone', 'target': '+8801620407362', 'msg': 'Churi kine ditei hobe??\nNa kine dile hoy na??'},
    {'type': 'username', 'target': 'sakib_all_hasan_2008', 'msg': 'Hello bro, Im working'},
]

DELAY_BETWEEN_MESSAGES = 1
DELAY_BETWEEN_CYCLES = 1

# ===== Flask app (Render এর জন্য) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Userbot is running!"

@app.route('/health')
def health():
    return "OK", 200

# ===== Userbot কোড =====
client = TelegramClient('userbot_session', API_ID, API_HASH)
sending_active = False
current_task = None

async def send_to_phone(phone, message):
    try:
        contact = InputPhoneContact(client_id=0, phone=phone, first_name='User', last_name='')
        result = await client(ImportContactsRequest([contact]))
        if result.users:
            await client.send_message(result.users[0], message)
            print(f'✅ ফোনে পাঠানো হয়েছে: {phone}')
            return True
        else:
            print(f'❌ {phone} - টেলিগ্রাম ইউজার পাওয়া যায়নি')
            return False
    except Exception as e:
        print(f'❌ {phone} - ত্রুটি: {e}')
        return False

async def send_to_username(username, message):
    try:
        await client.send_message(username, message)
        print(f'✅ ইউজারনেমে পাঠানো হয়েছে: {username}')
        return True
    except Exception as e:
        print(f'❌ {username} - ত্রুটি: {e}')
        return False

async def message_sender():
    global sending_active
    cycle_count = 0
    
    while sending_active:
        cycle_count += 1
        print(f'\n🔄 সাইকেল #{cycle_count} শুরু হচ্ছে...')
        
        for target in TARGETS:
            if not sending_active:
                break
            
            if target['type'] == 'phone':
                await send_to_phone(target['target'], target['msg'])
            else:
                await send_to_username(target['target'], target['msg'])
            
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
        
        if sending_active:
            print(f'\n⏸️ সাইকেল #{cycle_count} শেষ। {DELAY_BETWEEN_CYCLES} সেকেন্ড বিরতি...')
            await asyncio.sleep(DELAY_BETWEEN_CYCLES)

@client.on(events.NewMessage(from_users='me'))
async def handle_command(event):
    global sending_active, current_task
    msg = event.message.text.lower()
    
    if msg == '/start':
        if not sending_active:
            sending_active = True
            current_task = asyncio.create_task(message_sender())
            await event.reply(f'✅ {len(TARGETS)} জনকে মেসেজ শুরু হয়েছে।\n/stop লিখো থামাতে।')
        else:
            await event.reply('⚠️ ইতিমধ্যেই চলছে।')
    
    elif msg == '/stop':
        if sending_active:
            sending_active = False
            if current_task:
                current_task.cancel()
            await event.reply('⏹️ বন্ধ করা হয়েছে।')
        else:
            await event.reply('ℹ️ কিছু চলছিল না।')

async def run_bot():
    await client.start()
    print('=' * 50)
    print('🤖 ইউজারবট চালু হয়েছে!')
    print(f'📋 মোট টার্গেট: {len(TARGETS)} জন')
    print('=' * 50)
    await client.run_until_disconnected()

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

if __name__ == "__main__":
    # ব্যাকগ্রাউন্ডে বট চালাও
    thread = Thread(target=start_bot)
    thread.start()
    # Flask সার্ভার চালাও (Render এর জন্য)
    app.run(host='0.0.0.0', port=8080)
