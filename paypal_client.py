import requests
from telegram import Update
from telegram.ext import ContextTypes

# Configurazione API
PAYPAL_API_URL = "http://192.168.1.52:5001/api/paypal/check"  # Cambia con il tuo server

async def paypal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with PayPal API"""
    from security import is_allowed_chat, get_chat_permissions, can_use_command
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    # Verifica sicurezza chat
    if not is_allowed_chat(chat_id, chat_type, user_id):
        permission_info = get_chat_permissions(chat_id, chat_type, user_id)
        await update.message.reply_text(f"❌ {permission_info}")
        return
    
    # Verifica cooldown
    can_use, error_msg = can_use_command(user_id, 'paypal')
    if not can_use:
        await update.message.reply_text(error_msg)
        return
    
    if not context.args:
        await update.message.reply_text(
            "🔧 **PayPal Check**\n\n"
            "Usage: /paypal number|month|year|cvv\n\n"
            "Example: /paypal 424224242424242|10|2029|701"
        )
        return
    
    card_input = ' '.join(context.args)
    wait_message = await update.message.reply_text("🔄 Checking card with PayPal...")
    
    try:
        # Invia richiesta all'API
        response = requests.post(PAYPAL_API_URL, json={"card": card_input}, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                response_text = f"""
✅ **PayPal Check - APPROVED**

💳 Card: `{card_input}`
🔄 Status: {result["message"]}
🔒 Gateway: PayPal 1$ Charge
📝 Response: {result.get("details", "Success")}
"""
            else:
                response_text = f"""
❌ **PayPal Check - DECLINED**

💳 Card: `{card_input}`
🔄 Status: {result["message"]}
🔒 Gateway: PayPal 1$ Charge
📝 Details: {result.get("details", "No additional details")}
"""
        else:
            response_text = f"❌ API Error: {response.status_code}"
        
        await wait_message.edit_text(response_text)
        
    except requests.exceptions.Timeout:
        await wait_message.edit_text("❌ Timeout - API server not responding")
    except requests.exceptions.ConnectionError:
        await wait_message.edit_text("❌ Connection Error - Cannot reach API server")
    except Exception as e:
        await wait_message.edit_text(f"❌ Error: {str(e)}")