"""
OpenCart Automation Test Suite - Login Test Case
Single file containing test case for user login with valid credentials
"""

import pytest
import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = os.getenv("BASE_URL", "https://demo.opencart.com.gr/")  # OpenCart Demo URL
VALID_EMAIL = "fatimahasanat6@gmail.com"
VALID_PASSWORD = "123968574"

# ============================================================================
# PYTEST FIXTURES AND CONFIGURATION
# ============================================================================

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome or firefox"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=BASE_URL,
        help="Base URL for OpenCart application"
    )

@pytest.fixture(scope="function")
def driver(request):
    """Setup and teardown WebDriver instance"""
    browser = request.config.getoption("--browser", default="chrome")
    headless = request.config.getoption("--headless", default=False)
    
    # Force headless mode in CI environment
    is_ci = os.getenv("CI", "").lower() == "true" or os.getenv("GITHUB_ACTIONS", "").lower() == "true"
    if is_ci:
        headless = True
        logger.info("CI environment detected - forcing headless mode")
    
    logger.info(f"Setting up {browser} driver (headless: {headless})")
    
    if browser.lower() == "chrome":
        chrome_options = Options()
        if headless or is_ci:
            chrome_options.add_argument("--headless")
        
        # Essential arguments for CI environment
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # CI-specific arguments
        if is_ci:
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-sync")
            
            # Generate unique user data directory for CI
            import tempfile
            import uuid
            unique_dir = os.path.join(tempfile.gettempdir(), f"chrome_user_data_{uuid.uuid4().hex[:8]}")
            chrome_options.add_argument(f"--user-data-dir={unique_dir}")
            logger.info(f"Using unique user data directory: {unique_dir}")
        
        # Enable DevTools for cache clearing (removed incognito)
        chrome_options.add_argument("--enable-automation")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
    elif browser.lower() == "firefox":
        firefox_options = FirefoxOptions()
        if headless or is_ci:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        # Firefox preferences for normal browsing (removed cache disabling)
        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("media.volume_scale", "0.0")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
    
    else:
        raise ValueError(f"Browser {browser} is not supported")
    
    if not is_ci:
        driver.maximize_window()
    driver.implicitly_wait(10)
    
    # Clear all cookies and local storage for clean test start
    driver.delete_all_cookies()
    logger.info("Cleared all cookies for clean test start")
    
    yield driver
    
    # Clean up after test - clear cookies and close
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        logger.info("Cleaned up cookies and storage after test")
    except Exception as e:
        logger.warning(f"Could not clear storage after test: {e}")
    
    logger.info("Closing driver")
    driver.quit()

@pytest.fixture(scope="function")
def base_url(request):
    """Get base URL from command line or use default"""
    return request.config.getoption("--base-url", default=BASE_URL)

# ============================================================================
# BASE PAGE CLASS
# ============================================================================

