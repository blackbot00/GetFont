# bot.py
import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message
)
from pyrogram.errors import FloodWait
from config import Config
from fonts import FONTS, generate_all_fonts

# Bot Setup
app = Client(
    "font_changer_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Constants
START_MSG = """
👋 **Hello {user}!**

✨ Welcome to **Premium Font Changer Bot** ✨

🔥 **Features:**
• 50+ Premium Fonts
• Fancy Unicode Styles
• Copy & Paste Ready
• Fast & Reliable

💡 **Just send me any text and I'll convert it into multiple font styles!**

✍️ Type /fonts to see all available fonts
📖 Type /help for usage instructions
"""

HELP_MSG = """
📖 **How to Use Font Changer Bot**

**📝 Basic Usage:**
→ Just send any text to convert
→ Bot will reply with all font styles

**⚡ Inline Mode:**
→ Type `@your_bot_username text` in any chat
→ Select your favorite font style

**📋 Commands:**
• /start - Start the bot
• /fonts - View all font styles
• /help - Show this help message
• /about - About the bot

**💡 Tips:**
• Some fonts may not work on all devices
• Unicode fonts work on most platforms
• Best viewed on Telegram apps
"""

ABOUT_MSG = """
ℹ️ **About Font Changer Bot**

🤖 **Bot Name:** Premium Font Changer
📝 **Version:** 2.0 Premium
👨‍💻 **Developer:** [Your Name]
🌐 **Source:** Open Source

📊 **Stats:**
• Total Fonts: {fonts}
• Users Served: {users}

⚡ **Powered By:**
• Pyrogram
• Python 3.10+

❤️ **Made with love for Telegram users!**
"""

FONTS_PER_PAGE = 10

# Store user stats
user_stats = {"total_users": 0, "total_conversions": 0}
users_db = set()

# Keyboard Functions
def start_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 View Fonts", callback_data="view_fonts"),
            InlineKeyboardButton("📖 Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("👥 Channel", url="https://t.me/your_channel")
        ]
    ])

def fonts_keyboard(page=0):
    fonts_list = list(FONTS.keys())
    total_pages = (len(fonts_list) + FONTS_PER_PAGE - 1) // FONTS_PER_PAGE
    
    keyboard = []
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"fonts_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"fonts_{page+1}"))
    
    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    
    return InlineKeyboardMarkup(keyboard)

def result_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Copy All", callback_data="copy_all"),
            InlineKeyboardButton("🔄 Convert More", callback_data="home")
        ]
    ])

