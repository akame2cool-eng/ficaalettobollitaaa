import re
import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)

class Stripe9Tester:
    def __init__(self, headless=True, proxy_url=None):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.proxy_url = proxy_url
    
    def setup_driver(self):
        """Initialize selenium driver"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Proxy configuration
            if self.proxy_url:
                chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("✅ Driver initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Driver initialization error: {e}")
            return False

    def generate_usa_info(self):
        """Generate USA information for Florida"""
        first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
        streets = ['Main St', 'Oak Ave', 'Park Rd', 'Maple Dr', 'Cedar Ln']
        cities = ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale']
        
        return {
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f"test{random.randint(1000,9999)}@gmail.com",
            'phone': f"305{random.randint(100,999)}{random.randint(1000,9999)}",
            'address': f"{random.randint(100, 9999)} {random.choice(streets)}",
            'city': random.choice(cities),
            'state': 'FL',
            'postal_code': f"{random.randint(33000, 34999)}",
            'name_on_card': 'TEST CARD'
        }
    
    def add_to_cart(self):
        """Add product to cart"""
        logger.info("🛒 Adding product to cart...")
        
        try:
            self.driver.get("https://asiangarden2table.com/product/cucumber-jin5/")
            time.sleep(4)
            
            # Find and click Add to Cart button
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
                    logger.info(f"✅ Found button: {selector}")
                    break
                except:
                    continue
            
            if not add_button:
                logger.error("❌ Add to Cart button not found")
                return False
            
            self.driver.execute_script("arguments[0].click();", add_button)
            logger.info("✅ Product added to cart")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding to cart: {e}")
            return False
    
    def go_to_cart_and_checkout(self):
        """Go to cart and click checkout"""
        try:
            logger.info("🛒 Going to cart...")
            
            self.driver.get("https://asiangarden2table.com/cart/")
            time.sleep(4)
            
            # Find Proceed to Checkout button
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
                    logger.info(f"✅ Found checkout: {selector}")
                    break
                except:
                    continue
            
            if not checkout_button:
                logger.error("❌ Checkout button not found")
                return False
            
            self.driver.execute_script("arguments[0].click();", checkout_button)
            logger.info("✅ Checkout clicked")
            
            time.sleep(5)
            return True
                
        except Exception as e:
            logger.error(f"❌ Error during checkout: {e}")
            return False
    
    def fill_billing_info(self, info):
        """Fill billing information"""
        logger.info("📦 Filling billing information...")
        
        try:
            time.sleep(4)
            
            # FIRST NAME
            first_name_selectors = ["#billing_first_name", "#billing-first_name", "input[name='billing_first_name']"]
            for selector in first_name_selectors:
                try:
                    first_name_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    first_name_field.clear()
                    first_name_field.send_keys(info['first_name'])
                    logger.info(f"✅ First Name: {info['first_name']}")
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
                    logger.info(f"✅ Last Name: {info['last_name']}")
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
                    logger.info(f"✅ Address: {info['address']}")
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
                    logger.info(f"✅ City: {info['city']}")
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
                    logger.info("✅ State: Florida")
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
                    logger.info(f"✅ ZIP Code: {info['postal_code']}")
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
                    logger.info(f"✅ Phone: {info['phone']}")
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
                    logger.info(f"✅ Email: {info['email']}")
                    break
                except:
                    continue
            
            logger.info("✅ Billing information filled")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error filling billing info: {e}")
            return False

    def fill_credit_card_info(self, card_data):
        """Fill credit card fields in Stripe iframe"""
        logger.info("💳 Filling credit card data...")
        
        try:
            # Find Stripe iframe
            stripe_iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title*='Secure payment input frame']")))
            logger.info("✅ Found Stripe iframe")
            
            # Switch to iframe
            self.driver.switch_to.frame(stripe_iframe)
            logger.info("✅ Switched to Stripe iframe")
            
            time.sleep(2)
            
            # CARD NUMBER
            card_number_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='number']")))
            card_number_field.clear()
            card_number_field.send_keys(card_data['number'])
            logger.info(f"✅ Card number filled: {card_data['number'][:6]}******{card_data['number'][-4:]}")
            
            # EXPIRY
            expiry_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='expiry']")
            expiry_field.clear()
            expiry = f"{card_data['month']}{card_data['year'][-2:]}"  # MMYY
            expiry_field.send_keys(expiry)
            logger.info(f"✅ Expiry filled: {card_data['month']}/{card_data['year'][-2:]}")
            
            # CVV
            cvv_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='cvc']")
            cvv_field.clear()
            cvv_field.send_keys(card_data['cvv'])
            logger.info(f"✅ CVV filled: {card_data['cvv']}")
            
            # Return to main content
            self.driver.switch_to.default_content()
            logger.info("✅ Returned to main content")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error filling card: {e}")
            self.driver.switch_to.default_content()
            return False

    def place_order(self):
        """Click Place Order button"""
        logger.info("🚀 Attempting to complete order...")
        
        try:
            # Find Place Order button
            place_order_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#place_order")))
            logger.info("✅ Found Place Order button")
            
            # Click button
            self.driver.execute_script("arguments[0].click();", place_order_button)
            logger.info("✅ Place Order button clicked")
            
            # Wait longer for processing
            time.sleep(12)
            
            # Analyze result
            current_url = self.driver.current_url
            page_text = self.driver.page_source.lower()
            page_html = self.driver.page_source
            
            logger.info(f"📄 Final URL: {current_url}")
            
            # CHECK FOR SUCCESS FIRST - Most important indicators
            if 'order-received' in current_url or 'thank-you' in current_url:
                logger.info("✅ SUCCESS: Order received page")
                return "APPROVED", "Payment successful - Order completed"
            
            # Check for success messages in page content
            success_indicators = [
                'order complete', 'order confirmed', 'order placed',
                'your order has been received', 'order number', 'order details',
                'payment successful', 'transaction complete', 'thank you for your order'
            ]
            
            for indicator in success_indicators:
                if indicator in page_text:
                    logger.info(f"✅ SUCCESS INDICATOR: '{indicator}'")
                    return "APPROVED", f"Payment successful - {indicator.title()}"
            
            # CHECK FOR DECLINED - Look for specific error messages
            declined_patterns = [
                (r'your card was declined', 'Card declined'),
                (r'this transaction has been declined', 'Transaction declined'),
                (r'card declined', 'Card declined'),
                (r'the credit card number is invalid', 'Invalid card number'),
                (r'the card has expired', 'Card expired'),
                (r'the cvv number is invalid', 'Invalid CVV'),
                (r'insufficient funds', 'Insufficient funds'),
                (r'do not honor', 'Do not honor'),
                (r'transaction not allowed', 'Transaction not allowed'),
                (r'payment failed', 'Payment failed'),
                (r'declined', 'Declined'),
                (r'error processing payment', 'Payment processing error'),
                (r'invalid payment method', 'Invalid payment method'),
                (r'bank declined', 'Bank declined'),
                (r'processor declined', 'Processor declined'),
                (r'security code is incorrect', 'Incorrect CVV'),
                (r'zip code does not match', 'Zip code mismatch')
            ]
            
            for pattern, message in declined_patterns:
                if re.search(pattern, page_text, re.IGNORECASE):
                    logger.info(f"🔴 DECLINED: '{message}'")
                    return "DECLINED", message
            
            # Check for error messages in specific elements
            error_containers = [
                ".woocommerce-error",
                ".payment-error",
                ".stripe-error",
                ".gateway-error",
                "[class*='error']",
                "[class*='declin']",
                "div[role='alert']",
                ".alert",
                ".notice-error"
            ]
            
            for container in error_containers:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, container)
                    for element in elements:
                        if element.is_displayed():
                            error_text = element.text.strip()
                            if error_text and len(error_text) > 10:
                                # Check if it's actually an error, not just generic text
                                if any(word in error_text.lower() for word in ['declined', 'error', 'invalid', 'failed', 'cannot']):
                                    logger.info(f"🔴 ERROR IN CONTAINER: '{error_text}'")
                                    return "DECLINED", error_text[:100]  # Limit length
                except:
                    continue
            
            # CHECK FOR 3DS/PROCESSING - Only if no success/declined found
            processing_indicators = [
                '3d secure', '3ds', 'processing', 'verifying', 'authenticating',
                'redirect', 'challenge', 'secure verification', 'additional authentication'
            ]
            
            for indicator in processing_indicators:
                if indicator in page_text:
                    logger.info(f"🔄 PROCESSING: '{indicator}'")
                    return "PROCESSING", f"3DS Authentication Required - {indicator.title()}"
            
            # Final check - if still on checkout page with no errors, it might be processing
            if "checkout" in current_url or "cart" in current_url:
                # Check if there are any validation errors
                if any(word in page_text for word in ['required', 'invalid', 'missing']):
                    return "DECLINED", "Form validation error"
                else:
                    return "PROCESSING", "Payment processing - Check manually"
            
            # If we're not on checkout/cart and no success found, assume declined
            return "DECLINED", "Payment failed - No success confirmation"
                
        except Exception as e:
            logger.error(f"❌ Error during place order: {e}")
            return "ERROR", str(e)

    def run_test(self, card_number, expiry_month, expiry_year, cvv):
        """Run complete test"""
        logger.info("🧪 STARTING STRIPE $9 TEST")
        
        try:
            if not self.setup_driver():
                return "ERROR_DRIVER_INIT", "Driver initialization failed"
            
            usa_info = self.generate_usa_info()
            card_data = {
                'number': card_number,
                'month': expiry_month,
                'year': expiry_year,
                'cvv': cvv
            }
            
            logger.info(f"👤 Test info: {usa_info['first_name']} {usa_info['last_name']}")
            logger.info(f"💳 Card: {card_data['number'][:6]}******{card_data['number'][-4:]}")
            
            # TEST STEPS
            logger.info("\n1️⃣ ADD TO CART")
            if not self.add_to_cart():
                return "ERROR_ADD_TO_CART", "Failed to add product to cart"
            
            logger.info("\n2️⃣ CHECKOUT")
            if not self.go_to_cart_and_checkout():
                return "ERROR_CHECKOUT", "Failed to proceed to checkout"
            
            logger.info("\n3️⃣ FILL BILLING INFO") 
            if not self.fill_billing_info(usa_info):
                return "ERROR_BILLING_INFO", "Failed to fill billing information"
            
            logger.info("\n4️⃣ FILL CREDIT CARD INFO")
            if not self.fill_credit_card_info(card_data):
                return "ERROR_CREDIT_CARD", "Failed to fill credit card information"
            
            logger.info("\n5️⃣ COMPLETE ORDER")
            status, message = self.place_order()
            
            return status, message
            
        except Exception as e:
            logger.error(f"💥 Error during test: {e}")
            return "ERROR", str(e)
        finally:
            if self.driver:
                self.driver.quit()

def run_stripe9_check(card_number, month, year, cvv, proxy_url=None):
    """
    Execute payment test on Stripe $9 Gateway
    Returns: (status, message)
    """
    tester = Stripe9Tester(headless=True, proxy_url=proxy_url)
    return tester.run_test(card_number, month, year, cvv)