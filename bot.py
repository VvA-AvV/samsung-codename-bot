# samsung_codename_bot.py
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Samsung device codename database
DEVICE_DATABASE = {
    # Galaxy Note series
    "note 10": {"codename": "d1", "model": "SM-N970F", "chipset": "Exynos 9825 / SDM855"},
    "note 10+": {"codename": "d2x", "model": "SM-N975F", "chipset": "Exynos 9825 / SDM855"},
    "note 10 plus": {"codename": "d2x", "model": "SM-N975F", "chipset": "Exynos 9825 / SDM855"},
    "note 10+ 5g": {"codename": "d2xq", "model": "SM-N976B", "chipset": "Exynos 9825"},
    "note 10 lite": {"codename": "r7", "model": "SM-N770F", "chipset": "Exynos 9810"},
    
    # Galaxy S series (flagship)
    "s10": {"codename": "beyond1", "model": "SM-G973F", "chipset": "Exynos 9820 / SDM855"},
    "s10+": {"codename": "beyond2", "model": "SM-G975F", "chipset": "Exynos 9820 / SDM855"},
    "s10 plus": {"codename": "beyond2", "model": "SM-G975F", "chipset": "Exynos 9820 / SDM855"},
    "s10e": {"codename": "beyond0", "model": "SM-G970F", "chipset": "Exynos 9820 / SDM855"},
    "s10 5g": {"codename": "beyondx", "model": "SM-G977B", "chipset": "Exynos 9820"},
    "s10 lite": {"codename": "r5q", "model": "SM-G770F", "chipset": "SDM855"},
    
    "s20": {"codename": "x1s", "model": "SM-G980F", "chipset": "Exynos 990 / SDM865"},
    "s20+": {"codename": "y2s", "model": "SM-G985F", "chipset": "Exynos 990 / SDM865"},
    "s20 plus": {"codename": "y2s", "model": "SM-G985F", "chipset": "Exynos 990 / SDM865"},
    "s20 ultra": {"codename": "z3s", "model": "SM-G988B", "chipset": "Exynos 990 / SDM865"},
    "s20 fe": {"codename": "r8s", "model": "SM-G780F", "chipset": "Exynos 990 / SDM865"},
    
    "s21": {"codename": "o1s", "model": "SM-G991B", "chipset": "Exynos 2100 / SDM888"},
    "s21+": {"codename": "t2s", "model": "SM-G996B", "chipset": "Exynos 2100 / SDM888"},
    "s21 plus": {"codename": "t2s", "model": "SM-G996B", "chipset": "Exynos 2100 / SDM888"},
    "s21 ultra": {"codename": "p3s", "model": "SM-G998B", "chipset": "Exynos 2100 / SDM888"},
    "s21 fe": {"codename": "r9s", "model": "SM-G990B", "chipset": "Exynos 2100 / SDM888"},
    
    "s22": {"codename": "r0s", "model": "SM-S901B", "chipset": "Exynos 2200 / SDM8G1"},
    "s22+": {"codename": "g0s", "model": "SM-S906B", "chipset": "Exynos 2200 / SDM8G1"},
    "s22 plus": {"codename": "g0s", "model": "SM-S906B", "chipset": "Exynos 2200 / SDM8G1"},
    "s22 ultra": {"codename": "b0s", "model": "SM-S908B", "chipset": "Exynos 2200 / SDM8G1"},
    
    "s23": {"codename": "dm1q", "model": "SM-S911B", "chipset": "SDM8G2"},
    "s23+": {"codename": "dm2q", "model": "SM-S916B", "chipset": "SDM8G2"},
    "s23 plus": {"codename": "dm2q", "model": "SM-S916B", "chipset": "SDM8G2"},
    "s23 ultra": {"codename": "dm3q", "model": "SM-S918B", "chipset": "SDM8G2"},
    "s23 fe": {"codename": "r11s", "model": "SM-S711B", "chipset": "Exynos 2200 / SDM8G1"},
    
    "s24": {"codename": "e1s", "model": "SM-S921B", "chipset": "Exynos 2400 / SDM8G3"},
    "s24+": {"codename": "e2s", "model": "SM-S926B", "chipset": "Exynos 2400 / SDM8G3"},
    "s24 plus": {"codename": "e2s", "model": "SM-S926B", "chipset": "Exynos 2400 / SDM8G3"},
    "s24 ultra": {"codename": "e3q", "model": "SM-S928B", "chipset": "SDM8G3"},
    "s24 fe": {"codename": "r12s", "model": "SM-S721B", "chipset": "Exynos 2400e"},
    
    # Galaxy Note 20 series
    "note 20": {"codename": "c1s", "model": "SM-N980F", "chipset": "Exynos 990 / SDM865+"},
    "note 20 ultra": {"codename": "c2s", "model": "SM-N985F", "chipset": "Exynos 990 / SDM865+"},
    "note 20 5g": {"codename": "c1q", "model": "SM-N981B", "chipset": "SDM865+"},
    "note 20 ultra 5g": {"codename": "c2q", "model": "SM-N986B", "chipset": "SDM865+"},
    
    # Galaxy Z Fold series
    "fold": {"codename": "winner", "model": "SM-F900F", "chipset": "SDM855"},
    "z fold 2": {"codename": "f2q", "model": "SM-F916B", "chipset": "SDM865+"},
    "z fold 3": {"codename": "q2q", "model": "SM-F926B", "chipset": "SDM888"},
    "z fold 4": {"codename": "q4q", "model": "SM-F936B", "chipset": "SDM8+G1"},
    "z fold 5": {"codename": "q5q", "model": "SM-F946B", "chipset": "SDM8G2"},
    "z fold 6": {"codename": "q6q", "model": "SM-F956B", "chipset": "SDM8G3"},
    
    # Galaxy Z Flip series
    "z flip": {"codename": "bloom", "model": "SM-F700F", "chipset": "SDM855+"},
    "z flip 3": {"codename": "b2q", "model": "SM-F711B", "chipset": "SDM888"},
    "z flip 4": {"codename": "b4q", "model": "SM-F721B", "chipset": "SDM8+G1"},
    "z flip 5": {"codename": "b5q", "model": "SM-F731B", "chipset": "SDM8G2"},
    "z flip 6": {"codename": "b6q", "model": "SM-F741B", "chipset": "SDM8G3"},
    
    # Galaxy A series (popular ones)
    "a51": {"codename": "a51", "model": "SM-A515F", "chipset": "Exynos 9611"},
    "a52": {"codename": "a52q", "model": "SM-A525F", "chipset": "SDM720G"},
    "a52s": {"codename": "a52sxq", "model": "SM-A528B", "chipset": "SDM778G"},
    "a53": {"codename": "a53x", "model": "SM-A536B", "chipset": "Exynos 1280"},
    "a54": {"codename": "a54x", "model": "SM-A546B", "chipset": "Exynos 1380"},
    "a55": {"codename": "a55x", "model": "SM-A556B", "chipset": "Exynos 1480"},
    
    "a71": {"codename": "a71", "model": "SM-A715F", "chipset": "SDM730"},
    "a72": {"codename": "a72q", "model": "SM-A725F", "chipset": "SDM720G"},
    "a73": {"codename": "a73x", "model": "SM-A736B", "chipset": "SDM778G+"},
    
    # Galaxy M series
    "m31": {"codename": "m31", "model": "SM-M315F", "chipset": "Exynos 9611"},
    "m51": {"codename": "m51", "model": "SM-M515F", "chipset": "SDM730"},
    
    # Galaxy Tab series
    "tab s7": {"codename": "gts7l", "model": "SM-T870", "chipset": "SDM865+"},
    "tab s7+": {"codename": "gts7xl", "model": "SM-T970", "chipset": "SDM865+"},
    "tab s7 plus": {"codename": "gts7xl", "model": "SM-T970", "chipset": "SDM865+"},
    "tab s8": {"codename": "gts8", "model": "SM-X700", "chipset": "SDM8G1"},
    "tab s8+": {"codename": "gts8p", "model": "SM-X800", "chipset": "SDM8G1"},
    "tab s8 plus": {"codename": "gts8p", "model": "SM-X800", "chipset": "SDM8G1"},
    "tab s8 ultra": {"codename": "gts8u", "model": "SM-X900", "chipset": "SDM8G1"},
    "tab s9": {"codename": "gts9", "model": "SM-X710", "chipset": "SDM8G2"},
    "tab s9+": {"codename": "gts9p", "model": "SM-X810", "chipset": "SDM8G2"},
    "tab s9 plus": {"codename": "gts9p", "model": "SM-X810", "chipset": "SDM8G2"},
    "tab s9 ultra": {"codename": "gts9u", "model": "SM-X910", "chipset": "SDM8G2"},
    
    # Others
    "xcover 5": {"codename": "xcover5", "model": "SM-G525F", "chipset": "Exynos 850"},
    "xcover 6 pro": {"codename": "xcover6pro", "model": "SM-G736B", "chipset": "SDM778G"},
    "xcover 7": {"codename": "xcover7", "model": "SM-G556B", "chipset": "Dimensity 6100+"},
}