# Handlers
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id not in users_db:
        users_db.add(user_id)
        user_stats["total_users"] += 1
    
    await message.reply_text(
        START_MSG.format(user=user_name),
        reply_markup=start_keyboard(),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    await message.reply_text(
        HELP_MSG,
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

@app.on_message(filters.command("about"))
async def about_command(client, message: Message):
    await message.reply_text(
        ABOUT_MSG.format(
            fonts=len(FONTS),
            users=user_stats["total_users"]
        ),
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

@app.on_message(filters.command("fonts"))
async def fonts_command(client, message: Message):
    fonts_list = list(FONTS.keys())
    total_fonts = len(fonts_list)
    
    # Show first page fonts
    start_idx = 0
    end_idx = min(FONTS_PER_PAGE, total_fonts)
    
    text = f"🎨 **Available Font Styles**\n\n"
    text += f"📊 **Total Fonts:** {total_fonts}\n\n"
    text += "**Sample Fonts:**\n"
    
    for i, font_name in enumerate(fonts_list[start_idx:end_idx], 1):
        sample = ""
        for char in "Hello":
            sample += FONTS[font_name].get(char, char)
        text += f"`{i}.` {font_name} → {sample}\n"
    
    text += f"\n💡 _Send any text to see all fonts!_"
    
    await message.reply_text(
        text,
        reply_markup=fonts_keyboard(0),
        parse_mode=enums.ParseMode.MARKDOWN
    )

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about", "fonts"]))
async def convert_text(client, message: Message):
    text = message.text
    user_stats["total_conversions"] += 1
    
    # Generate all fonts
    results = generate_all_fonts(text)
    
    # Create response
    response = f"✨ **Font Conversion Results**\n\n"
    response += f"📝 **Original:** `{text}`\n\n"
    response += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for font_name, converted in results[:20]:  # Limit to 20 fonts in message
        response += f"**{font_name}:**\n`{converted}`\n\n"
    
    if len(results) > 20:
        response += f"_...and {len(results) - 20} more fonts!_"
    
    response += "\n━━━━━━━━━━━━━━━━━━━━━\n"
    response += "💡 _Tap on any font to copy!_"
    
    await message.reply_text(
        response,
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=result_keyboard()
    )

@app.on_callback_query()
async def callback_handler(client, callback: CallbackQuery):
    data = callback.data
    user = callback.from_user
    
    if data == "ignore":
        await callback.answer()
        return
    
    if data == "home":
        await callback.message.edit_text(
            START_MSG.format(user=user.first_name),
            reply_markup=start_keyboard(),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await callback.answer()
    
    elif data == "help":
        await callback.message.edit_text(
            HELP_MSG,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await callback.answer()
    
    elif data == "about":
        await callback.message.edit_text(
            ABOUT_MSG.format(
                fonts=len(FONTS),
                users=user_stats["total_users"]
            ),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await callback.answer()
    
    elif data == "view_fonts":
        fonts_list = list(FONTS.keys())
        total_fonts = len(fonts_list)
        
        text = f"🎨 **Available Font Styles**\n\n"
        text += f"📊 **Total Fonts:** {total_fonts}\n\n"
        text += "**Sample Fonts:**\n"
        
        for i, font_name in enumerate(fonts_list[:FONTS_PER_PAGE], 1):
            sample = ""
            for char in "Hello":
                sample += FONTS[font_name].get(char, char)
            text += f"`{i}.` {font_name} → {sample}\n"
        
        text += f"\n💡 _Send any text to see all fonts!_"
        
        await callback.message.edit_text(
            text,
            reply_markup=fonts_keyboard(0),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await callback.answer()
    
    elif data.startswith("fonts_"):
        page = int(data.split("_")[1])
        fonts_list = list(FONTS.keys())
        total_fonts = len(fonts_list)
        total_pages = (total_fonts + FONTS_PER_PAGE - 1) // FONTS_PER_PAGE
        
        start_idx = page * FONTS_PER_PAGE
        end_idx = min(start_idx + FONTS_PER_PAGE, total_fonts)
        
        text = f"🎨 **Available Font Styles**\n\n"
        text += f"📊 **Total Fonts:** {total_fonts}\n\n"
        text += "**Sample Fonts:**\n"
        
        for i, font_name in enumerate(fonts_list[start_idx:end_idx], start_idx + 1):
            sample = ""
            for char in "Hello":
                sample += FONTS[font_name].get(char, char)
            text += f"`{i}.` {font_name} → {sample}\n"
        
        text += f"\n💡 _Send any text to see all fonts!_"
        
        await callback.message.edit_text(
            text,
            reply_markup=fonts_keyboard(page),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await callback.answer()
    
    elif data == "copy_all":
        await callback.answer("📋 Long press on any font to copy!", show_alert=True)

# Inline Mode Handler
@app.on_inline_query()
async def inline_query_handler(client, inline_query):
    query = inline_query.query.strip()
    
    if not query:
        # Show default message
        results = [
            dict(
                type="article",
                title="Type something to convert!",
                description="Enter text after @bot_username",
                input_message_content=dict(
                    message_text="🎨 **Font Changer Bot**\n\nType any text after the bot username to convert it into different fonts!",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            )
        ]
        await inline_query.answer(results, cache_time=1)
        return
    
    # Generate fonts
    all_fonts = generate_all_fonts(query)
    
    results = []
    for font_name, converted in all_fonts[:50]:  # Limit to 50 results
        results.append(
            dict(
                type="article",
                title=converted,
                description=f"Font: {font_name}",
                input_message_content=dict(
                    message_text=converted
                ),
                thumb_url="https://telegra.ph/file/abc123.png"  # Add your thumb URL
            )
        )
    
    await inline_query.answer(results, cache_time=1)

# Run Bot
if __name__ == "__main__":
    print("🤖 Font Changer Bot Starting...")
    print(f"📊 Total Fonts Loaded: {len(FONTS)}")
    app.run()