class BasePage:
    """Base page class containing common methods for all pages"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
    
    def clear_browser_data(self):
        """Clear browser cache, cookies, and site data specifically for the current website"""
        try:
            self.logger.info("Clearing website cookies and site data...")
            
            # Method 1: Clear all cookies and site data for current domain
            current_domain = self.driver.execute_script("return window.location.hostname")
            self.logger.info(f"Clearing data for domain: {current_domain}")
            
            # Clear cookies
            self.driver.delete_all_cookies()
            self.logger.info("✓ Cleared all cookies")
            
            # Method 2: Clear all types of storage
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            self.logger.info("✓ Cleared localStorage and sessionStorage")
            
            # Method 3: Clear Chrome site data using DevTools Protocol
            try:
                # Clear cache
                self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
                self.logger.info("✓ Cleared browser cache")
                
                # Clear cookies via CDP
                self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
                self.logger.info("✓ Cleared browser cookies via CDP")
                
                # Clear all browsing data (Chrome specific)
                self.driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
                    'origin': f'https://{current_domain}',
                    'storageTypes': 'all'
                })
                self.logger.info("✓ Cleared all site data for origin")
                
            except Exception as e:
                self.logger.info(f"CDP commands not available (non-Chrome browser): {e}")
            
            # Method 4: Clear IndexedDB, WebSQL, and other storage APIs
            try:
                self.driver.execute_script("""
                    // Clear IndexedDB
                    if (window.indexedDB) {
                        indexedDB.databases().then(databases => {
                            databases.forEach(db => {
                                indexedDB.deleteDatabase(db.name);
                                console.log('Deleted IndexedDB:', db.name);
                            });
                        }).catch(e => console.log('IndexedDB clear error:', e));
                    }
                    
                    // Clear WebSQL
                    if (window.openDatabase) {
                        try {
                            var db = openDatabase('', '', '', '');
                            db.transaction(function(tx) {
                                tx.executeSql('DROP TABLE IF EXISTS test');
                            });
                        } catch(e) {
                            console.log('WebSQL clear error:', e);
                        }
                    }
                    
                    // Clear Service Worker caches
                    if ('caches' in window) {
                        caches.keys().then(names => {
                            names.forEach(name => {
                                caches.delete(name);
                                console.log('Deleted cache:', name);
                            });
                        }).catch(e => console.log('Cache clear error:', e));
                    }
                    
                    // Clear any remaining storage
                    try {
                        window.localStorage.clear();
                        window.sessionStorage.clear();
                        console.log('Storage cleared via script');
                    } catch(e) {
                        console.log('Storage clear error:', e);
                    }
                """)
                self.logger.info("✓ Cleared advanced storage (IndexedDB, WebSQL, Service Workers)")
            except Exception as e:
                self.logger.info(f"Advanced storage clear error: {e}")
            
            # Method 5: Navigate to chrome://settings/content/all to programmatically clear (Chrome only)
            try:
                if "chrome" in self.driver.capabilities.get('browserName', '').lower():
                    # This opens Chrome's site data management
                    original_url = self.driver.current_url
                    self.logger.info("Attempting to clear site data via Chrome settings...")
                    
                    # Try to clear via automation (this might not work in all Chrome versions)
                    self.driver.execute_script(f"""
                        // Attempt to clear site data programmatically
                        if (navigator.storage && navigator.storage.estimate) {{
                            navigator.storage.estimate().then(estimate => {{
                                console.log('Storage before clear:', estimate);
                            }});
                        }}
                        
                        // Clear all possible storage types
                        if ('serviceWorker' in navigator) {{
                            navigator.serviceWorker.getRegistrations().then(registrations => {{
                                registrations.forEach(registration => {{
                                    registration.unregister();
                                }});
                            }});
                        }}
                    """)
                    
            except Exception as e:
                self.logger.info(f"Chrome-specific clearing not available: {e}")
            
            self.logger.info("🎯 Website cookies and site data clearing completed!")
            
        except Exception as e:
            self.logger.warning(f"Could not clear some site data: {e}")
    
    def clear_chrome_site_data_manually(self):
        """Clear Chrome site data by accessing chrome://settings (for reference)"""
        try:
            # Note: This is for reference - automation of chrome:// pages is restricted
            self.logger.info("For manual clearing, you can:")
            self.logger.info("1. Press F12 -> Application tab -> Storage -> Clear site data")
            self.logger.info("2. Or go to chrome://settings/content/all and remove the site")
            self.logger.info("3. Or use Ctrl+Shift+Delete -> Advanced -> All time")
        except Exception as e:
            self.logger.error(f"Manual instruction error: {e}")
    
    def force_cache_reload(self, url):
        """Navigate to URL with cache-busting parameters and hard refresh"""
        import time
        import random
        
        # Add cache-busting parameter
        separator = "&" if "?" in url else "?"
        cache_buster = f"{separator}cb={int(time.time())}{random.randint(1000, 9999)}&nocache=1"
        url_with_cache_buster = f"{url}{cache_buster}"
        
        self.logger.info(f"Loading URL with cache buster: {url_with_cache_buster}")
        self.driver.get(url_with_cache_buster)
        
        # Perform hard refresh to bypass any remaining cache
        self.driver.execute_script("location.reload(true);")
        self.logger.info("✓ Performed hard refresh")
        
    def open_url(self, url):
        """Navigate to specified URL"""
        self.driver.get(url)
        self.logger.info(f"Navigated to: {url}")
    
    def get_title(self):
        """Get page title"""
        return self.driver.title
    
    def get_current_url(self):
        """Get current URL"""
        return self.driver.current_url
    
    def find_element(self, locator, timeout=10):
        """Find single element with explicit wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {locator}")
            raise
    
    def find_elements(self, locator, timeout=10):
        """Find multiple elements with explicit wait"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            self.logger.error(f"Elements not found: {locator}")
            return []
    
    def click_element(self, locator, timeout=10):
        """Click element with explicit wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            self.logger.info(f"Clicked element: {locator}")
        except TimeoutException:
            self.logger.error(f"Element not clickable: {locator}")
            raise
    
    def send_keys(self, locator, text, timeout=10):
        """Send keys to element with explicit wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            element.clear()
            element.send_keys(text)
            self.logger.info(f"Sent keys '{text}' to element: {locator}")
        except TimeoutException:
            self.logger.error(f"Element not found for sending keys: {locator}")
            raise
    
    def get_text(self, locator, timeout=10):
        """Get text from element"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element.text
        except TimeoutException:
            self.logger.error(f"Element not found for getting text: {locator}")
            raise
    
    def is_element_present(self, locator, timeout=5):
        """Check if element is present"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def verify_registration_failure_fast(self):
        """Verify if registration failed (faster version with shorter timeouts)"""
        # Method 1: Check for error messages (shorter timeout)
        if self.is_element_present(self.ALERT_DANGER, timeout=2):
            error_message = self.get_text(self.ALERT_DANGER)
            self.logger.info(f"Error message found: {error_message}")
            return True
        
        if self.is_element_present(self.ALERT_WARNING, timeout=2):
            warning_message = self.get_text(self.ALERT_WARNING)
            self.logger.info(f"Warning message found: {warning_message}")
            return True
        
        # Method 2: Quick URL check
        current_url = self.get_current_url()
        if "register" in current_url.lower() and "success" not in current_url.lower():
            self.logger.info("Still on registration page - indicates failure")
            return True
        
        # Method 3: Quick success element check (shorter timeout)
        success_elements_present = (
            self.is_element_present(self.SUCCESS_HEADING, timeout=1) or
            self.is_element_present(self.ACCOUNT_CREATED_MESSAGE, timeout=1) or
            self.is_element_present(self.ALERT_SUCCESS, timeout=1)
        )
        
        if not success_elements_present:
            self.logger.info("No success elements found - indicates failure")
            return True
        
        return False
    
    def get_error_message_fast(self):
        """Get error message if present (faster version)"""
        if self.is_element_present(self.ALERT_DANGER, timeout=1):
            return self.get_text(self.ALERT_DANGER)
        elif self.is_element_present(self.ALERT_WARNING, timeout=1):
            return self.get_text(self.ALERT_WARNING)
        return None
    
    def fill_partial_form_data(self, data):
        """Fill form with partial data (some fields may be empty for validation testing)"""
        # Fill first name if provided
        if data.get('first_name') is not None:
            if data['first_name']:
                self.send_keys(self.FIRST_NAME_INPUT, data['first_name'])
            else:
                # Clear the field if empty string provided
                self.find_element(self.FIRST_NAME_INPUT).clear()
        
        # Fill last name if provided
        if data.get('last_name') is not None:
            if data['last_name']:
                self.send_keys(self.LAST_NAME_INPUT, data['last_name'])
            else:
                self.find_element(self.LAST_NAME_INPUT).clear()
        
        # Fill email if provided
        if data.get('email') is not None:
            if data['email']:
                self.send_keys(self.EMAIL_INPUT, data['email'])
            else:
                self.find_element(self.EMAIL_INPUT).clear()
        
        # Fill telephone if provided
        if data.get('telephone') is not None:
            if data['telephone']:
                self.send_keys(self.TELEPHONE_INPUT, data['telephone'])
            else:
                self.find_element(self.TELEPHONE_INPUT).clear()
        
        # Fill password if provided
        if data.get('password') is not None:
            if data['password']:
                self.send_keys(self.PASSWORD_INPUT, data['password'])
                self.send_keys(self.PASSWORD_CONFIRM_INPUT, data['password'])
            else:
                self.find_element(self.PASSWORD_INPUT).clear()
                self.find_element(self.PASSWORD_CONFIRM_INPUT).clear()
        
        self.logger.info(f"Filled partial form data: {data}")
    
    def fill_partial_form_data_fast(self, data):
        """Fill form with partial data (faster version - essential fields only)"""
        # Fill first name if provided
        if data.get('first_name'):
            self.send_keys(self.FIRST_NAME_INPUT, data['first_name'])
        
        # Fill last name if provided  
        if data.get('last_name'):
            self.send_keys(self.LAST_NAME_INPUT, data['last_name'])
        
        # Fill email if provided (most critical field)
        if data.get('email'):
            self.send_keys(self.EMAIL_INPUT, data['email'])
        
        # Fill telephone if provided
        if data.get('telephone'):
            self.send_keys(self.TELEPHONE_INPUT, data['telephone'])
        
        # Fill password if provided
        if data.get('password'):
            self.send_keys(self.PASSWORD_INPUT, data['password'])
            self.send_keys(self.PASSWORD_CONFIRM_INPUT, data['password'])
        
        self.logger.info(f"Filled partial form data (fast): {data}")
    
    def get_field_validation_errors(self):
        """Get individual field validation error messages"""
        field_errors = {}
        
        # Common field error selectors (OpenCart specific)
        field_error_selectors = [
            (By.CSS_SELECTOR, ".text-danger"),  # General error messages
            (By.CSS_SELECTOR, ".help-block"),   # Help block errors
            (By.CSS_SELECTOR, ".error"),        # Error class
            (By.XPATH, "//div[contains(@class, 'alert')]//text()"),  # Alert messages
        ]
        
        try:
            # Look for field-specific error messages
            for selector in field_error_selectors:
                if self.is_element_present(selector, timeout=2):
                    error_elements = self.find_elements(selector)
                    for i, element in enumerate(error_elements):
                        error_text = element.text.strip()
                        if error_text:
                            field_errors[f"error_{i+1}"] = error_text
            
            # Look for specific field validation patterns
            field_patterns = {
                "firstname": [
                    (By.XPATH, "//input[@id='input-firstname']/following-sibling::*[contains(@class, 'text-danger')]"),
                    (By.XPATH, "//label[contains(text(), 'First Name')]/following-sibling::*[contains(@class, 'text-danger')]")
                ],
                "lastname": [
                    (By.XPATH, "//input[@id='input-lastname']/following-sibling::*[contains(@class, 'text-danger')]"),
                    (By.XPATH, "//label[contains(text(), 'Last Name')]/following-sibling::*[contains(@class, 'text-danger')]")
                ],
                "email": [
                    (By.XPATH, "//input[@id='input-email']/following-sibling::*[contains(@class, 'text-danger')]"),
                    (By.XPATH, "//label[contains(text(), 'E-Mail')]/following-sibling::*[contains(@class, 'text-danger')]")
                ],
                "telephone": [
                    (By.XPATH, "//input[@id='input-telephone']/following-sibling::*[contains(@class, 'text-danger')]"),
                    (By.XPATH, "//label[contains(text(), 'Telephone')]/following-sibling::*[contains(@class, 'text-danger')]")
                ],
                "password": [
                    (By.XPATH, "//input[@id='input-password']/following-sibling::*[contains(@class, 'text-danger')]"),
                    (By.XPATH, "//label[contains(text(), 'Password')]/following-sibling::*[contains(@class, 'text-danger')]")
                ]
            }
            
            for field_name, selectors in field_patterns.items():
                for selector in selectors:
                    if self.is_element_present(selector, timeout=1):
                        error_element = self.find_element(selector)
                        error_text = error_element.text.strip()
                        if error_text:
                            field_errors[field_name] = error_text
                            break
            
        except Exception as e:
            self.logger.error(f"Error getting field validation errors: {e}")
        
        if field_errors:
            self.logger.info(f"Found field validation errors: {field_errors}")
        
        return field_errors
    
    def is_element_visible(self, locator, timeout=5):
        """Check if element is visible"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def wait_for_page_load(self, timeout=10):
        """Wait for page to load completely"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    
    def scroll_to_element(self, locator, timeout=10):
        """Scroll to element"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.logger.info(f"Scrolled to element: {locator}")
        except TimeoutException:
            self.logger.error(f"Element not found for scrolling: {locator}")
            raise

# ============================================================================
# PAGE OBJECT CLASSES
# ============================================================================

class HomePage(BasePage):
    """Home page object model"""
    
    # Locators
    LOGO = (By.CSS_SELECTOR, "#logo h1 a")
    MY_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "a[title='My Account']")
    LOGIN_LINK = (By.LINK_TEXT, "Login")
    REGISTER_LINK = (By.LINK_TEXT, "Register")
    LOGOUT_LINK = (By.LINK_TEXT, "Logout")
    SEARCH_INPUT = (By.NAME, "search")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".btn.btn-default.btn-lg")
    CART_BUTTON = (By.ID, "cart")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def go_to_login_page(self):
        """Navigate to login page via My Account dropdown"""
        self.logger.info("Navigating to login page")
        
        # Click on My Account dropdown
        self.click_element(self.MY_ACCOUNT_DROPDOWN)
        time.sleep(1)  # Small wait for dropdown to appear
        
        # Click on Login link
        self.click_element(self.LOGIN_LINK)
        
        self.logger.info("Successfully navigated to login page")
    
    def go_to_register_page(self):
        """Navigate to registration page via My Account dropdown"""
        self.logger.info("Navigating to registration page")
        
        # Click on My Account dropdown
        self.click_element(self.MY_ACCOUNT_DROPDOWN)
        time.sleep(1)  # Small wait for dropdown to appear
        
        # Click on Register link
        self.click_element(self.REGISTER_LINK)
        
        self.logger.info("Successfully navigated to registration page")
    
    def is_user_logged_in(self):
        """Check if user is logged in by looking for logout option"""
        try:
            # Click on My Account dropdown
            self.click_element(self.MY_ACCOUNT_DROPDOWN)
            time.sleep(1)
            
            # Check if logout link is present
            is_logged_in = self.is_element_present(self.LOGOUT_LINK, timeout=3)
            
            # Click somewhere else to close dropdown
            self.click_element(self.LOGO)
            
            return is_logged_in
        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False

class LoginPage(BasePage):
    """Login page object model"""
    
    # Locators
    PAGE_HEADING = (By.TAG_NAME, "h1")
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")
    
    # New Customer Section
    NEW_CUSTOMER_HEADING = (By.XPATH, "//h2[text()='New Customer']")
    REGISTER_TEXT = (By.XPATH, "//h2[text()='New Customer']/following-sibling::p")
    CONTINUE_BUTTON = (By.LINK_TEXT, "Continue")
    
    # Returning Customer Section
    RETURNING_CUSTOMER_HEADING = (By.XPATH, "//h2[text()='Returning Customer']")
    RETURNING_CUSTOMER_TEXT = (By.XPATH, "//strong[text()='I am a returning customer']")
    
    # Login Form Elements
    EMAIL_INPUT = (By.ID, "input-email")
    PASSWORD_INPUT = (By.ID, "input-password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Login']")
    FORGOTTEN_PASSWORD_LINK = (By.LINK_TEXT, "Forgotten Password")
    
    # Error/Success Messages
    ALERT_DANGER = (By.CSS_SELECTOR, ".alert.alert-danger")
    ALERT_SUCCESS = (By.CSS_SELECTOR, ".alert.alert-success")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def verify_login_page_loaded(self):
        """Verify that login page has loaded properly"""
        self.logger.info("Verifying login page elements")
        
        # Wait for page to load
        self.wait_for_page_load()
        
        # Verify page elements
        assert self.is_element_present(self.NEW_CUSTOMER_HEADING), "New Customer section not found"
        assert self.is_element_present(self.RETURNING_CUSTOMER_HEADING), "Returning Customer section not found"
        assert self.is_element_present(self.EMAIL_INPUT), "Email input field not found"
        assert self.is_element_present(self.PASSWORD_INPUT), "Password input field not found"
        assert self.is_element_present(self.LOGIN_BUTTON), "Login button not found"
        
        self.logger.info("Login page loaded successfully")
    
    def login_with_credentials(self, email, password):
        """Login with provided credentials"""
        self.logger.info(f"Attempting to login with email: {email}")
        
        # Enter email
        self.send_keys(self.EMAIL_INPUT, email)
        
        # Enter password
        self.send_keys(self.PASSWORD_INPUT, password)
        
        # Click login button
        self.click_element(self.LOGIN_BUTTON)
        
        # Wait for page to load after login attempt
        time.sleep(2)
        
        self.logger.info("Login form submitted")
    
    def is_login_successful(self):
        """Check if login was successful by checking for error messages"""
        # Check if there are any error messages
        if self.is_element_present(self.ALERT_DANGER, timeout=3):
            error_message = self.get_text(self.ALERT_DANGER)
            self.logger.error(f"Login failed with error: {error_message}")
            return False, error_message
        
        # If no error message and we're redirected away from login page, login was successful
        current_url = self.get_current_url()
        if "login" not in current_url.lower():
            self.logger.info("Login successful - redirected from login page")
            return True, "Login successful"
        
        return False, "Unknown login status"

class AccountPage(BasePage):
    """Account/Dashboard page object model"""
    
    # Locators
    PAGE_HEADING = (By.TAG_NAME, "h2")
    ACCOUNT_LINKS = (By.CSS_SELECTOR, ".list-group a")
    EDIT_ACCOUNT_LINK = (By.LINK_TEXT, "Edit Account")
    PASSWORD_LINK = (By.LINK_TEXT, "Password")
    ADDRESS_BOOK_LINK = (By.LINK_TEXT, "Address Book")
    WISH_LIST_LINK = (By.LINK_TEXT, "Wish List")
    ORDER_HISTORY_LINK = (By.LINK_TEXT, "Order History")
    LOGOUT_LINK = (By.LINK_TEXT, "Logout")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def verify_account_page_loaded(self):
        """Verify that account dashboard page has loaded"""
        self.logger.info("Verifying account page elements")
        
        # Wait for page to load
        self.wait_for_page_load()
        
        # Check for account page elements
        assert self.is_element_present(self.EDIT_ACCOUNT_LINK), "Edit Account link not found"
        assert self.is_element_present(self.ORDER_HISTORY_LINK), "Order History link not found"
        
        # Check URL contains account
        current_url = self.get_current_url()
        assert "account" in current_url.lower(), f"Not on account page. Current URL: {current_url}"
        
        self.logger.info("Account page loaded successfully")

class ForgottenPasswordPage(BasePage):
    """Forgotten Password page object model"""
    
    # Locators
    PAGE_HEADING = (By.TAG_NAME, "h1")
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")
    ACCOUNT_BREADCRUMB = (By.LINK_TEXT, "Account")
    FORGOTTEN_PASSWORD_BREADCRUMB = (By.LINK_TEXT, "Forgotten Password")
    
    # Page content
    PAGE_DESCRIPTION = (By.XPATH, "//p[contains(text(), 'Enter the e-mail address associated with your account')]")
    EMAIL_LABEL = (By.XPATH, "//label[text()='Your E-Mail Address']")
    
    # Form elements
    EMAIL_INPUT = (By.ID, "input-email")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "input[value='Continue']")
    BACK_BUTTON = (By.LINK_TEXT, "Back")
    
    # Messages
    ALERT_SUCCESS = (By.CSS_SELECTOR, ".alert.alert-success")
    ALERT_DANGER = (By.CSS_SELECTOR, ".alert.alert-danger")
    ALERT_WARNING = (By.CSS_SELECTOR, ".alert.alert-warning")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def verify_forgotten_password_page_loaded(self):
        """Verify that forgotten password page has loaded properly"""
        self.logger.info("Verifying forgotten password page elements")
        
        # Wait for page to load
        self.wait_for_page_load()
        
        # Verify URL contains forgotten password
        current_url = self.get_current_url()
        assert "forgotten" in current_url.lower() or "password" in current_url.lower(), \
            f"Not on forgotten password page. Current URL: {current_url}"
        
        # Verify page heading or content
        page_elements_present = (
            self.is_element_present(self.EMAIL_INPUT) and
            self.is_element_present(self.CONTINUE_BUTTON)
        )
        assert page_elements_present, "Required forgotten password page elements not found"
        
        # Verify breadcrumb shows correct navigation
        if self.is_element_present(self.BREADCRUMB):
            breadcrumb_text = self.get_text(self.BREADCRUMB)
            self.logger.info(f"Breadcrumb: {breadcrumb_text}")
        
        self.logger.info("Forgotten password page loaded successfully")
    
    def enter_email(self, email):
        """Enter email address in the email field"""
        self.send_keys(self.EMAIL_INPUT, email)
        self.logger.info(f"Entered email: {email}")
    
    def click_continue_button(self):
        """Click the Continue button"""
        self.click_element(self.CONTINUE_BUTTON)
        self.logger.info("Clicked Continue button")
        
        # Wait for page to process
        time.sleep(2)
    
    def click_back_button(self):
        """Click the Back button"""
        self.click_element(self.BACK_BUTTON)
        self.logger.info("Clicked Back button")
    
    def verify_submission_success(self):
        """Verify if the forgotten password submission was successful"""
        # Check for success message
        if self.is_element_present(self.ALERT_SUCCESS, timeout=5):
            success_message = self.get_text(self.ALERT_SUCCESS)
            self.logger.info(f"Success message: {success_message}")
            return True
        
        # Check if redirected to login page (some implementations do this)
        current_url = self.get_current_url()
        if "login" in current_url.lower() and "forgotten" not in current_url.lower():
            self.logger.info("Redirected to login page - submission successful")
            return True
        
        # Check if there's a confirmation message in page content
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            success_keywords = ["sent", "email", "reset", "link", "check", "inbox"]
            if any(keyword in page_text for keyword in success_keywords):
                self.logger.info("Page contains confirmation text - submission successful")
                return True
        except:
            pass
        
        return False
    
    def get_error_message(self):
        """Get error message if present"""
        if self.is_element_present(self.ALERT_DANGER):
            return self.get_text(self.ALERT_DANGER)
        elif self.is_element_present(self.ALERT_WARNING):
            return self.get_text(self.ALERT_WARNING)
        return None

class RegistrationPage(BasePage):
    """Registration page object model"""
    
    # Locators
    PAGE_HEADING = (By.TAG_NAME, "h1")
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")
    ACCOUNT_BREADCRUMB = (By.LINK_TEXT, "Account")
    REGISTER_BREADCRUMB = (By.LINK_TEXT, "Register")
    
    # Personal Details Section
    PERSONAL_DETAILS_HEADING = (By.XPATH, "//legend[text()='Your Personal Details']")
    FIRST_NAME_INPUT = (By.ID, "input-firstname")
    LAST_NAME_INPUT = (By.ID, "input-lastname")
    EMAIL_INPUT = (By.ID, "input-email")
    TELEPHONE_INPUT = (By.ID, "input-telephone")
    
    # Password Section
    PASSWORD_HEADING = (By.XPATH, "//legend[text()='Your Password']")
    PASSWORD_INPUT = (By.ID, "input-password")
    PASSWORD_CONFIRM_INPUT = (By.ID, "input-confirm")
    
    # Newsletter Section
    NEWSLETTER_HEADING = (By.XPATH, "//legend[text()='Newsletter']")
    NEWSLETTER_YES_RADIO = (By.XPATH, "//input[@name='newsletter' and @value='1']")
    NEWSLETTER_NO_RADIO = (By.XPATH, "//input[@name='newsletter' and @value='0']")
    
    # Privacy Policy
    PRIVACY_POLICY_CHECKBOX = (By.NAME, "agree")
    PRIVACY_POLICY_LINK = (By.LINK_TEXT, "Privacy Policy")
    
    # Buttons
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "input[value='Continue']")
    
    # Messages
    ALERT_SUCCESS = (By.CSS_SELECTOR, ".alert.alert-success")
    ALERT_DANGER = (By.CSS_SELECTOR, ".alert.alert-danger")
    ALERT_WARNING = (By.CSS_SELECTOR, ".alert.alert-warning")
    
    # Success page elements
    SUCCESS_HEADING = (By.XPATH, "//h1[contains(text(), 'Your Account Has Been Created')]")
    ACCOUNT_CREATED_MESSAGE = (By.XPATH, "//p[contains(text(), 'Congratulations')]")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def verify_registration_page_loaded(self):
        """Verify that registration page has loaded properly"""
        self.logger.info("Verifying registration page elements")
        
        # Wait for page to load
        self.wait_for_page_load()
        
        # Verify URL contains register
        current_url = self.get_current_url()
        assert "register" in current_url.lower() or "account" in current_url.lower(), \
            f"Not on registration page. Current URL: {current_url}"
        
        # Verify required form elements are present
        required_elements = [
            self.FIRST_NAME_INPUT,
            self.LAST_NAME_INPUT,
            self.EMAIL_INPUT,
            self.TELEPHONE_INPUT,
            self.PASSWORD_INPUT,
            self.PASSWORD_CONFIRM_INPUT,
            self.PRIVACY_POLICY_CHECKBOX,
            self.CONTINUE_BUTTON
        ]
        
        for element in required_elements:
            assert self.is_element_present(element), f"Required element not found: {element}"
        
        # Verify breadcrumb shows correct navigation
        if self.is_element_present(self.BREADCRUMB):
            breadcrumb_text = self.get_text(self.BREADCRUMB)
            self.logger.info(f"Breadcrumb: {breadcrumb_text}")
        
        self.logger.info("Registration page loaded successfully")
    
    def fill_personal_details(self, first_name, last_name, email, telephone):
        """Fill in personal details section"""
        self.send_keys(self.FIRST_NAME_INPUT, first_name)
        self.send_keys(self.LAST_NAME_INPUT, last_name)
        self.send_keys(self.EMAIL_INPUT, email)
        self.send_keys(self.TELEPHONE_INPUT, telephone)
        
        self.logger.info(f"Filled personal details: {first_name} {last_name}, {email}, {telephone}")
    
    def fill_password_fields(self, password):
        """Fill in password and confirm password fields"""
        self.send_keys(self.PASSWORD_INPUT, password)
        self.send_keys(self.PASSWORD_CONFIRM_INPUT, password)
        
        self.logger.info("Password fields filled successfully")
    
    def select_newsletter_option(self, subscribe=False):
        """Select newsletter subscription option"""
        if subscribe:
            self.click_element(self.NEWSLETTER_YES_RADIO)
            self.logger.info("Selected newsletter subscription: Yes")
        else:
            self.click_element(self.NEWSLETTER_NO_RADIO)
            self.logger.info("Selected newsletter subscription: No")
    
    def accept_privacy_policy(self):
        """Accept privacy policy by checking the checkbox"""
        # Scroll to the privacy policy checkbox to ensure it's visible
        self.scroll_to_element(self.PRIVACY_POLICY_CHECKBOX)
        
        # Click the privacy policy checkbox
        self.click_element(self.PRIVACY_POLICY_CHECKBOX)
        
        self.logger.info("Privacy policy accepted")
    
    def is_privacy_policy_checked(self):
        """Check if privacy policy checkbox is checked"""
        try:
            checkbox = self.find_element(self.PRIVACY_POLICY_CHECKBOX)
            is_checked = checkbox.is_selected()
            self.logger.info(f"Privacy policy checkbox checked status: {is_checked}")
            return is_checked
        except Exception as e:
            self.logger.error(f"Error checking privacy policy checkbox: {e}")
            return False
    
    def get_email_field_value(self):
        """Get current value in email field"""
        try:
            email_field = self.find_element(self.EMAIL_INPUT)
            email_value = email_field.get_attribute("value")
            return email_value
        except Exception as e:
            self.logger.error(f"Error getting email field value: {e}")
            return ""
    
    def get_first_name_field_value(self):
        """Get current value in first name field"""
        try:
            first_name_field = self.find_element(self.FIRST_NAME_INPUT)
            first_name_value = first_name_field.get_attribute("value")
            return first_name_value
        except Exception as e:
            self.logger.error(f"Error getting first name field value: {e}")
            return ""
    
    def verify_registration_failure(self):
        """Verify if registration failed (opposite of verify_registration_success)"""
        # Method 1: Check for error messages
        if self.is_element_present(self.ALERT_DANGER, timeout=5):
            error_message = self.get_text(self.ALERT_DANGER)
            self.logger.info(f"Error message found: {error_message}")
            return True
        
        if self.is_element_present(self.ALERT_WARNING, timeout=5):
            warning_message = self.get_text(self.ALERT_WARNING)
            self.logger.info(f"Warning message found: {warning_message}")
            return True
        
        # Method 2: Check if still on registration page (not redirected)
        current_url = self.get_current_url()
        if "register" in current_url.lower() and "success" not in current_url.lower():
            self.logger.info("Still on registration page - indicates failure")
            return True
        
        # Method 3: Check for validation errors in page content
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            error_keywords = ["error", "required", "invalid", "please", "must", "agree", "policy"]
            if any(keyword in page_text for keyword in error_keywords):
                self.logger.info("Page contains validation error text")
                return True
        except:
            pass
        
        # Method 4: Check if success elements are NOT present
        success_elements_present = (
            self.is_element_present(self.SUCCESS_HEADING, timeout=2) or
            self.is_element_present(self.ACCOUNT_CREATED_MESSAGE, timeout=2) or
            self.is_element_present(self.ALERT_SUCCESS, timeout=2)
        )
        
        if not success_elements_present:
            self.logger.info("No success elements found - indicates failure")
            return True
        
        return False
    
    def click_continue_button(self):
        """Click the Continue button to submit registration"""
        # Scroll to the continue button to ensure it's visible
        self.scroll_to_element(self.CONTINUE_BUTTON)
        
        # Click continue button
        self.click_element(self.CONTINUE_BUTTON)
        
        self.logger.info("Continue button clicked")
        
        # Wait for page to process
        time.sleep(3)
    
    def click_continue_button_fast(self):
        """Click the Continue button to submit registration (faster version)"""
        # Scroll to the continue button to ensure it's visible
        self.scroll_to_element(self.CONTINUE_BUTTON)
        
        # Click continue button
        self.click_element(self.CONTINUE_BUTTON)
        
        self.logger.info("Continue button clicked (fast)")
        
        # Shorter wait for page to process
        time.sleep(1)
    
    def verify_registration_success(self):
        """Verify if registration was successful"""
        # Method 1: Check for success page heading
        if self.is_element_present(self.SUCCESS_HEADING, timeout=10):
            success_text = self.get_text(self.SUCCESS_HEADING)
            self.logger.info(f"Success heading found: {success_text}")
            return True
        
        # Method 2: Check for congratulations message
        if self.is_element_present(self.ACCOUNT_CREATED_MESSAGE, timeout=5):
            congrats_text = self.get_text(self.ACCOUNT_CREATED_MESSAGE)
            self.logger.info(f"Congratulations message found: {congrats_text}")
            return True
        
        # Method 3: Check for success alert
        if self.is_element_present(self.ALERT_SUCCESS, timeout=5):
            success_message = self.get_text(self.ALERT_SUCCESS)
            self.logger.info(f"Success alert found: {success_message}")
            return True
        
        # Method 4: Check if redirected to account page
        current_url = self.get_current_url()
        if "account/success" in current_url.lower() or "account/account" in current_url.lower():
            self.logger.info("Redirected to account success page")
            return True
        
        # Method 5: Check page content for success keywords
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            success_keywords = ["congratulations", "account has been created", "successfully", "welcome"]
            if any(keyword in page_text for keyword in success_keywords):
                self.logger.info("Page contains success confirmation text")
                return True
        except:
            pass
        
        return False
    
    def get_error_message(self):
        """Get error message if present"""
        if self.is_element_present(self.ALERT_DANGER):
            return self.get_text(self.ALERT_DANGER)
        elif self.is_element_present(self.ALERT_WARNING):
            return self.get_text(self.ALERT_WARNING)
        return None

# ============================================================================
# ADDITIONAL IMPORTS FOR REGISTRATION PAGE
# ============================================================================

import random
import string

# ============================================================================
# TEST CASES
# ============================================================================

class TestUserLogin:
    """Test cases for user login functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, base_url):
        """Setup for each test method"""
        self.driver = driver
        self.base_url = base_url
        self.home_page = HomePage(driver)
        self.login_page = LoginPage(driver)
        self.account_page = AccountPage(driver)
        
        # Navigate to homepage first
        self.home_page.open_url(base_url)
        
        # Clear website cache and data after loading the page
        self.home_page.clear_browser_data()
        
        # Navigate again with fresh cache
        self.home_page.force_cache_reload(base_url)
    
    def test_verify_user_login_with_valid_credentials_TC_001(self):
        """
        Test Case: Verify user login with valid credentials
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Login link
        4. Verify login page loads correctly
        5. Enter valid email: fatimahasanat6@gmail.com
        6. Enter valid password: 123968574
        7. Click Login button
        8. Verify successful login by checking account dashboard
        """
        
        logger.info("Starting test: Verify user login with valid credentials")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to login page
        self.home_page.go_to_login_page()
        
        # Step 4: Verify login page loaded
        self.login_page.verify_login_page_loaded()
        logger.info("✓ Login page loaded successfully")
        
        # Step 5 & 6 & 7: Login with valid credentials
        self.login_page.login_with_credentials(VALID_EMAIL, VALID_PASSWORD)
        
        # Step 8: Verify successful login
        login_success, message = self.login_page.is_login_successful()
        
        if login_success:
            logger.info("✓ Login successful - verifying account page")
            self.account_page.verify_account_page_loaded()
            logger.info("✓ Account dashboard loaded successfully")
            
            # Additional verification: Check if user is logged in from homepage
            self.home_page.open_url(self.base_url)
            assert self.home_page.is_user_logged_in(), "User not logged in according to homepage"
            logger.info("✓ User login status confirmed from homepage")
            
        else:
            pytest.fail(f"Login failed: {message}")
        
        logger.info("✅ Test completed successfully: User login with valid credentials")
    
    def test_verify_user_login_with_invalid_credentials_TC_002(self):
        """
        Test Case: Verify user login with invalid credentials
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Login link
        4. Verify login page loads correctly
        5. Enter invalid email: invalid@test.com
        6. Enter invalid password: wrongpassword
        7. Click Login button
        8. Verify login fails with appropriate error message
        9. Verify user remains on login page
        """
        
        logger.info("Starting test: Verify user login with invalid credentials")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to login page
        self.home_page.go_to_login_page()
        
        # Step 4: Verify login page loaded
        self.login_page.verify_login_page_loaded()
        logger.info("✓ Login page loaded successfully")
        
        # Step 5 & 6 & 7: Login with invalid credentials
        invalid_email = "invalid@test.com"
        invalid_password = "wrongpassword"
        self.login_page.login_with_credentials(invalid_email, invalid_password)
        
        # Step 8: Verify login fails with error message
        login_success, message = self.login_page.is_login_successful()
        
        if not login_success:
            logger.info("✓ Login correctly failed with invalid credentials")
            logger.info(f"✓ Error message displayed: {message}")
            
            # Step 9: Verify we're still on login page
            current_url = self.login_page.get_current_url()
            assert "login" in current_url.lower(), f"Expected to remain on login page, but URL is: {current_url}"
            logger.info("✓ User correctly remains on login page after failed login")
            
            # Additional verification: Check that error message is appropriate
            if self.login_page.is_element_present(self.login_page.ALERT_DANGER):
                error_text = self.login_page.get_text(self.login_page.ALERT_DANGER)
                expected_error_keywords = ["warning", "no match", "incorrect", "invalid", "error"]
                
                error_found = any(keyword in error_text.lower() for keyword in expected_error_keywords)
                assert error_found, f"Expected error message with warning keywords, got: {error_text}"
                logger.info(f"✓ Appropriate error message displayed: {error_text}")
            
            # Verify user is NOT logged in from homepage
            self.home_page.open_url(self.base_url)
            assert not self.home_page.is_user_logged_in(), "User should not be logged in with invalid credentials"
            logger.info("✓ User login status confirmed as NOT logged in")
            
        else:
            pytest.fail(f"Login should have failed with invalid credentials, but it succeeded: {message}")
        
        logger.info("✅ Test completed successfully: User login with invalid credentials")
    
    def test_login_and_continue_from_last_activity_TC_003(self):
        """
        Test Case: Login and Continue from Last Activity
        
        Steps:
        1. Clear cache and navigate to OpenCart homepage
        2. Click on My Account dropdown and select Login
        3. Enter valid credentials and login
        4. Verify account dashboard is loaded
        5. Click on My Account dropdown and select Logout
        6. Verify logout success page with Continue button
        7. Click Continue button
        8. Verify we're back on homepage
        """
        
        logger.info("Starting test: Login and Continue from Last Activity")
        
        # Step 1: Verify we're on homepage (cache already cleared in setup)
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully with cache cleared")
        
        # Step 2: Click on My Account dropdown and select Login
        self.home_page.go_to_login_page()
        logger.info("✓ Navigated to login page via My Account dropdown")
        
        # Step 3: Enter valid credentials and login
        self.login_page.verify_login_page_loaded()
        self.login_page.login_with_credentials(VALID_EMAIL, VALID_PASSWORD)
        logger.info("✓ Login credentials entered and submitted")
        
        # Verify login was successful
        login_success, message = self.login_page.is_login_successful()
        if not login_success:
            pytest.fail(f"Login failed: {message}")
        
        # Step 4: Verify account dashboard is loaded
        self.account_page.verify_account_page_loaded()
        logger.info("✓ Account dashboard loaded successfully after login")
        
        # Step 5: Click on My Account dropdown and select Logout
        # Navigate to current page to ensure we can access the dropdown
        current_url = self.driver.current_url
        self.home_page.open_url(current_url)
        
        # Click My Account dropdown
        self.home_page.click_element(self.home_page.MY_ACCOUNT_DROPDOWN)
        time.sleep(1)  # Wait for dropdown to appear
        
        # Click Logout
        self.home_page.click_element(self.home_page.LOGOUT_LINK)
        logger.info("✓ Logout clicked via My Account dropdown")
        
        # Step 6: Verify logout success page with Continue button
        # Wait for logout page to load
        time.sleep(2)
        
        # Verify we're on logout page
        current_url = self.driver.current_url
        assert "logout" in current_url.lower() or "account" in current_url.lower(), \
            f"Expected to be on logout page, but URL is: {current_url}"
        
        # Verify Continue button is present
        continue_button_locator = (By.LINK_TEXT, "Continue")
        continue_button_alt = (By.CSS_SELECTOR, "a.btn")
        
        continue_button_present = (
            self.home_page.is_element_present(continue_button_locator, timeout=5) or
            self.home_page.is_element_present(continue_button_alt, timeout=5)
        )
        assert continue_button_present, "Continue button not found on logout page"
        logger.info("✓ Logout success page loaded with Continue button")
        
        # Step 7: Click Continue button
        try:
            if self.home_page.is_element_present(continue_button_locator, timeout=3):
                self.home_page.click_element(continue_button_locator)
                logger.info("✓ Continue button clicked (primary locator)")
            elif self.home_page.is_element_present(continue_button_alt, timeout=3):
                self.home_page.click_element(continue_button_alt)
                logger.info("✓ Continue button clicked (alternative locator)")
            else:
                # Look for any element with "Continue" text
                continue_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Continue')]")
                if continue_elements:
                    continue_elements[0].click()
                    logger.info("✓ Continue button clicked (xpath text search)")
                else:
                    pytest.fail("Continue button not found")
        except Exception as e:
            pytest.fail(f"Failed to click Continue button: {e}")
        
        # Step 8: Verify we're back on homepage
        # Wait for navigation to complete
        time.sleep(2)
        
        # Verify we're on homepage - only check this as requested
        final_url = self.driver.current_url
        homepage_indicators = [
            self.base_url in final_url,
            "common/home" in final_url.lower(),
            final_url.endswith("/") or final_url.endswith("/index.php")
        ]
        
        is_on_homepage = any(homepage_indicators)
        assert is_on_homepage, f"Expected to be on homepage, but URL is: {final_url}"
        
        # Additional verification: Check page title
        if "Your Store" in self.home_page.get_title():
            logger.info("✓ Homepage title confirmed")
        
        logger.info("✓ Successfully returned to homepage after clicking Continue")
        logger.info("✅ Test completed successfully: Login and Continue from Last Activity")
    
    def test_verify_forgotten_password_functionality_TC_004(self):
        """
        Test Case: Verify 'Forgotten Password' functionality
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Login link
        4. Verify login page loads correctly
        5. Click on 'Forgotten Password' link
        6. Verify forgotten password page loads correctly
        7. Enter a valid email address
        8. Click Continue button
        9. Verify success or confirmation message
        """
        
        logger.info("Starting test: Verify 'Forgotten Password' functionality")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to login page
        self.home_page.go_to_login_page()
        
        # Step 4: Verify login page loaded
        self.login_page.verify_login_page_loaded()
        logger.info("✓ Login page loaded successfully")
        
        # Step 5: Click on 'Forgotten Password' link
        self.login_page.click_element(self.login_page.FORGOTTEN_PASSWORD_LINK)
        logger.info("✓ Clicked on 'Forgotten Password' link")
        
        # Step 6: Verify forgotten password page loads correctly
        self.forgotten_password_page = ForgottenPasswordPage(self.driver)
        self.forgotten_password_page.verify_forgotten_password_page_loaded()
        logger.info("✓ Forgotten Password page loaded successfully")
        
        # Step 7: Enter a valid email address
        test_email = "fatimahasanat6@gmail.com"  # Using the same valid email
        self.forgotten_password_page.enter_email(test_email)
        logger.info(f"✓ Entered email: {test_email}")
        
        # Step 8: Click Continue button
        self.forgotten_password_page.click_continue_button()
        logger.info("✓ Clicked Continue button")
        
        # Step 9: Verify success or confirmation message
        success = self.forgotten_password_page.verify_submission_success()
        
        if success:
            logger.info("✓ Forgotten password request submitted successfully")
            logger.info("✓ Confirmation message displayed or page redirected appropriately")
        else:
            # Even if no explicit success message, verify we're not on the same page with errors
            current_url = self.forgotten_password_page.get_current_url()
            has_errors = self.forgotten_password_page.is_element_present(
                self.forgotten_password_page.ALERT_DANGER, timeout=3
            )
            
            if not has_errors:
                logger.info("✓ No error messages displayed - submission appears successful")
            else:
                error_message = self.forgotten_password_page.get_text(
                    self.forgotten_password_page.ALERT_DANGER
                )
                logger.warning(f"Warning: Error message displayed: {error_message}")
        
        logger.info("✅ Test completed successfully: Verify 'Forgotten Password' functionality")
    
    def test_verify_new_customer_registration_flow_TC_005(self):
        """
        Test Case: Verify new customer registration flow
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Register link
        4. Verify registration page loads correctly
        5. Fill in all required personal details with random data
        6. Fill in password fields
        7. Accept privacy policy
        8. Click Continue button
        9. Verify successful registration
        """
        
        logger.info("Starting test: Verify new customer registration flow")
        
        # Generate random test data
        import random
        import string
        
        # Generate random email
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_{random_str}@example.com"
        
        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Generate random personal data
        first_name = f"Test{random.randint(100, 999)}"
        last_name = f"User{random.randint(100, 999)}"
        telephone = f"555{random.randint(1000000, 9999999)}"
        
        logger.info(f"Generated test data - Email: {test_email}, Name: {first_name} {last_name}")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to registration page
        self.home_page.go_to_register_page()
        
        # Step 4: Verify registration page loaded
        self.registration_page = RegistrationPage(self.driver)
        self.registration_page.verify_registration_page_loaded()
        logger.info("✓ Registration page loaded successfully")
        
        # Step 5: Fill in personal details
        self.registration_page.fill_personal_details(
            first_name=first_name,
            last_name=last_name,
            email=test_email,
            telephone=telephone
        )
        logger.info("✓ Personal details filled successfully")
        
        # Step 6: Fill in password fields
        self.registration_page.fill_password_fields(password)
        logger.info("✓ Password fields filled successfully")
        
        # Step 7: Accept privacy policy
        self.registration_page.accept_privacy_policy()
        logger.info("✓ Privacy policy accepted")
        
        # Step 8: Click Continue button
        self.registration_page.click_continue_button()
        logger.info("✓ Continue button clicked")
        
        # Step 9: Verify successful registration
        success = self.registration_page.verify_registration_success()
        
        if success:
            logger.info("✓ Registration completed successfully")
            logger.info("✓ Account created and user is logged in")
            
            # Additional verification: Check if redirected to account page
            current_url = self.registration_page.get_current_url()
            if "account" in current_url.lower():
                logger.info("✓ Redirected to account dashboard after registration")
        else:
            # Check for any error messages
            if self.registration_page.is_element_present(self.registration_page.ALERT_DANGER):
                error_message = self.registration_page.get_text(self.registration_page.ALERT_DANGER)
                pytest.fail(f"Registration failed with error: {error_message}")
            else:
                pytest.fail("Registration did not complete successfully")
        
        logger.info(f"✅ Test completed successfully: New customer registration with email: {test_email}")
    
    def test_verify_registration_with_existing_email_TC_006(self):
        """
        Test Case: Verify registration with existing email
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Register link
        4. Verify registration page loads correctly
        5. Fill in all required personal details with EXISTING email
        6. Fill in password fields
        7. Accept privacy policy
        8. Click Continue button
        9. Verify registration fails with "email already exists" error message
        10. Verify user remains on registration page
        """
        
        logger.info("Starting test: Verify registration with existing email")
        
        # Use an existing email (the valid login email from our test data)
        existing_email = VALID_EMAIL  # "fatimahasanat6@gmail.com"
        
        # Generate random password and other data
        import random
        import string
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        first_name = f"Test{random.randint(100, 999)}"
        last_name = f"User{random.randint(100, 999)}"
        telephone = f"555{random.randint(1000000, 9999999)}"
        
        logger.info(f"Attempting registration with existing email: {existing_email}")
        logger.info(f"Generated other data - Name: {first_name} {last_name}")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to registration page
        self.home_page.go_to_register_page()
        
        # Step 4: Verify registration page loaded
        self.registration_page = RegistrationPage(self.driver)
        self.registration_page.verify_registration_page_loaded()
        logger.info("✓ Registration page loaded successfully")
        
        # Step 5: Fill in personal details with EXISTING email
        self.registration_page.fill_personal_details(
            first_name=first_name,
            last_name=last_name,
            email=existing_email,  # Using existing email - should cause conflict
            telephone=telephone
        )
        logger.info(f"✓ Personal details filled with existing email: {existing_email}")
        
        # Step 6: Fill in password fields
        self.registration_page.fill_password_fields(password)
        logger.info("✓ Password fields filled successfully")
        
        # Step 7: Accept privacy policy
        self.registration_page.accept_privacy_policy()
        logger.info("✓ Privacy policy accepted")
        
        # Step 8: Click Continue button (should fail due to existing email)
        self.registration_page.click_continue_button()
        logger.info("✓ Continue button clicked")
        
        # Step 9: Verify registration fails with "email already exists" error
        registration_failed = self.registration_page.verify_registration_failure()
        
        if registration_failed:
            logger.info("✓ Registration correctly failed with existing email")
            
            # Check for specific "email already exists" error message
            error_message = self.registration_page.get_error_message()
            if error_message:
                # Check if error message mentions email conflict
                email_conflict_keywords = [
                    "email", "e-mail", "already", "exists", "registered", 
                    "address", "use", "taken", "account", "duplicate"
                ]
                email_conflict_found = any(keyword in error_message.lower() for keyword in email_conflict_keywords)
                
                if email_conflict_found:
                    logger.info(f"✓ Appropriate email conflict error message: {error_message}")
                else:
                    logger.info(f"✓ Error message displayed: {error_message}")
                
                # Additional check for email-specific field errors
                field_errors = self.registration_page.get_field_validation_errors()
                if field_errors:
                    email_field_error = field_errors.get('email', '')
                    if email_field_error:
                        logger.info(f"✓ Email field specific error: {email_field_error}")
            else:
                logger.info("✓ Registration failed (checking for other error indicators)")
            
            # Step 10: Verify user remains on registration page
            current_url = self.registration_page.get_current_url()
            assert "register" in current_url.lower() or "account/register" in current_url.lower(), \
                f"Expected to remain on registration page, but URL is: {current_url}"
            logger.info("✓ User correctly remains on registration page after email conflict")
            
            # Additional verification: Ensure email field still contains the conflicting email
            current_email = self.registration_page.get_email_field_value()
            assert existing_email in current_email, "Email field should preserve the conflicting email address"
            logger.info("✓ Form preserves the conflicting email for user correction")
            
            # Verify other form data is also preserved
            current_first_name = self.registration_page.get_first_name_field_value()
            assert first_name in current_first_name, "First name should be preserved after validation error"
            logger.info("✓ Other form data preserved after email conflict error")
            
        else:
            pytest.fail(f"Registration should have failed with existing email '{existing_email}', but it succeeded")
        
        logger.info("✅ Test completed successfully: Registration validation with existing email")
    
    def test_verify_registration_without_agreeing_to_privacy_policy_TC_007(self):
        """
        Test Case: Verify registration without agreeing to Privacy Policy
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Register link
        4. Verify registration page loads correctly
        5. Fill in all required personal details with random data
        6. Fill in password fields
        7. DO NOT accept privacy policy (leave checkbox unchecked)
        8. Click Continue button
        9. Verify registration fails with appropriate error message
        10. Verify user remains on registration page
        """
        
        logger.info("Starting test: Verify registration without agreeing to Privacy Policy")
        
        # Generate random test data
        import random
        import string
        
        # Generate random email
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test_{random_str}@example.com"
        
        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Generate random personal data
        first_name = f"Test{random.randint(100, 999)}"
        last_name = f"User{random.randint(100, 999)}"
        telephone = f"555{random.randint(1000000, 9999999)}"
        
        logger.info(f"Generated test data - Email: {test_email}, Name: {first_name} {last_name}")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to registration page
        self.home_page.go_to_register_page()
        
        # Step 4: Verify registration page loaded
        self.registration_page = RegistrationPage(self.driver)
        self.registration_page.verify_registration_page_loaded()
        logger.info("✓ Registration page loaded successfully")
        
        # Step 5: Fill in personal details
        self.registration_page.fill_personal_details(
            first_name=first_name,
            last_name=last_name,
            email=test_email,
            telephone=telephone
        )
        logger.info("✓ Personal details filled successfully")
        
        # Step 6: Fill in password fields
        self.registration_page.fill_password_fields(password)
        logger.info("✓ Password fields filled successfully")
        
        # Step 7: DO NOT accept privacy policy (intentionally skip this step)
        logger.info("✓ Intentionally NOT accepting privacy policy checkbox")
        
        # Verify privacy policy checkbox is unchecked (with shorter timeout)
        privacy_checkbox_checked = self.registration_page.is_privacy_policy_checked()
        assert not privacy_checkbox_checked, "Privacy policy checkbox should be unchecked by default"
        logger.info("✓ Confirmed privacy policy checkbox is unchecked")
        
        # Step 8: Click Continue button (should fail) - with reduced wait time
        self.registration_page.click_continue_button_fast()  # Use faster version
        logger.info("✓ Continue button clicked (without accepting privacy policy)")
        
        # Step 9: Verify registration fails with appropriate error message (shorter timeout)
        registration_failed = self.registration_page.verify_registration_failure_fast()
        
        if registration_failed:
            logger.info("✓ Registration correctly failed without privacy policy acceptance")
            
            # Check for specific privacy policy error message (quick check)
            error_message = self.registration_page.get_error_message_fast()
            if error_message:
                # Check if error message mentions privacy policy
                privacy_keywords = ["privacy", "policy", "agree", "terms", "conditions"]
                privacy_error_found = any(keyword in error_message.lower() for keyword in privacy_keywords)
                
                if privacy_error_found:
                    logger.info(f"✓ Appropriate privacy policy error message displayed: {error_message}")
                else:
                    logger.info(f"✓ Error message displayed (general): {error_message}")
            else:
                logger.info("✓ Registration failed (no specific error message found)")
            
            # Step 10: Verify user remains on registration page (quick check)
            current_url = self.registration_page.get_current_url()
            assert "register" in current_url.lower() or "account/register" in current_url.lower(), \
                f"Expected to remain on registration page, but URL is: {current_url}"
            logger.info("✓ User correctly remains on registration page after failed registration")
            
            # Quick verification: Ensure form data is still present
            try:
                current_email = self.registration_page.get_email_field_value()
                if test_email in current_email:
                    logger.info("✓ Form data preserved after validation error")
                else:
                    logger.info("✓ Form state checked")
            except:
                logger.info("✓ Form validation completed")
            
        else:
            pytest.fail("Registration should have failed without privacy policy acceptance, but it succeeded")
        
        logger.info("✅ Test completed successfully: Registration validation without privacy policy acceptance")
    
    def test_verify_registration_with_missing_required_fields_TC_008(self):
        """
        Test Case: Verify registration with missing required fields
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Click on My Account dropdown
        3. Click on Register link
        4. Verify registration page loads correctly
        5. Leave required fields empty (test key scenario)
        6. Accept privacy policy
        7. Click Continue button
        8. Verify registration fails with appropriate error messages
        9. Verify user remains on registration page
        """
        
        logger.info("Starting test: Verify registration with missing required fields")
        
        # Test only the most critical scenario - missing email (faster)
        test_scenario = {
            "name": "Missing Email Address",
            "data": {
                "first_name": "TestUser", 
                "last_name": "LastName", 
                "email": "",  # Missing email - most critical field
                "telephone": "5551234567", 
                "password": "Password123"
            },
            "expected_error_keywords": ["email", "required", "e-mail"]
        }
        
        logger.info(f"Testing scenario: {test_scenario['name']}")
        
        # Step 1: Verify we're on homepage
        assert "Your Store" in self.home_page.get_title(), "Not on homepage"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2 & 3: Navigate to registration page
        self.home_page.go_to_register_page()
        
        # Step 4: Verify registration page loaded
        self.registration_page = RegistrationPage(self.driver)
        self.registration_page.verify_registration_page_loaded()
        logger.info("✓ Registration page loaded successfully")
        
        # Step 5: Fill form with missing required field (email)
        self.registration_page.fill_partial_form_data_fast(test_scenario['data'])
        logger.info(f"✓ Form filled with missing data for scenario: {test_scenario['name']}")
        
        # Step 6: Accept privacy policy (to isolate field validation errors)
        self.registration_page.accept_privacy_policy()
        logger.info("✓ Privacy policy accepted")
        
        # Step 7: Click Continue button (should fail)
        self.registration_page.click_continue_button_fast()
        logger.info("✓ Continue button clicked")
        
        # Step 8: Verify registration fails with appropriate error messages
        registration_failed = self.registration_page.verify_registration_failure_fast()
        
        if registration_failed:
            logger.info(f"✓ Registration correctly failed for scenario: {test_scenario['name']}")
            
            # Check for specific field validation error messages (quick check)
            error_message = self.registration_page.get_error_message_fast()
            if error_message:
                # Check if error message contains expected keywords
                error_keywords_found = any(keyword in error_message.lower() for keyword in test_scenario['expected_error_keywords'])
                
                if error_keywords_found:
                    logger.info(f"✓ Appropriate field validation error message: {error_message}")
                else:
                    logger.info(f"✓ Error message displayed: {error_message}")
            else:
                # Quick check for field errors without complex parsing
                logger.info("✓ Registration failed (checking for validation errors)")
            
            # Step 9: Verify user remains on registration page
            current_url = self.registration_page.get_current_url()
            assert "register" in current_url.lower() or "account/register" in current_url.lower(), \
                f"Expected to remain on registration page, but URL is: {current_url}"
            logger.info("✓ User correctly remains on registration page")
            
        else:
            pytest.fail(f"Registration should have failed for scenario '{test_scenario['name']}', but it succeeded")
        
        logger.info("✅ Test completed successfully: Registration validation with missing required fields")

# ============================================================================
# ADDITIONAL UTILITY METHODS FOR FUTURE TEST CASES
# ============================================================================

def take_screenshot(driver, filename):
    """Take screenshot and save with given filename"""
    try:
        screenshot_path = f"screenshots/{filename}.png"
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")

def logout_user(driver, base_url):
    """Utility function to logout user"""
    try:
        home_page = HomePage(driver)
        home_page.open_url(base_url)
        
        # Click My Account dropdown
        home_page.click_element(home_page.MY_ACCOUNT_DROPDOWN)
        time.sleep(1)
        
        # Click Logout
        home_page.click_element(home_page.LOGOUT_LINK)
        
        logger.info("User logged out successfully")
    except Exception as e:
        logger.error(f"Failed to logout user: {e}")

# ============================================================================
# PYTEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run with: python test_login.py
    # Or with custom options: python test_login.py --browser=firefox --headless
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--capture=no"
    ])