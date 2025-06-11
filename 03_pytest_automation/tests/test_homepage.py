# ============================================================================
# BASE PAGE CLASS
# ============================================================================

import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.short_wait = WebDriverWait(driver, 3)
    
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    
    def find_element_with_multiple_selectors(self, selectors, wait_time=3):
        """
        Try multiple selectors to find an element
        Returns tuple: (element_found: bool, element: WebElement or None)
        """
        wait = WebDriverWait(self.driver, wait_time)
        
        for selector_type, selector_value in selectors:
            try:
                element = wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                return True, element
            except TimeoutException:
                continue
        
        return False, None
    
    def is_element_present_multiple_selectors(self, selectors, element_name):
        """Check if element is present using multiple selectors with logging"""
        found, element = self.find_element_with_multiple_selectors(selectors)
        if found:
            logger.info(f"✓ {element_name} found")
        else:
            logger.error(f"✗ {element_name} not found")
        return found
    
    def get_page_title(self):
        """Get current page title"""
        return self.driver.title
    
    def navigate_to(self, url):
        """Navigate to specified URL"""
        self.driver.get(url)
        logger.info(f"Navigated to: {url}")
        self.wait_for_page_load()

# ============================================================================
# HOMEPAGE PAGE OBJECT
# ============================================================================

