import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler

# ===== LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
BOT_TOKEN = "8569654657:AAHe9tCSMqezL3YzEUAipVQsIlU9FgAYvok"
TARGET_GROUP_ID = -1003248802557
ADMIN_ID = 7595358595
DATABASE_FILE = "users_db.json"

# ===== PAYMENT INFO =====
UPI_ID = "sumal.somu@ptyes"
PAYMENT_QR = "https://files.catbox.moe/lmal2k.jpg"
ADMIN_USERNAME = "@Are_lqdaa"

# ===== PRICING =====
PACKAGES = {
    20: 100,
    50: 500,
    80: 1000,
    300: 5000
}

# ===== STORAGE =====
users_db: Dict[str, Any] = {}
payment_data: Dict[str, Any] = {}

# ===== DATABASE =====
def load_db():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db():
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, indent=2, ensure_ascii=False)

def init_user(user_id: str, name: str):
    users_db[user_id] = {
        "name": name,
        "posts": 0,
        "sent": 0,
        "purchased": 0,
        "joined": datetime.now().isoformat()
    }
    save_db()

# ===== KEYBOARDS =====
def main_menu():
    keyboard = [
        [KeyboardButton("💰 My Balance"), KeyboardButton("🛒 Buy Posts")],
        [KeyboardButton("❓ Help"), KeyboardButton("📞 Support")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def buy_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Pay Now (UPI)", callback_data="pay")],
        [InlineKeyboardButton("💬 Contact Admin", callback_data="admin")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def balance_menu():
    keyboard = [
        [InlineKeyboardButton("🛒 Buy More Posts", callback_data="pay")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    name = update.message.from_user.full_name or "User"
    
    if user_id not in users_db:
        init_user(user_id, name)
    
    welcome = f"""
━━━━━━━━━━━━━━━━━━━━
🚀 <b>MESSAGE FORWARD BOT</b> 🚀
━━━━━━━━━━━━━━━━━━━━

<b>✨ What We Do:</b>
Forward your messages to our exclusive group instantly!

<b>💰 Pricing Plans:</b>

┏━━━━━━━━━━━━━┓
┃  100 Posts → ₹20
┃  500 Posts → ₹50
┃ 1000 Posts → ₹80
┃ 5000 Posts → ₹300
┗━━━━━━━━━━━━━┛

<b>⚡ How It Works:</b>
1️⃣ Buy post credits
2️⃣ Send any message here
3️⃣ We forward to group
4️⃣ Everyone sees it!

<b>📱 Supported:</b>
✓ Text  ✓ Photos  ✓ Videos  ✓ Docs

━━━━━━━━━━━━━━━━━━━━
👇 <i>Use buttons below to start</i> 👇
"""
    
    await update.message.reply_text(welcome, parse_mode='HTML', reply_markup=main_menu())

# ===== MY BALANCE =====
async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
    if user_id not in users_db:
        await update.message.reply_text("❌ Please /start first!", reply_markup=main_menu())
        return
    
    user = users_db[user_id]
    posts = user.get('posts', 0)
    sent = user.get('sent', 0)
    purchased = user.get('purchased', 0)
    
    # Status emoji and message
    if posts > 50:
        status = "🟢"
        status_text = "Active"
    elif posts > 0:
        status = "🟡"
        status_text = "Low Balance"
    else:
        status = "🔴"
        status_text = "Out of Credits"
    
    balance = f"""
━━━━━━━━━━━━━━━━━━━━
💰 <b>MY BALANCE</b> 💰
━━━━━━━━━━━━━━━━━━━━

{status} <b>Status:</b> {status_text}

━━━━━━━━━━━━━━━━━━━━

💎 <b>Posts Remaining:</b>
<code>{posts}</code>

📨 <b>Messages Sent:</b>
{sent}

🛒 <b>Total Purchased:</b>
{purchased} posts

━━━━━━━━━━━━━━━━━━━━
"""
    
    if posts <= 0:
        balance += "\n⚠️ <b>Out of credits!</b>\n👇 Buy more to continue posting"
        keyboard = [[InlineKeyboardButton("🛒 Buy Posts Now", callback_data="pay")],
                   [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]
        markup = InlineKeyboardMarkup(keyboard)
    elif posts <= 10:
        balance += "\n⚠️ <b>Low balance warning!</b>\n👇 Consider buying more"
        keyboard = [[InlineKeyboardButton("🛒 Buy More Posts", callback_data="pay")],
                   [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]
        markup = InlineKeyboardMarkup(keyboard)
    else:
        balance += "\n✅ <b>You're all set!</b>\nJust forward messages to post."
        keyboard = [[InlineKeyboardButton("🛒 Buy More Posts", callback_data="pay")],
                   [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]
        markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(balance, parse_mode='HTML', reply_markup=markup)

# ===== BUY POSTS =====
async def buy_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pricing = f"""
━━━━━━━━━━━━━━━━━━━━
🛒 <b>PRICING PLANS</b> 🛒
━━━━━━━━━━━━━━━━━━━━

<b>Choose Your Package:</b>

┏━━━━━━━━━━━━━━━┓
┃ 🔰 <b>Starter Pack</b>
┃ 100 Posts → ₹20
┃ <i>₹0.20 per post</i>
┗━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━┓
┃ ⭐ <b>Basic Pack</b>
┃ 500 Posts → ₹50
┃ <i>₹0.10 per post</i>
┗━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━┓
┃ 💎 <b>Pro Pack</b>
┃ 1000 Posts → ₹80
┃ <i>₹0.08 per post</i>
┗━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━┓
┃ 👑 <b>Premium Pack</b>
┃ 5000 Posts → ₹300
┃ <i>₹0.06 per post</i>
┗━━━━━━━━━━━━━━━┛

━━━━━━━━━━━━━━━━━━━━
💳 <i>Instant activation!</i>
"""
    
    await update.message.reply_text(pricing, parse_mode='HTML', reply_markup=buy_menu())

# ===== HELP =====
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
━━━━━━━━━━━━━━━━━━━━
❓ <b>HELP GUIDE</b> ❓
━━━━━━━━━━━━━━━━━━━━

<b>🎯 Getting Started:</b>

1️⃣ <b>Buy Credits</b>
   Click "🛒 Buy Posts"
   Choose a package
   Complete payment

2️⃣ <b>Post Messages</b>
   Just send any message here
   We'll forward to group
   1 message = 1 credit

3️⃣ <b>Check Balance</b>
   Click "💰 My Balance"
   View remaining posts

━━━━━━━━━━━━━━━━━━━━

<b>💳 Payment Steps:</b>

• Click "Pay Now"
• Scan QR / Use UPI
• Pay the amount
• Send screenshot
• Enter amount & UTR
• Wait for approval (1-2h)

━━━━━━━━━━━━━━━━━━━━

<b>📞 Need Help?</b>
Contact: {ADMIN_USERNAME}
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]
    await update.message.reply_text(help_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ===== SUPPORT =====
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = f"""
━━━━━━━━━━━━━━━━━━━━
📞 <b>SUPPORT</b> 📞
━━━━━━━━━━━━━━━━━━━━

<b>👤 Admin Contact:</b>
{ADMIN_USERNAME}

<b>⏰ Response Time:</b>
Usually within 1-2 hours

<b>💬 We Help With:</b>
✓ Payment issues
✓ Technical problems  
✓ Bulk orders
✓ Custom packages

━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("💬 Message Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
    ]
    await update.message.reply_text(support_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ===== CALLBACKS =====
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()
    
    if query.data == "back":
        welcome = f"""
━━━━━━━━━━━━━━━━━━━━
🚀 <b>MESSAGE FORWARD BOT</b> 🚀
━━━━━━━━━━━━━━━━━━━━

<b>✨ What We Do:</b>
Forward your messages to our exclusive group instantly!

<b>💰 Pricing Plans:</b>

┏━━━━━━━━━━━━━┓
┃  100 Posts → ₹20
┃  500 Posts → ₹50
┃ 1000 Posts → ₹80
┃ 5000 Posts → ₹300
┗━━━━━━━━━━━━━┛

<b>⚡ How It Works:</b>
1️⃣ Buy post credits
2️⃣ Send any message here
3️⃣ We forward to group
4️⃣ Everyone sees it!

<b>📱 Supported:</b>
✓ Text  ✓ Photos  ✓ Videos  ✓ Docs

━━━━━━━━━━━━━━━━━━━━
👇 <i>Use buttons below to start</i> 👇
"""
        try:
            await query.edit_message_text(
                welcome,
                parse_mode='HTML'
            )
        except:
            await query.message.reply_text(welcome, parse_mode='HTML', reply_markup=main_menu())
    
    elif query.data == "pay":
        payment_data[user_id] = {"step": 1}
        
        payment_info = f"""
━━━━━━━━━━━━━━━━━━━━
💳 <b>UPI PAYMENT</b> 💳
━━━━━━━━━━━━━━━━━━━━

<b>UPI ID:</b> <code>{UPI_ID}</code>
<i>(Tap to copy)</i>

<b>📱 Steps:</b>

1️⃣ Scan QR or copy UPI ID
2️⃣ Enter amount (₹20/50/80/300)
3️⃣ Complete payment
4️⃣ Send screenshot HERE
5️⃣ Enter amount
6️⃣ Enter UTR number

━━━━━━━━━━━━━━━━━━━━

⏳ <b>Waiting for screenshot...</b>
"""
        
        await query.message.reply_photo(
            photo=PAYMENT_QR,
            caption=payment_info,
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    
    elif query.data == "admin":
        keyboard = [
            [InlineKeyboardButton("💬 Open Chat", url=f"https://t.me/{ADMIN_USERNAME[1:]}")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.message.reply_text(
            f"📞 <b>Contact Admin:</b> {ADMIN_USERNAME}\n\n"
            f"Say: <i>Hi! I want to buy posts</i>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===== PAYMENT PROCESSING =====
async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.full_name or "User"
    
    if user_id not in payment_data:
        return False
    
    step = payment_data[user_id].get("step", 0)
    
    # Step 1: Screenshot
    if step == 1 and update.message.photo:
        payment_data[user_id]["screenshot"] = update.message.photo[-1].file_id
        payment_data[user_id]["step"] = 2
        
        await update.message.reply_text(
            "✅ <b>Screenshot Received!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📝 Now send the <b>amount</b> you paid\n\n"
            "Example: <code>50</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
        return True
    
    # Step 2: Amount
    elif step == 2 and update.message.text:
        text = update.message.text.strip()
        
        if not text.isdigit():
            await update.message.reply_text("❌ Please send only numbers!\nExample: 50")
            return True
        
        amount = int(text)
        if amount < 10 or amount > 10000:
            await update.message.reply_text("❌ Invalid amount! Enter between ₹10-₹10,000")
            return True
        
        payment_data[user_id]["amount"] = amount
        payment_data[user_id]["step"] = 3
        
        await update.message.reply_text(
            f"✅ <b>Amount: ₹{amount}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 Now send the <b>UTR number</b>\n\n"
            f"Example: <code>123456789012</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
        return True
    
    # Step 3: UTR
    elif step == 3 and update.message.text:
        utr = update.message.text.strip()
        
        if len(utr) < 6:
            await update.message.reply_text("❌ UTR too short! Please check and send again.")
            return True
        
        payment_data[user_id]["utr"] = utr
        
        # Send to admin
        amount = payment_data[user_id]["amount"]
        posts = PACKAGES.get(amount, int(amount / 0.2))
        
        admin_msg = f"""
━━━━━━━━━━━━━━━━━━━━
🔔 <b>NEW PAYMENT</b>
━━━━━━━━━━━━━━━━━━━━

👤 <b>User:</b> {user_name}
🆔 <b>ID:</b> <code>{user_id}</code>

💰 <b>Amount:</b> ₹{amount}
🔢 <b>UTR:</b> <code>{utr}</code>
📦 <b>Posts:</b> {posts}

⏰ {datetime.now().strftime('%d %b, %H:%M')}

━━━━━━━━━━━━━━━━━━━━

<b>Quick Approve:</b>
/approve {user_id} {posts}
"""
        
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=payment_data[user_id]["screenshot"],
                caption=admin_msg,
                parse_mode='HTML'
            )
        except:
            await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
        
        del payment_data[user_id]
        
        await update.message.reply_text(
            "✅ <b>Payment Submitted!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 <b>Details:</b>\n"
            f"• Amount: ₹{amount}\n"
            f"• UTR: {utr}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏳ <b>What's Next?</b>\n\n"
            "✓ Admin will verify\n"
            "✓ Posts added to account\n"
            "✓ You'll be notified\n\n"
            "⏱️ Processing: 30 min - 2 hours\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Thank you! 🙏",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
        return True
    
    return False

# ===== FORWARD MESSAGE =====
async def forward_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
    if user_id not in users_db:
        init_user(user_id, update.message.from_user.full_name or "User")
    
    user = users_db[user_id]
    
    if user.get("posts", 0) <= 0:
        keyboard = [[InlineKeyboardButton("🛒 Buy Posts", callback_data="pay")]]
        await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>No credits left!</b>\n\n"
            "💰 Balance: <b>0 posts</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Click below to buy more",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    try:
        await context.bot.forward_message(
            chat_id=TARGET_GROUP_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        
        user["posts"] -= 1
        user["sent"] += 1
        save_db()
        
        remaining = user["posts"]
        
        msg = "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "✅ <b>Posted Successfully!</b>\n\n"
        msg += f"💰 Remaining: <b>{remaining} posts</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        
        if remaining <= 5:
            msg += "\n⚠️ Low balance!\n"
            keyboard = [[InlineKeyboardButton("🛒 Buy More", callback_data="pay")]]
            markup = InlineKeyboardMarkup(keyboard)
        else:
            markup = main_menu()
        
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=markup)
        
    except Exception as e:
        await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ <b>Failed to post</b>\n\n"
            f"Error: {str(e)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Contact: {ADMIN_USERNAME}",
            parse_mode='HTML'
        )

# ===== MESSAGE HANDLER =====
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message.text else ""
    user_id = str(update.message.from_user.id)
    
    if text == "💰 My Balance":
        await my_balance(update, context)
    elif text == "🛒 Buy Posts":
        await buy_posts(update, context)
    elif text == "❓ Help":
        await help_cmd(update, context)
    elif text == "📞 Support":
        await support(update, context)
    elif text == "📋 User List" and update.message.from_user.id == ADMIN_ID:
        await user_list(update, context)
    elif user_id in payment_data:
        await process_payment(update, context)
    else:
        await forward_msg(update, context)

# ===== ADMIN: APPROVE =====
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /approve <user_id> <posts>\n"
            "Example: /approve 123456789 100"
        )
        return
    
    user_id = str(context.args[0])
    posts = int(context.args[1])
    
    if user_id not in users_db:
        users_db[user_id] = {
            "name": "Unknown",
            "posts": posts,
            "sent": 0,
            "purchased": posts,
            "joined": datetime.now().isoformat()
        }
    else:
        users_db[user_id]["posts"] += posts
        users_db[user_id]["purchased"] = users_db[user_id].get("purchased", 0) + posts
    
    save_db()
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"""
━━━━━━━━━━━━━━━━━━━━
🎉 <b>Payment Approved!</b>
━━━━━━━━━━━━━━━━━━━━

✅ <b>{posts} Posts</b> added!

💰 <b>Total Balance:</b> {users_db[user_id]['posts']} posts

━━━━━━━━━━━━━━━━━━━━

🚀 Start posting now!
Just send any message here.

Thank you! 🙏
""",
            parse_mode='HTML',
            reply_markup=main_menu()
        )
    except:
        pass
    
    await update.message.reply_text(
        f"✅ <b>Approved!</b>\n\n"
        f"User: <code>{user_id}</code>\n"
        f"Posts: {posts}\n"
        f"Total: {users_db[user_id]['posts']}",
        parse_mode='HTML'
    )

# ===== ADMIN: USER LIST =====
async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    if not users_db:
        await update.message.reply_text("No users yet!")
        return
    
    total_posts = sum(u.get('posts', 0) for u in users_db.values())
    total_sent = sum(u.get('sent', 0) for u in users_db.values())
    active = sum(1 for u in users_db.values() if u.get('posts', 0) > 0)
    
    msg = f"""
━━━━━━━━━━━━━━━━━━━━
📊 <b>USER DATABASE</b> 📊
━━━━━━━━━━━━━━━━━━━━

<b>📈 Stats:</b>
• Total Users: {len(users_db)}
• Active: {active}
• Posts Available: {total_posts}
• Messages Sent: {total_sent}

━━━━━━━━━━━━━━━━━━━━

<b>👥 Users:</b>

"""
    
    for uid, data in sorted(users_db.items(), key=lambda x: x[1].get('posts', 0), reverse=True)[:30]:
        status = "🟢" if data.get('posts', 0) > 0 else "🔴"
        msg += f"{status} <b>{data.get('name', 'Unknown')}</b>\n"
        msg += f"   Posts: {data.get('posts', 0)} | Sent: {data.get('sent', 0)}\n"
        msg += f"   ID: <code>{uid}</code>\n\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━"
    
    await update.message.reply_text(msg, parse_mode='HTML')

# ===== ADMIN: REMOVE =====
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /remove <user_id>")
        return
    
    user_id = str(context.args[0])
    
    if user_id in users_db:
        name = users_db[user_id].get('name', 'Unknown')
        del users_db[user_id]
        save_db()
        await update.message.reply_text(f"✅ Removed: {name} ({user_id})")
    else:
        await update.message.reply_text("❌ User not found!")

# ===== ADMIN: BROADCAST =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    msg = ' '.join(context.args)
    success = 0
    
    for uid in users_db.keys():
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"━━━━━━━━━━━━━━━━━━━━\n"
                     f"📢 <b>ANNOUNCEMENT</b>\n"
                     f"━━━━━━━━━━━━━━━━━━━━\n\n"
                     f"{msg}\n\n"
                     f"━━━━━━━━━━━━━━━━━━━━",
                parse_mode='HTML'
            )
            success += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Sent to {success} users")

# ===== ADMIN: STATS =====
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    
    total = len(users_db)
    active = sum(1 for u in users_db.values() if u.get('posts', 0) > 0)
    posts = sum(u.get('posts', 0) for u in users_db.values())
    sent = sum(u.get('sent', 0) for u in users_db.values())
    purchased = sum(u.get('purchased', 0) for u in users_db.values())
    revenue = (purchased / 100) * 20
    
    stats = f"""
━━━━━━━━━━━━━━━━━━━━
📊 <b>STATISTICS</b> 📊
━━━━━━━━━━━━━━━━━━━━

<b>👥 Users:</b>
• Total: {total}
• Active: {active}
• Inactive: {total - active}

<b>💰 Posts:</b>
• Available: {posts}
• Sent: {sent}
• Purchased: {purchased}

<b>💵 Revenue:</b>
• ~₹{revenue:.0f}

━━━━━━━━━━━━━━━━━━━━
"""
    
    await update.message.reply_text(stats, parse_mode='HTML')

# ===== MAIN =====
def main():
    global users_db
    users_db = load_db()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("list", user_list))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", admin_stats))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Messages
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL,
        handle_msg
    ))
    
    print("=" * 40)
    print("🚀 BOT IS RUNNING!")
    print("🔥 Press Ctrl+C to stop")
    print("=" * 40)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()