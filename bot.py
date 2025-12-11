import os
import asyncio 
import random 
import json 
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters,
)

# **********************************************
## 1. ग्लोबल स्टेट और सेटअप
# **********************************************

# 👉 ⚠️ आपका Telegram Bot Token
# इसे हमने Railway से लेने के लिए बदल दिया है।
TOKEN = os.environ.get('TOKEN') 

# इकोनॉमी/गेमिंग वेरिएबल्स (JSON सेविंग के कारण अब परमानेंट)
USER_SCORES = {} 
PROTECTED_USERS = {}
USER_BALANCE = {}

DATA_FILE = 'game_data.json' # डेटा फाइल का नाम


# **********************************************
## 2. डेटा सेव और लोड फ़ंक्शन्स
# **********************************************

def load_data():
    """'game_data.json' फाइल से स्कोर और बैलेंस लोड करता है।"""
    global USER_SCORES, USER_BALANCE, PROTECTED_USERS
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # JSON keys स्ट्रिंग होते हैं, उन्हें वापस integer ID में बदलें
                USER_SCORES = {int(k): v for k, v in data.get('scores', {}).items()}
                USER_BALANCE = {int(k): v for k, v in data.get('balance', {}).items()}
                PROTECTED_USERS = {int(k): v for k, v in data.get('protected', {}).items()}
                print("डेटा सफलतापूर्वक लोड हुआ।")
        except json.JSONDecodeError:
            print("चेतावनी: डेटा फाइल दूषित है या खाली है। नया डेटाबेस शुरू कर रहे हैं।")
        except Exception as e:
            print(f"डेटा लोड करते समय त्रुटि आई: {e}")
    else:
        print("कोई डेटा फाइल नहीं मिली, नया डेटाबेस शुरू कर रहे हैं।")


def save_data():
    """स्कोर और बैलेंस को 'game_data.json' फाइल में सेव करता है।"""
    data = {
        # IDs को JSON में सेव करने के लिए string में बदलें
        'scores': {str(k): v for k, v in USER_SCORES.items()},
        'balance': {str(k): v for k, v in USER_BALANCE.items()},
        'protected': {str(k): v for k, v in PROTECTED_USERS.items()},
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"डेटा सेव करते समय त्रुटि आई: {e}")