class HomePage(BasePage):
    """Page Object for OpenCart Homepage"""
    
    def __init__(self, driver, base_url):
        super().__init__(driver)
        self.base_url = base_url
        
        # Top Bar Element Selectors
        self.currency_selectors = [
            (By.XPATH, "//button[contains(text(), '$') or contains(text(), 'Currency')]"),
            (By.XPATH, "//button[contains(@class, 'dropdown-toggle')]"),
            (By.XPATH, "//*[contains(text(), 'Currency')]")
        ]
        
        self.phone_selectors = [
            (By.XPATH, "//i[contains(@class, 'fa-phone')]"),
            (By.XPATH, "//*[contains(text(), '123456789')]"),
            (By.XPATH, "//i[@class='fa fa-phone']")
        ]
        
        self.my_account_selectors = [
            (By.XPATH, "//a[@title='My Account' or contains(text(), 'My Account')]"),
            (By.XPATH, "//a[contains(text(), 'Account')]"),
            (By.XPATH, "//*[@title='My Account']")
        ]
        
        self.wishlist_selectors = [
            (By.XPATH, "//a[@title='Wish List' or contains(text(), 'Wish List')]"),
            (By.XPATH, "//a[contains(text(), 'Wishlist')]"),
            (By.XPATH, "//*[@title='Wish List']")
        ]
        
        self.shopping_cart_selectors = [
            (By.XPATH, "//button[@title='Shopping Cart' or contains(text(), 'Shopping Cart')]"),
            (By.XPATH, "//button[contains(text(), 'Cart')]"),
            (By.XPATH, "//a[contains(text(), 'Shopping Cart')]"),
            (By.XPATH, "//*[@title='Shopping Cart']")
        ]
        
        self.checkout_selectors = [
            (By.XPATH, "//a[contains(text(), 'Checkout')]"),
            (By.XPATH, "//button[contains(text(), 'Checkout')]"),
            (By.XPATH, "//*[contains(text(), 'Checkout')]")
        ]
        
        # Header Element Selectors
        self.logo_selectors = [
            (By.XPATH, "//h1//a[contains(text(), 'Your Store')]"),
            (By.XPATH, "//*[contains(text(), 'Your Store')]"),
            (By.XPATH, "//a[@title='Your Store']"),
            (By.CSS_SELECTOR, "#logo")
        ]
        
        self.search_input_selectors = [
            (By.XPATH, "//input[@name='search']"),
            (By.XPATH, "//input[@placeholder='Search']"),
            (By.XPATH, "//input[contains(@class, 'form-control')]"),
            (By.CSS_SELECTOR, "input[name='search']")
        ]
        
        self.search_button_selectors = [
            (By.XPATH, "//button[contains(@class, 'btn') and contains(@class, 'btn-default')]"),
            (By.XPATH, "//button[@type='button']"),
            (By.XPATH, "//i[@class='fa fa-search']"),
            (By.CSS_SELECTOR, ".btn.btn-default")
        ]
        
        self.nav_menu_selectors = [
            (By.XPATH, "//nav[contains(@class, 'navbar')]"),
            (By.XPATH, "//div[contains(@class, 'navbar')]"),
            (By.XPATH, "//ul[contains(@class, 'nav')]"),
            (By.CSS_SELECTOR, ".navbar")
        ]
        
        self.cart_summary_selectors = [
            (By.XPATH, "//button[contains(text(), 'item')]"),
            (By.XPATH, "//button[contains(text(), '$')]"),
            (By.XPATH, "//*[contains(text(), '0 item') or contains(text(), 'item(s)')]"),
            (By.CSS_SELECTOR, ".btn.btn-inverse")
        ]
    
    # Navigation Methods
    def open(self):
        """Open the homepage"""
        self.navigate_to(self.base_url)
        return self
    
    def verify_page_loaded(self):
        """Verify homepage is loaded correctly"""
        assert "Your Store" in self.get_page_title(), f"Expected 'Your Store' in title, got: {self.get_page_title()}"
        logger.info("✓ Homepage loaded successfully")
        return True
    
    # Top Bar Element Methods
    def is_currency_dropdown_present(self):
        """Check if currency dropdown is present"""
        return self.is_element_present_multiple_selectors(
            self.currency_selectors, "Currency dropdown"
        )
    
    def is_contact_phone_present(self):
        """Check if contact phone is present"""
        return self.is_element_present_multiple_selectors(
            self.phone_selectors, "Contact Phone"
        )
    
    def is_my_account_present(self):
        """Check if My Account dropdown is present"""
        return self.is_element_present_multiple_selectors(
            self.my_account_selectors, "My Account dropdown"
        )
    
    def is_wishlist_present(self):
        """Check if Wish List link is present"""
        return self.is_element_present_multiple_selectors(
            self.wishlist_selectors, "Wish List link"
        )
    
    def is_shopping_cart_present(self):
        """Check if Shopping Cart button is present"""
        return self.is_element_present_multiple_selectors(
            self.shopping_cart_selectors, "Shopping Cart button"
        )
    
    def is_checkout_present(self):
        """Check if Checkout link is present"""
        return self.is_element_present_multiple_selectors(
            self.checkout_selectors, "Checkout link"
        )
    
    def verify_all_top_bar_elements(self):
        """Verify all top bar elements are present"""
        results = {
            'currency': self.is_currency_dropdown_present(),
            'phone': self.is_contact_phone_present(),
            'my_account': self.is_my_account_present(),
            'wishlist': self.is_wishlist_present(),
            'shopping_cart': self.is_shopping_cart_present(),
            'checkout': self.is_checkout_present()
        }
        
        all_found = all(results.values())
        
        if all_found:
            logger.info("✅ All top bar elements found successfully:")
            logger.info("   - Currency Dropdown: ✓")
            logger.info("   - Contact Phone: ✓")
            logger.info("   - My Account: ✓")
            logger.info("   - Wish List: ✓")
            logger.info("   - Shopping Cart: ✓")
            logger.info("   - Checkout: ✓")
        
        return all_found, results
    
    # Header Element Methods
    def is_logo_present(self):
        """Check if logo is present"""
        return self.is_element_present_multiple_selectors(
            self.logo_selectors, "Logo (Your Store)"
        )
    
    def is_search_input_present(self):
        """Check if search input field is present"""
        return self.is_element_present_multiple_selectors(
            self.search_input_selectors, "Search input field"
        )
    
    def is_search_button_present(self):
        """Check if search button is present"""
        return self.is_element_present_multiple_selectors(
            self.search_button_selectors, "Search button"
        )
    
    def is_navigation_menu_present(self):
        """Check if navigation menu is present"""
        return self.is_element_present_multiple_selectors(
            self.nav_menu_selectors, "Navigation menu container"
        )
    
    def is_cart_summary_present(self):
        """Check if cart summary is present"""
        return self.is_element_present_multiple_selectors(
            self.cart_summary_selectors, "Cart summary"
        )
    
    def verify_all_header_elements(self):
        """Verify all header elements are present"""
        results = {
            'logo': self.is_logo_present(),
            'search_input': self.is_search_input_present(),
            'search_button': self.is_search_button_present(),
            'navigation_menu': self.is_navigation_menu_present(),
            'cart_summary': self.is_cart_summary_present()
        }
        
        all_found = all(results.values())
        
        if all_found:
            logger.info("✅ All header elements found successfully:")
            logger.info("   - Logo (Your Store): ✓")
            logger.info("   - Search Input Field: ✓")
            logger.info("   - Search Button: ✓")
            logger.info("   - Navigation Menu Container: ✓")
            logger.info("   - Cart Summary: ✓")
        
        return all_found, results
    
    # Action Methods (for future use)
    def click_my_account(self):
        """Click on My Account dropdown"""
        found, element = self.find_element_with_multiple_selectors(self.my_account_selectors)
        if found:
            element.click()
            logger.info("Clicked on My Account dropdown")
            return True
        return False
    
    def click_shopping_cart(self):
        """Click on Shopping Cart button"""
        found, element = self.find_element_with_multiple_selectors(self.shopping_cart_selectors)
        if found:
            element.click()
            logger.info("Clicked on Shopping Cart button")
            return True
        return False
    
    def search_product(self, search_term):
        """Search for a product"""
        found, search_input = self.find_element_with_multiple_selectors(self.search_input_selectors)
        if found:
            search_input.clear()
            search_input.send_keys(search_term)
            
            found_btn, search_button = self.find_element_with_multiple_selectors(self.search_button_selectors)
            if found_btn:
                search_button.click()
                logger.info(f"Searched for: {search_term}")
                return True
        return False

