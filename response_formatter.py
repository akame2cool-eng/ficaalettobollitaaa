import json
import time

start_time = None

def start_timer():
    global start_time
    start_time = time.time()

def get_elapsed_time():
    global start_time
    if start_time is None:
        return "N/A"
    elapsed = time.time() - start_time
    return f"{elapsed:.2f} seconds"

def parse_api_message(api_data: dict) -> str:
    if not api_data:
        return "No API response"
    
    message = api_data.get('message')
    if message:
        return message
    
    response_str = api_data.get('response', '')
    if isinstance(response_str, str) and response_str.strip().startswith('{'):
        try:
            response_data = json.loads(response_str)
            return response_data.get('message', response_str)
        except:
            return response_str
    
    return str(api_data)

def format_api_response(card_info: dict, api_result: dict, bin_info: dict = None) -> str:
    if not api_result['success']:
        return f"""Declined ❌

Card: {card_info['number']}|{card_info['month']}|{card_info['year']}|{card_info['cvv']}
Gateway: {api_result.get('gateway', 'Stripe1').upper()}
Response: {api_result['error']}

Time: {get_elapsed_time()}"""
    
    api_data = api_result['data']
    api_message = parse_api_message(api_data)
    
    # Determine status
    message_lower = api_message.lower()
    
    if any(word in message_lower for word in ['approved', 'success', 'live', 'valid', 'charge_succeeded']):
        status_emoji = "✅"
        title = "Approved"
    elif any(word in message_lower for word in ['declined', 'declinata', 'failed', 'dead', 'charge_failed', 'payment_declined']):
        status_emoji = "❌"
        title = "Declined"
    elif any(word in message_lower for word in ['error', 'errore', 'invalid', 'non valida', 'incorrect']):
        status_emoji = "⚠️"
        title = "Error"
    else:
        status_emoji = "🔍"
        title = "Unknown"
    
    gateway_display = api_result.get('gateway', 'stripe1').upper()
    if gateway_display == 'STRIPE1':
        gateway_display = "STRIPE $1"
    elif gateway_display == 'STRIPE5':
        gateway_display = "STRIPE $5"
    elif gateway_display == 'SHOPIFY':
        gateway_display = "SHOPIFY $1"
    elif gateway_display == 'AUTHNET $32':
        gateway_display = "AUTHNET $1"
    
    response = f"""{title} {status_emoji}

Card: {card_info['number']}|{card_info['month']}|{card_info['year']}|{card_info['cvv']}
Gateway: {gateway_display}
Response: {api_message}"""

    # Add BIN info if available
    if bin_info and bin_info['success']:
        bin_data = bin_info['data']
        response += f"""

BIN Info:
Country: {bin_data.get('country', 'N/A')}
Issuer: {bin_data.get('issuer', 'N/A')}
Scheme: {bin_data.get('scheme', 'N/A')}
Type: {bin_data.get('type', 'N/A')}
Tier: {bin_data.get('tier', 'N/A')}"""
    
    response += f"""

Time: {get_elapsed_time()}"""
    
    return response

def format_crunchyroll_response(api_result: dict) -> str:
    if not api_result['success']:
        return f"""Crunchyroll Error ❌

Error: {api_result['error']}

Time: {get_elapsed_time()}"""
    
    api_data = api_result['data']
    api_message = parse_api_message(api_data)
    
    return f"""Crunchyroll Check ✅

Response: {api_message}

Time: {get_elapsed_time()}"""

def format_bin_response(bin_result: dict) -> str:
    if not bin_result['success']:
        return f"""BIN Error ❌

Error: {bin_result['error']}"""
    
    bin_data = bin_result['data']
    
    return f"""BIN Information ✅

BIN: {bin_data.get('bin', 'N/A')}
Country: {bin_data.get('country', 'N/A')}
Issuer: {bin_data.get('issuer', 'N/A')}
Scheme: {bin_data.get('scheme', 'N/A')}
Type: {bin_data.get('type', 'N/A')}
Tier: {bin_data.get('tier', 'N/A')}
Status: {bin_data.get('status', 'N/A')}"""

def format_gen_response(gen_result: dict) -> str:
    if not gen_result['success']:
        return f"""Generator Error ❌

Error: {gen_result['error']}"""
    
    cards = gen_result['data']
    cards_text = "\n".join(cards[:10])  # Max 10 cards
    
    return f"""Cards Generated ✅

{cards_text}

Total: {len(cards)} cards"""

def format_error_message(error_type: str, details: str = "") -> str:
    error_templates = {
        'invalid_format': f"""Invalid Format ❌

{details}

Supported Formats:
number|month|year|cvv
number month year cvv
number/month/year/cvv

Example:
/chk 4147768578745265|04|2026|168""",
        'api_error': f"""API Error ❌

{details}

Try again in a few minutes""",
        'invalid_bin': f"""Invalid BIN ❌

{details}

BIN must be at least 6 digits""",
        'invalid_credentials': f"""Invalid Credentials ❌

{details}

Format: email:password
Example: /crunchy user@example.com:password123"""
    }
    

    return error_templates.get(error_type, f"Error: {details}")
