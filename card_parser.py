import re

def parse_card_input(input_text: str) -> dict:
    if not input_text:
        return {'valid': False, 'error': 'Empty input'}
    
    normalized = re.sub(r'[\s/]', '|', input_text.strip())
    parts = normalized.split('|')
    parts = [part for part in parts if part]
    
    if len(parts) != 4:
        return {'valid': False, 'error': 'Invalid format. Use: number|month|year|cvv'}
    
    number, month, year, cvv = parts
    
    if not number.isdigit() or len(number) < 13:
        return {'valid': False, 'error': 'Invalid card number'}
    
    if not month.isdigit() or not (1 <= int(month) <= 12):
        return {'valid': False, 'error': 'Invalid month (1-12)'}
    
    if not year.isdigit() or len(year) != 4:
        return {'valid': False, 'error': 'Invalid year (format: YYYY)'}
    
    if not cvv.isdigit() or len(cvv) not in [3, 4]:
        return {'valid': False, 'error': 'Invalid CVV (3-4 digits)'}
    
    return {
        'valid': True,
        'card_data': f"{number}|{month}|{year}|{cvv}",
        'number': number,
        'month': month,
        'year': year,
        'cvv': cvv
    }

def format_card_display(card_info: dict) -> str:
    number = card_info.get('number', '')
    masked_number = f"{number[:6]}******{number[-4:]}" if len(number) >= 16 else number
    return f"💳 {masked_number} | {card_info.get('month', '')}/{card_info.get('year', '')}"