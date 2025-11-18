import time
import logging
from config import COOLDOWN_SECONDS, OWNER_USER_ID, ALLOWED_CHAT_IDS

logger = logging.getLogger(__name__)

# Dictionary to track last command usage for each user
user_cooldowns = {}

def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    return user_id == OWNER_USER_ID

def is_allowed_chat(chat_id: int, chat_type: str, user_id: int = None) -> bool:
    """
    Check if chat is allowed
    - Owner can use anywhere
    - Everyone can use in allowed chats
    """
    # Owner can use anywhere (use user_id for owner check)
    if user_id and is_owner(user_id):
        return True
    
    # Chat in allowed list
    if chat_id in ALLOWED_CHAT_IDS:
        return True
    
    # In DM, only owner
    if chat_type == "private":
        return user_id and is_owner(user_id)
    
    return False

def add_allowed_chat(chat_id: int) -> bool:
    """
    Add chat to allowed list
    Returns True if added, False if already present
    """
    if chat_id not in ALLOWED_CHAT_IDS:
        ALLOWED_CHAT_IDS.append(chat_id)
        logger.info(f"Chat {chat_id} added to allowed list")
        return True
    return False

def remove_allowed_chat(chat_id: int) -> bool:
    """
    Remove chat from allowed list
    Returns True if removed, False if not present
    """
    if chat_id in ALLOWED_CHAT_IDS:
        ALLOWED_CHAT_IDS.remove(chat_id)
        logger.info(f"Chat {chat_id} removed from allowed list")
        return True
    return False

def get_allowed_chats() -> list:
    """Return list of allowed chats"""
    return ALLOWED_CHAT_IDS.copy()

def can_use_command(user_id: int, command: str) -> tuple:
    """
    Check if user can use command
    Returns (True, "") if can, (False, error_message) if cannot
    """
    # Owner can always use commands without cooldown
    if is_owner(user_id):
        return True, ""
    
    # Check if it's a card check command
    card_commands = ['chk', 'st5', 'sh', 'au', 'pp', 'caliper', 's1']  # AGGIUNTO 's1'
    if command in card_commands:
        current_time = time.time()
        last_used = user_cooldowns.get(user_id)
        
        if last_used and (current_time - last_used) < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - (current_time - last_used)
            return False, f"⏰ Please wait {remaining:.1f} seconds before using another card check command."
        
        # Update cooldown
        user_cooldowns[user_id] = current_time
        return True, ""
    
    # For other commands (bin, gen, crunchy) no cooldown
    return True, ""

def get_cooldown_status(user_id: int) -> str:
    """Return cooldown status for user"""
    if is_owner(user_id):
        return "🛡️ Owner - No cooldown"
    
    last_used = user_cooldowns.get(user_id)
    if not last_used:
        return "✅ Ready to use"
    
    current_time = time.time()
    elapsed = current_time - last_used
    
    if elapsed < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - elapsed
        return f"⏰ Cooldown: {remaining:.1f}s remaining"
    else:
        return "✅ Ready to use"

def get_chat_permissions(chat_id: int, chat_type: str, user_id: int = None) -> str:
    """Return chat permissions info"""
    if user_id and is_owner(user_id):
        return "🛡️ Owner access"
    elif chat_id in ALLOWED_CHAT_IDS:
        return "✅ Allowed chat"
    elif chat_type == "private":
        return "❌ Private chat not allowed"
    else:
        return "❌ Chat not allowed"