def search_device(query: str):
    """Search for a device by query string."""
    query = query.lower().strip()
    
    # Direct match
    if query in DEVICE_DATABASE:
        return DEVICE_DATABASE[query]
    
    # Partial match
    matches = []
    for name, data in DEVICE_DATABASE.items():
        if query in name or name in query:
            matches.append((name, data))
    
    if len(matches) == 1:
        return matches[0][1]
    elif len(matches) > 1:
        return matches  # Return list of tuples for multiple matches
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message."""
    welcome_text = (
        "📱 *Samsung Device Codename Bot*\n\n"
        "Send me a Samsung device name and I'll tell you its:\n"
        "• Internal codename (tag)\n"
        "• Model number\n"
        "• Chipset\n\n"
        "*Examples:*\n"
        "`Note 10 Lite` → `r7`\n"
        "`S24 Ultra` → `e3q`\n"
        "`Z Fold 5` → `q5q`\n\n"
        "You can also use /list to browse all devices or /search to find specific ones."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = (
        "*Available Commands:*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/list - Browse device categories\n"
        "/search <device> - Search for a specific device\n"
        "/codename <tag> - Reverse lookup by codename\n\n"
        "*Tips:*\n"
        "• Just type a device name directly (e.g., 'Note 10+')\n"
        "• Works with or without 'Galaxy' prefix\n"
        "• Supports common abbreviations (e.g., '+' for 'Plus')"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def list_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show device categories."""
    keyboard = [
        [InlineKeyboardButton("📱 Galaxy S Series", callback_data='cat_s')],
        [InlineKeyboardButton("📝 Galaxy Note Series", callback_data='cat_note')],
        [InlineKeyboardButton("📂 Galaxy Z Fold", callback_data='cat_fold')],
        [InlineKeyboardButton("🔄 Galaxy Z Flip", callback_data='cat_flip')],
        [InlineKeyboardButton("⭐ Galaxy A Series", callback_data='cat_a')],
        [InlineKeyboardButton("📟 Galaxy Tab", callback_data='cat_tab')],
        [InlineKeyboardButton("🔍 Others", callback_data='cat_other')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a category:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    categories = {
        'cat_s': [k for k in DEVICE_DATABASE.keys() if k.startswith('s') and not k.startswith('sm-')],
        'cat_note': [k for k in DEVICE_DATABASE.keys() if 'note' in k],
        'cat_fold': [k for k in DEVICE_DATABASE.keys() if 'fold' in k],
        'cat_flip': [k for k in DEVICE_DATABASE.keys() if 'flip' in k],
        'cat_a': [k for k in DEVICE_DATABASE.keys() if k.startswith('a')],
        'cat_tab': [k for k in DEVICE_DATABASE.keys() if 'tab' in k],
        'cat_other': [k for k in DEVICE_DATABASE.keys() if k.startswith(('m', 'x', 'fold', 'z')) and 'flip' not in k and 'fold' not in k],
    }
    
    if query.data in categories:
        devices = categories[query.data]
        if not devices:
            await query.edit_message_text("No devices found in this category.")
            return
            
        text = "*Devices in this category:*\n\n"
        for device in sorted(devices):
            data = DEVICE_DATABASE[device]
            text += f"• *{device.title()}* → `{data['codename']}`\n"
        
        # Add back button
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='back_list')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'back_list':
        await list_devices(update, context)

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for a specific device."""
    if not context.args:
        await update.message.reply_text("Usage: /search <device name>\nExample: /search Note 10 Lite")
        return
    
    query = ' '.join(context.args)
    result = search_device(query)
    
    if result is None:
        await update.message.reply_text(f"❌ No device found matching '{query}'.\nTry /list to browse available devices.")
    elif isinstance(result, list):
        # Multiple matches
        text = f"🔍 *Multiple matches for '{query}':*\n\n"
        for name, data in result[:10]:  # Limit to 10
            text += f"• *{name.title()}* → `{data['codename']}`\n"
        if len(result) > 10:
            text += f"\n_...and {len(result) - 10} more_"
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        # Single match
        text = format_device_info(query, result)
        await update.message.reply_text(text, parse_mode='Markdown')

async def codename_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reverse lookup by codename."""
    if not context.args:
        await update.message.reply_text("Usage: /codename <tag>\nExample: /codename r7")
        return
    
    tag = context.args[0].lower().strip()
    matches = []
    
    for name, data in DEVICE_DATABASE.items():
        if data['codename'].lower() == tag:
            matches.append((name, data))
    
    if not matches:
        await update.message.reply_text(f"❌ No device found with codename '{tag}'.")
    else:
        text = f"🔖 *Devices with codename `{tag}`:*\n\n"
        for name, data in matches:
            text += format_device_info(name, data, header=False)
        await update.message.reply_text(text, parse_mode='Markdown')

def format_device_info(name: str, data: dict, header: bool = True) -> str:
    """Format device information."""
    if header:
        text = f"📱 *{name.title()}*\n\n"
    else:
        text = f"📱 *{name.title()}*\n"
    
    text += (
        f"🏷️ *Codename:* `{data['codename']}`\n"
        f"🔢 *Model:* `{data['model']}`\n"
        f"⚡ *Chipset:* {data['chipset']}\n\n"
    )
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct device name messages."""
    text = update.message.text
    
    # Remove common prefixes
    text = text.lower().replace('galaxy ', '').replace('samsung ', '').strip()
    
    result = search_device(text)
    
    if result is None:
        await update.message.reply_text(
            f"❌ I don't know '{update.message.text}' yet.\n\n"
            f"Try:\n"
            f"• /search {update.message.text}\n"
            f"• /list to browse categories\n"
            f"• /help for usage tips"
        )
    elif isinstance(result, list):
        # Multiple matches
        msg = f"🔍 *Did you mean one of these?*\n\n"
        for name, data in result[:5]:
            msg += f"• *{name.title()}* → `{data['codename']}`\n"
        msg += "\n_Send the exact name for full details._"
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        # Single match
        response = format_device_info(text, result)
        await update.message.reply_text(response, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("⚠️ An error occurred. Please try again.")

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("Error: Please set the TELEGRAM_BOT_TOKEN environment variable.")
        print("Example: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_devices))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("codename", codename_lookup))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
