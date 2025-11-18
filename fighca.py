from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import random
import time

class AsianGardenTester:
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.headless = headless
    
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
            
            # USER AGENT
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            print("✅ Driver inizializzato")
            return True
        except Exception as e:
            print(f"❌ Errore inizializzazione driver: {e}")
            return False

    def generate_usa_info(self):
        """Genera informazioni USA per Florida"""
        first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
        streets = ['Main St', 'Oak Ave', 'Park Rd', 'Maple Dr', 'Cedar Ln']
        cities = ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale']
        
        return {
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f"test{random.randint(1000,9999)}@gmail.com",  # Cambiato a gmail.com
            'phone': f"305{random.randint(100,999)}{random.randint(1000,9999)}",
            'address': f"{random.randint(100, 9999)} {random.choice(streets)}",
            'city': random.choice(cities),
            'state': 'FL',
            'postal_code': f"{random.randint(33000, 34999)}",
            'name_on_card': 'TEST CARD'
        }
    
    def analyze_page_structure(self):
        """Analizza la struttura della pagina per debugging"""
        print("\n🔍 ANALISI STRUTTURA PAGINA:")
        
        try:
            # Analizza checkout page
            current_url = self.driver.current_url
            print(f"📄 URL: {current_url}")
            
            # Cerca tutti i campi di input
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"📝 Input fields trovati: {len(inputs)}")
            
            for inp in inputs[:10]:  # Mostra primi 10
                field_id = inp.get_attribute('id') or inp.get_attribute('name') or inp.get_attribute('class')
                field_type = inp.get_attribute('type')
                placeholder = inp.get_attribute('placeholder')
                print(f"   - {field_type}: {field_id} | Placeholder: {placeholder}")
            
            # Cerca iframe (per Stripe)
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"🖼️  Iframes trovati: {len(iframes)}")
            
            for iframe in iframes[:5]:  # Mostra primi 5
                title = iframe.get_attribute('title')
                print(f"   - Iframe title: {title}")
            
            # Cerca bottoni
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"🔘 Bottoni trovati: {len(buttons)}")
            
            for btn in buttons[:5]:
                btn_text = btn.text.strip()
                btn_class = btn.get_attribute('class')
                if btn_text:
                    print(f"   - Bottone: '{btn_text}' | Class: {btn_class}")
            
        except Exception as e:
            print(f"❌ Errore analisi: {e}")

    def add_to_cart(self):
        """Aggiunge il prodotto al carrello"""
        print("🛒 Aggiunta prodotto Asian Garden...")
        
        try:
            self.driver.get("https://asiangarden2table.com/product/cucumber-jin5/")
            time.sleep(4)
            
            # ANALIZZA LA PAGINA PRODOTTO
            print("🔍 Analisi pagina prodotto...")
            self.analyze_page_structure()
            
            # Cerca e clicca il bottone Add to Cart
            add_button_selectors = [
                "button.single_add_to_cart_button",
                "button[name='add-to-cart']",
                ".add_to_cart_button", 
                "button[type='submit']",
                "input[type='submit']",
                ".single_add_to_cart_button"
            ]
            
            add_button = None
            for selector in add_button_selectors:
                try:
                    add_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Trovato bottone: {selector}")
                    print(f"   Testo: {add_button.text}")
                    break
                except:
                    continue
            
            if not add_button:
                print("❌ Bottone Add to Cart non trovato")
                return False
            
            self.driver.execute_script("arguments[0].click();", add_button)
            print("✅ Prodotto aggiunto al carrello")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ Errore aggiunta carrello: {e}")
            return False
    
    def go_to_cart_and_checkout(self):
        """Va al carrello e clicca checkout"""
        try:
            print("🛒 Andando al carrello...")
            
            self.driver.get("https://asiangarden2table.com/cart/")
            time.sleep(4)
            
            # ANALIZZA LA PAGINA CARRELLO
            print("🔍 Analisi pagina carrello...")
            self.analyze_page_structure()
            
            # Cerca il bottone Proceed to Checkout
            checkout_selectors = [
                "a.checkout-button",
                ".checkout-button", 
                "a[href*='checkout']",
                "button[value*='checkout']",
                "input[value*='checkout']",
                ".wc-forward"
            ]
            
            checkout_button = None
            for selector in checkout_selectors:
                try:
                    checkout_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Trovato checkout: {selector}")
                    print(f"   Testo: {checkout_button.text}")
                    break
                except:
                    continue
            
            if not checkout_button:
                print("❌ Bottone checkout non trovato")
                return False
            
            self.driver.execute_script("arguments[0].click();", checkout_button)
            print("✅ Checkout cliccato")
            
            time.sleep(5)
            return True
                
        except Exception as e:
            print(f"❌ Errore checkout: {e}")
            return False
    
    def fill_billing_info(self, info):
        """Compila informazioni di fatturazione"""
        print("📦 Compilazione informazioni fatturazione...")
        
        try:
            time.sleep(4)
            
            # ANALIZZA LA PAGINA CHECKOUT
            print("🔍 Analisi pagina checkout...")
            self.analyze_page_structure()
            
            # FIRST NAME
            first_name_selectors = ["#billing_first_name", "#billing-first_name", "input[name='billing_first_name']"]
            for selector in first_name_selectors:
                try:
                    first_name_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    first_name_field.clear()
                    first_name_field.send_keys(info['first_name'])
                    print(f"✅ First Name: {info['first_name']}")
                    break
                except:
                    continue
            
            # LAST NAME  
            last_name_selectors = ["#billing_last_name", "#billing-last_name", "input[name='billing_last_name']"]
            for selector in last_name_selectors:
                try:
                    last_name_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    last_name_field.clear()
                    last_name_field.send_keys(info['last_name'])
                    print(f"✅ Last Name: {info['last_name']}")
                    break
                except:
                    continue
            
            # STREET ADDRESS
            address_selectors = ["#billing_address_1", "input[name='billing_address_1']"]
            for selector in address_selectors:
                try:
                    address_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    address_field.clear()
                    address_field.send_keys(info['address'])
                    print(f"✅ Address: {info['address']}")
                    break
                except:
                    continue
            
            # TOWN/CITY
            city_selectors = ["#billing_city", "input[name='billing_city']"]
            for selector in city_selectors:
                try:
                    city_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    city_field.clear()
                    city_field.send_keys(info['city'])
                    print(f"✅ City: {info['city']}")
                    break
                except:
                    continue
            
            # STATE (Florida)
            state_selectors = ["#billing_state", "select[name='billing_state']"]
            for selector in state_selectors:
                try:
                    state_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    select = Select(state_field)
                    select.select_by_value('FL')
                    print("✅ State: Florida")
                    break
                except:
                    continue
            
            # ZIP CODE
            zip_selectors = ["#billing_postcode", "input[name='billing_postcode']"]
            for selector in zip_selectors:
                try:
                    zip_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    zip_field.clear()
                    zip_field.send_keys(info['postal_code'])
                    print(f"✅ ZIP Code: {info['postal_code']}")
                    break
                except:
                    continue
            
            # PHONE
            phone_selectors = ["#billing_phone", "input[name='billing_phone']"]
            for selector in phone_selectors:
                try:
                    phone_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    phone_field.clear()
                    phone_field.send_keys(info['phone'])
                    print(f"✅ Phone: {info['phone']}")
                    break
                except:
                    continue
            
            # EMAIL ADDRESS
            email_selectors = ["#billing_email", "input[name='billing_email']"]
            for selector in email_selectors:
                try:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    email_field.clear()
                    email_field.send_keys(info['email'])
                    print(f"✅ Email: {info['email']}")
                    break
                except:
                    continue
            
            print("✅ Informazioni fatturazione compilate")
            return True
            
        except Exception as e:
            print(f"❌ Errore compilazione fatturazione: {e}")
            return False

    def fill_credit_card_info(self, card_data):
        """Compila i campi della carta di credito nell'iframe Stripe"""
        print("💳 Compilazione dati carta di credito...")
        
        try:
            # Trova l'iframe dei campi della carta
            stripe_iframe_selectors = [
                "iframe[title*='Secure payment input frame']",
                "iframe[title*='payment input']",
                "iframe[name*='StripeFrame']"
            ]
            
            stripe_iframe = None
            for selector in stripe_iframe_selectors:
                try:
                    stripe_iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ Trovato iframe Stripe: {selector}")
                    break
                except:
                    continue
            
            if not stripe_iframe:
                print("❌ Iframe Stripe non trovato")
                return False
            
            # Switcha nell'iframe
            self.driver.switch_to.frame(stripe_iframe)
            print("✅ Switchato nell'iframe Stripe")
            
            # Trova e compila il campo numero carta
            card_number_selectors = [
                "input[name='number']",
                "input[placeholder*='1234']",
                "input[data-elements-stable-field-name='cardNumber']"
            ]
            
            card_number_field = None
            for selector in card_number_selectors:
                try:
                    card_number_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ Trovato campo numero carta: {selector}")
                    break
                except:
                    continue
            
            if card_number_field:
                card_number_field.clear()
                card_number_field.send_keys(card_data['number'])
                print(f"✅ Numero carta inserito: {card_data['number'][:6]}******{card_data['number'][-4:]}")
            else:
                print("❌ Campo numero carta non trovato")
                self.driver.switch_to.default_content()
                return False
            
            # Trova e compila il campo scadenza
            expiry_selectors = [
                "input[name='expiry']",
                "input[placeholder*='MM / YY']",
                "input[data-elements-stable-field-name='cardExpiry']"
            ]
            
            expiry_field = None
            for selector in expiry_selectors:
                try:
                    expiry_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Trovato campo scadenza: {selector}")
                    break
                except:
                    continue
            
            if expiry_field:
                expiry_field.clear()
                expiry = f"{card_data['month']}{card_data['year'][-2:]}"  # Formato MMYY
                expiry_field.send_keys(expiry)
                print(f"✅ Scadenza inserita: {card_data['month']}/{card_data['year'][-2:]}")
            else:
                print("❌ Campo scadenza non trovato")
                self.driver.switch_to.default_content()
                return False
            
            # Trova e compila il campo CVV
            cvv_selectors = [
                "input[name='cvc']",
                "input[placeholder*='CVC']",
                "input[data-elements-stable-field-name='cardCvc']"
            ]
            
            cvv_field = None
            for selector in cvv_selectors:
                try:
                    cvv_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Trovato campo CVV: {selector}")
                    break
                except:
                    continue
            
            if cvv_field:
                cvv_field.clear()
                cvv_field.send_keys(card_data['cvv'])
                print(f"✅ CVV inserito: {card_data['cvv']}")
            else:
                print("❌ Campo CVV non trovato")
                self.driver.switch_to.default_content()
                return False
            
            # Ritorna al contenuto principale
            self.driver.switch_to.default_content()
            print("✅ Ritornato al contenuto principale")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore compilazione carta: {e}")
            self.driver.switch_to.default_content()
            return False

    def place_order(self):
        """Clicca sul bottone Place Order"""
        print("🚀 Tentativo di completare l'ordine...")
        
        try:
            # Cerca il bottone Place Order
            place_order_selectors = [
                "button#place_order",
                "button[name='woocommerce_checkout_place_order']",
                "input[type='submit'][value*='Place order']",
                ".button.alt",
                "button[value*='Place order']"
            ]
            
            place_order_button = None
            for selector in place_order_selectors:
                try:
                    place_order_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Trovato bottone Place Order: {selector}")
                    print(f"   Testo: {place_order_button.text}")
                    break
                except:
                    continue
            
            if not place_order_button:
                print("❌ Bottone Place Order non trovato")
                return False
            
            # Scroll per rendere visibile il bottone
            self.driver.execute_script("arguments[0].scrollIntoView(true);", place_order_button)
            time.sleep(2)
            
            # Clicca il bottone
            self.driver.execute_script("arguments[0].click();", place_order_button)
            print("✅ Bottone Place Order cliccato")
            
            # Aspetta la risposta
            time.sleep(10)
            
            # Controlla se l'ordine è andato a buon fine
            current_url = self.driver.current_url
            if 'order-received' in current_url or 'thank-you' in current_url:
                print("🎉 ORDINE COMPLETATO CON SUCCESSO!")
                return True
            else:
                print("⚠️  Possibile errore nell'ordine")
                return False
                
        except Exception as e:
            print(f"❌ Errore durante il place order: {e}")
            return False

    def run_test(self, card_number, expiry_month, expiry_year, cvv):
        """Esegue il test completo"""
        print("🧪 AVVIO TEST ASIAN GARDEN $6")
        print("=" * 50)
        
        try:
            if not self.setup_driver():
                return "ERROR_DRIVER_INIT"
            
            usa_info = self.generate_usa_info()
            card_data = {
                'number': card_number,
                'month': expiry_month,
                'year': expiry_year,
                'cvv': cvv
            }
            
            print(f"👤 Informazioni test:")
            print(f"   Nome: {usa_info['first_name']} {usa_info['last_name']}")
            print(f"   Email: {usa_info['email']}")
            print(f"   Indirizzo: {usa_info['address']}, {usa_info['city']}, FL {usa_info['postal_code']}")
            print(f"💳 Carta: {card_data['number'][:6]}******{card_data['number'][-4:]}")
            print(f"   Scadenza: {card_data['month']}/{card_data['year']}")
            print(f"   CVV: {card_data['cvv']}")
            print("=" * 50)
            
            # TEST STEP BY STEP
            print("\n1️⃣ AGGIUNTA AL CARRELLO")
            if not self.add_to_cart():
                return "ERROR_ADD_TO_CART"
            
            print("\n2️⃣ CHECKOUT")
            if not self.go_to_cart_and_checkout():
                return "ERROR_CHECKOUT"
            
            print("\n3️⃣ COMPILAZIONE FATTURAZIONE") 
            if not self.fill_billing_info(usa_info):
                return "ERROR_BILLING_INFO"
            
            print("\n4️⃣ COMPILAZIONE CARTA DI CREDITO")
            if not self.fill_credit_card_info(card_data):
                return "ERROR_CREDIT_CARD"
            
            print("\n5️⃣ COMPLETAMENTO ORDINE")
            if not self.place_order():
                return "ERROR_PLACE_ORDER"
            
            print("\n✅ TEST COMPLETATO CON SUCCESSO!")
            time.sleep(5)
            
            return "ORDER_SUCCESS"
            
        except Exception as e:
            print(f"💥 Errore durante il test: {e}")
            return f"ERROR - {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Funzione principale per test"""
    print("🔧 TESTER ASIAN GARDEN $6")
    print("💳 Utilizza una carta di test")
    print("=" * 50)
    
    # Dati di test
    card_number = input("Inserisci numero carta (o premi INVIO per usare 4111111111111111): ").strip()
    if not card_number:
        card_number = "4111111111111111"
    
    expiry_month = input("Mese scadenza (MM): ").strip() or "12"
    expiry_year = input("Anno scadenza (YYYY): ").strip() or "2028" 
    cvv = input("CVV: ").strip() or "123"
    
    print("\n" + "=" * 50)
    
    # Esegui test
    tester = AsianGardenTester(headless=False)
    result = tester.run_test(card_number, expiry_month, expiry_year, cvv)
    
    print(f"\n📊 RISULTATO: {result}")
    print("=" * 50)

if __name__ == "__main__":
    main()