# **********************************************
## 3. कमांड्स
# **********************************************

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """बॉट शुरू होने पर एक आकर्षक परिचय मैसेज भेजता है।"""
    start_message = (
        "✨ Hey Qais 🌙 ~\n"
        "@ You're talking to Qais, **the coolest economy bot** 😎\n"
        "\n"
        "+ **Choose an option below (ग्रुप में चलाएँ):**\n"
        "\n"
        "🔸 **💰 Earn** (`/daily`, `/bal`)\n"
        "🔸 **🔫 Kill** (रिप्लाई करके चलाएँ: `/kill`)\n"
        "🔸 **🛡️ Protect** (चलाएँ: `/protect`)\n"
        "🔸 **❓ More Commands** (चलाएँ: `/help`)\n"
    )
    await update.message.reply_text(start_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """उपलब्ध कमांड्स की सूची दिखाता है।"""
    help_text = (
        "😎 मैं Qais हूँ! \n\n"
        "👑 **SIMPLE BAKA ECONOMY SYSTEM (ग्रुप कमांड्स):**\n"
        "(यह डेटा अब परमानेंटली सेव होगा 💾)\n\n"
        "🔸 **💰 अर्निंग और बैलेंस:**\n"
        "/daily - दैनिक रिवॉर्ड ($1000-$2000) प्राप्त करें (बिना टाइम लॉक के)।\n"
        "/bal - अपना मज़ाकिया बैलेंस (Balance) देखें।\n\n"
        "🔸 **⚔️ किलिंग और प्रोटेक्शन:**\n"
        "/kill (रिप्लाई) - किसी यूज़र को मारकर स्कोर बढ़ाएँ और पॉइंट कमाएँ।\n"
        "/protect - खुद को एक बार के लिए किलिंग से बचाएँ।\n\n"
        "🔸 **📊 लीडरबोर्ड:**\n"
        "/myrank - अपना किल स्कोर और प्रोटेक्शन स्टेटस देखें।\n"
        "/topkillers - टॉप किलर की लिस्ट देखें।\n"
    )
    await update.message.reply_text(help_text)

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """दैनिक रिवॉर्ड देता है।"""
    global USER_BALANCE
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    reward = random.randint(1000, 2000) 
    current_bal = USER_BALANCE.get(user_id, 0)
    USER_BALANCE[user_id] = current_bal + reward
    
    await update.message.reply_text(
        f"💰 **@{user_name}**\n"
        f"• **Daily** - Received ${reward}\n"
        f"• **Current Bal:** ${USER_BALANCE[user_id]}"
    )
    save_data() # <--- डेटा सेव करें

async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """यूज़र का वर्तमान बैलेंस दिखाता है।"""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    balance = USER_BALANCE.get(user_id, 500)
    
    await update.message.reply_text(
        f"👤 **@{user_name}**'s Balance\n"
        f"💰 **Balance:** ${balance}"
    )

async def protect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """यूज़र को अस्थायी प्रोटेक्शन देता है।"""
    global PROTECTED_USERS
    user_id = update.message.from_user.id
    
    if user_id in PROTECTED_USERS:
        await update.message.reply_text("🛡️ आप पहले से ही सुरक्षित हैं! प्रोटेक्शन अभी भी सक्रिय है।")
        return
        
    PROTECTED_USERS[user_id] = True
    await update.message.reply_text("🛡️ **प्रोटेक्शन सक्रिय!** अगले अटैक से आप बच जाएँगे।")
    save_data() # <--- डेटा सेव करें


async def kill_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """रिप्लाई किए गए यूज़र को मारता है, किलर का स्कोर बढ़ाता है, और Baka स्टाइल में रिवॉर्ड दिखाता है।"""
    global USER_SCORES, PROTECTED_USERS, USER_BALANCE
    
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ यह कमांड केवल ग्रुप में काम करती है!")
        return
        
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ कृपया किसी यूज़र के मैसेज का रिप्लाई करके `/kill` चलाएँ।")
        return

    killed_user = update.message.reply_to_message.from_user
    killer_user = update.message.from_user
    killer_id = killer_user.id
    killed_id = killed_user.id
    
    if killer_id == killed_id:
        await update.message.reply_text("😂 क्या यार, खुद को ही मार रहा है? किसी और को मार!", reply_to_message_id=update.message.message_id)
        return
    
    if killed_id in PROTECTED_USERS:
        del PROTECTED_USERS[killed_id]
        await update.message.reply_text(
            f"❌ **अटैक विफल!** @{killed_user.first_name} सुरक्षित था और उसका प्रोटेक्शन टूट गया है।",
            reply_to_message_id=update.message.reply_to_message.message_id
        )
        save_data()
        return

    current_kills = USER_SCORES.get(killer_id, 0)
    USER_SCORES[killer_id] = current_kills + 1
    
    reward = random.randint(100, 200) 
    current_bal = USER_BALANCE.get(killer_id, 0)
    USER_BALANCE[killer_id] = current_bal + reward
    
    kill_message = (
        f"👑 **Qais** 🌙 killed **{killed_user.first_name}** !\n"
        f"💰 Earned: **${reward}**"
    )

    await update.message.reply_text(
        kill_message,
        reply_to_message_id=update.message.message_id 
    )
    save_data() # <--- डेटा सेव करें

async def myrank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """यूज़र का वर्तमान किल काउंट और रैंक दिखाता है।"""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    kill_count = USER_SCORES.get(user_id, 0)
    protection_status = "🛡️ ON" if user_id in PROTECTED_USERS else "⚔️ OFF"
    
    await update.message.reply_text(
        f"👤 **{user_name}** का स्टेटस:\n"
        f"🔥 **कुल किल्स:** {kill_count}\n"
        f"🛡️ **प्रोटेक्शन:** {protection_status}"
    )

async def topkillers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """टॉप 5 किलर्स को दिखाता है।"""
    
    if not USER_SCORES:
        await update.message.reply_text("कोई नहीं मारा गया! लिस्ट खाली है।")
        return

    sorted_killers = sorted(USER_SCORES.items(), key=lambda item: item[1], reverse=True)
    
    top_list = "👑 **TOP 5 KILLERS** 👑\n\n"
    
    for rank, (user_id, kills) in enumerate(sorted_killers[:5]):
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            user_name = member.user.first_name
        except Exception:
            user_name = f"Unknown User"

        top_list += f"**{rank + 1}.** {user_name} — **{kills}** किल्स\n"
        
    await update.message.reply_text(top_list)


# **********************************************
## 4. मुख्य रनिंग फ़ंक्शन
# **********************************************

def main() -> None:
    # ⚠️ सबसे पहले, पुरानी स्थिति को लोड करें
    load_data() 
    print("बॉट एप्लीकेशन बना रहे हैं...")
    
    # TOKEN की जाँच करें (क्योंकि अब यह os.environ से आ रहा है)
    if not TOKEN:
        print("❌ त्रुटि: TOKEN एनवायरनमेंट वेरिएबल सेट नहीं है। कृपया Railway पर TOKEN सेट करें।")
        return

    application = Application.builder().token(TOKEN).build()

    # कमांड हैंडलर्स 
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command)) 
    
    # गेमिंग/इकोनॉमी कमांड्स
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("bal", bal_command))
    application.add_handler(CommandHandler("kill", kill_command)) 
    application.add_handler(CommandHandler("protect", protect_command))
    application.add_handler(CommandHandler("myrank", myrank_command)) 
    application.add_handler(CommandHandler("topkillers", topkillers_command)) 
    
    # बॉट को शुरू करें
    print("बॉट शुरू हो रहा है...")
    application.run_polling(poll_interval=3) 

if __name__ == '__main__':
    main()