# ============================================================================
# UPDATED TEST FILE WITH POM
# ============================================================================

"""
OpenCart Automation Test Suite - Homepage Elements Test Cases (POM Version)
Tests for top bar elements and header elements using Page Object Model
"""

import pytest
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = os.getenv("BASE_URL", "https://demo.opencart.com.gr/")

# ============================================================================
# PYTEST FIXTURES
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
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
    elif browser.lower() == "firefox":
        firefox_options = FirefoxOptions()
        if headless or is_ci:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
    
    else:
        raise ValueError(f"Browser {browser} is not supported")
    
    if not is_ci:
        driver.maximize_window()
    
    yield driver
    
    logger.info("Closing driver")
    driver.quit()

@pytest.fixture(scope="function")
def homepage(driver):
    """Create HomePage instance"""
    return HomePage(driver, BASE_URL)

# ============================================================================
# TEST CASES USING POM
# ============================================================================

class TestHomepageElementsPOM:
    """Test cases for homepage elements using Page Object Model"""
    
    def test_verify_all_top_bar_elements_visibility_TC_009(self, homepage):
        """
        Test Case: Verify All Top Bar Elements are found on the homepage
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Verify all top bar elements are present
        """
        
        logger.info("Starting test: Verify All Top Bar Elements are found (POM)")
        
        # Step 1: Navigate to homepage and verify it loaded
        homepage.open()
        homepage.verify_page_loaded()
        
        # Step 2: Verify all top bar elements
        all_found, results = homepage.verify_all_top_bar_elements()
        
        # Individual assertions for better error reporting
        assert results['currency'], "Currency dropdown should be found on the homepage"
        assert results['phone'], "Contact Phone should be found on the homepage"
        assert results['my_account'], "My Account dropdown should be found on the homepage"
        assert results['wishlist'], "Wish List link should be found on the homepage"
        assert results['shopping_cart'], "Shopping Cart button should be found on the homepage"
        assert results['checkout'], "Checkout link should be found on the homepage"
        
        # Overall assertion
        assert all_found, "All top bar elements should be found"
        
        logger.info("✅ Test completed successfully")
    
    def test_verify_header_elements_TC_010(self, homepage):
        """
        Test Case: Verify Header Contains Logo, Search Bar, Navigation Menu, and Cart Summary
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Verify all header elements are present
        """
        
        logger.info("Starting test: Verify Header Elements are found (POM)")
        
        # Step 1: Navigate to homepage and verify it loaded
        homepage.open()
        homepage.verify_page_loaded()
        
        # Step 2: Verify all header elements
        all_found, results = homepage.verify_all_header_elements()
        
        # Individual assertions for better error reporting
        assert results['logo'], "Logo (Your Store) should be found on the homepage"
        assert results['search_input'], "Search input field should be found on the homepage"
        assert results['search_button'], "Search button should be found on the homepage"
        assert results['navigation_menu'], "Navigation menu container should be found on the homepage"
        assert results['cart_summary'], "Cart summary should be found on the homepage"
        
        # Overall assertion
        assert all_found, "All header elements should be found"
        
        logger.info("✅ Test completed successfully")
    
    def test_homepage_functionality_TC_011(self, homepage):
        """
        Test Case: Basic Homepage Functionality Test
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Verify page elements are present
        3. Test search functionality
        4. Test navigation clicks
        """
        
        logger.info("Starting test: Basic Homepage Functionality (POM)")
        
        # Step 1: Navigate and verify
        homepage.open()
        homepage.verify_page_loaded()
        
        # Step 2: Verify key elements are present
        assert homepage.is_logo_present(), "Logo should be present"
        assert homepage.is_search_input_present(), "Search input should be present"
        assert homepage.is_my_account_present(), "My Account should be present"
        
        # Step 3: Test search functionality
        search_success = homepage.search_product("laptop")
        assert search_success, "Search functionality should work"
        
        # Go back to homepage for next test
        homepage.open()
        
        # Step 4: Test My Account click
        account_click_success = homepage.click_my_account()
        assert account_click_success, "My Account click should work"
        
        logger.info("✅ Basic functionality test completed successfully")

# ============================================================================
# PYTEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--capture=no"
    ])