import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import BOT_TOKEN
from bot_handlers import (
    start_command, cmds_command, cmd_command, id_command, allow_command, 
    disallow_command, list_allowed_command, check_card_command, stripe5_command, 
    stripe9_command, shopify_command, crunchyroll_command, bin_command, gen_command,  # ADDED stripe9_command
    gates_command, utility_command, button_handler, handle_messages, error_handler,
    caliper_command, authnet_command_wrapper
)
from paypal_client import paypal_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Main commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("cmds", cmds_command))
    application.add_handler(CommandHandler("cmd", cmd_command))
    application.add_handler(CommandHandler("id", id_command))
    
    # Owner-only commands
    application.add_handler(CommandHandler("allow", allow_command))
    application.add_handler(CommandHandler("disallow", disallow_command))
    application.add_handler(CommandHandler("listallowed", list_allowed_command))
    
    # Secondary commands
    application.add_handler(CommandHandler("gates", gates_command))
    application.add_handler(CommandHandler("utility", utility_command))
    application.add_handler(CommandHandler("chk", check_card_command))
    application.add_handler(CommandHandler("st5", stripe5_command))
    application.add_handler(CommandHandler("st9", stripe9_command))  # NEW COMMAND
    application.add_handler(CommandHandler("sh", shopify_command))
    application.add_handler(CommandHandler("au", authnet_command_wrapper))
    application.add_handler(CommandHandler("paypal", paypal_command))
    application.add_handler(CommandHandler("crunchy", crunchyroll_command))
    application.add_handler(CommandHandler("bin", bin_command))
    application.add_handler(CommandHandler("gen", gen_command))
    application.add_handler(CommandHandler("caliper", caliper_command))
    
    # Inline button handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Normal message handler (only in allowed chats)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    application.add_error_handler(error_handler)
    
    print("🤖 Bot started with Stripe $9 Gateway...")
    application.run_polling()

if __name__ == '__main__':
    main()