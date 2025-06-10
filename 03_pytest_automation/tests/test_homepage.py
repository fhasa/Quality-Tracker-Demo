"""
OpenCart Automation Test Suite - Homepage Elements Test Cases
Tests for top bar elements and header elements
"""

import pytest
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

# ============================================================================
# TEST CASES
# ============================================================================

class TestHomepageElements:
    """Test cases for homepage elements"""
    
    def test_verify_all_top_bar_elements_visibility_TC_009(self, driver):
        """
        Test Case: Verify All Top Bar Elements are found on the homepage
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Check if Currency dropdown is found
        3. Check if Contact Phone is found
        4. Check if My Account dropdown is found
        5. Check if Wish List link is found
        6. Check if Shopping Cart button is found
        7. Check if Checkout link is found
        """
        
        logger.info("Starting test: Verify All Top Bar Elements are found")
        
        # Step 1: Navigate to homepage
        driver.get(BASE_URL)
        logger.info(f"Navigated to: {BASE_URL}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Verify we're on the correct page
        assert "Your Store" in driver.title, f"Expected 'Your Store' in title, got: {driver.title}"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2: Check Currency dropdown
        currency_selectors = [
            "//button[contains(text(), '$') or contains(text(), 'Currency')]",
            "//button[contains(@class, 'dropdown-toggle')]",
            "//*[contains(text(), 'Currency')]"
        ]
        currency_found = False
        for selector in currency_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info("✓ Currency dropdown found")
                currency_found = True
                break
            except TimeoutException:
                continue
        
        if not currency_found:
            logger.error("✗ Currency dropdown not found")
        
        # Step 3: Check Contact Phone
        phone_selectors = [
            "//i[contains(@class, 'fa-phone')]",
            "//*[contains(text(), '123456789')]",
            "//i[@class='fa fa-phone']"
        ]
        phone_found = False
        for selector in phone_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info("✓ Contact Phone found")
                phone_found = True
                break
            except TimeoutException:
                continue
        
        if not phone_found:
            logger.error("✗ Contact Phone not found")
        
        # Step 4: Check My Account dropdown
        account_selectors = [
            "//a[@title='My Account' or contains(text(), 'My Account')]",
            "//a[contains(text(), 'Account')]",
            "//*[@title='My Account']"
        ]
        account_found = False
        for selector in account_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info("✓ My Account dropdown found")
                account_found = True
                break
            except TimeoutException:
                continue
        
        if not account_found:
            logger.error("✗ My Account dropdown not found")
        
        # Step 5: Check Wish List link
        wishlist_selectors = [
            "//a[@title='Wish List' or contains(text(), 'Wish List')]",
            "//a[contains(text(), 'Wishlist')]",
            "//*[@title='Wish List']"
        ]
        wishlist_found = False
        for selector in wishlist_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info("✓ Wish List link found")
                wishlist_found = True
                break
            except TimeoutException:
                continue
        
        if not wishlist_found:
            logger.error("✗ Wish List link not found")
        
        # Step 6: Check Shopping Cart button
        cart_selectors = [
            "//button[@title='Shopping Cart' or contains(text(), 'Shopping Cart')]",
            "//button[contains(text(), 'Cart')]",
            "//a[contains(text(), 'Shopping Cart')]",
            "//*[@title='Shopping Cart']"
        ]
        cart_found = False
        for selector in cart_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info("✓ Shopping Cart button found")
                cart_found = True
                break
            except TimeoutException:
                continue
        
        if not cart_found:
            logger.error("✗ Shopping Cart button not found")
        
        # Step 7: Check Checkout link
        checkout_selectors = [
            "//a[contains(text(), 'Checkout')]",
            "//button[contains(text(), 'Checkout')]",
            "//*[contains(text(), 'Checkout')]"
        ]
        checkout_found = False
        for selector in checkout_selectors:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info("✓ Checkout link found")
                checkout_found = True
                break
            except TimeoutException:
                continue
        
        if not checkout_found:
            logger.error("✗ Checkout link not found")
        
        # Assertions
        assert currency_found, "Currency dropdown should be found on the homepage"
        assert phone_found, "Contact Phone should be found on the homepage"
        assert account_found, "My Account dropdown should be found on the homepage"
        assert wishlist_found, "Wish List link should be found on the homepage"
        assert cart_found, "Shopping Cart button should be found on the homepage"
        assert checkout_found, "Checkout link should be found on the homepage"
        
        # Final verification
        all_elements_found = all([
            currency_found,
            phone_found,
            account_found,
            wishlist_found,
            cart_found,
            checkout_found
        ])
        
        assert all_elements_found, "All top bar elements should be found"
        
        logger.info("✅ All top bar elements found successfully:")
        logger.info("   - Currency Dropdown: ✓ Found")
        logger.info("   - Contact Phone: ✓ Found")
        logger.info("   - My Account: ✓ Found")
        logger.info("   - Wish List: ✓ Found")
        logger.info("   - Shopping Cart: ✓ Found")
        logger.info("   - Checkout: ✓ Found")
        logger.info("✅ Test completed successfully")
    
    def test_verify_header_elements_TC_010(self, driver):
        """
        Test Case: Verify Header Contains Logo, Search Bar, Navigation Menu, and Cart Summary
        
        Steps:
        1. Navigate to OpenCart homepage
        2. Check if Logo (Your Store) is found
        3. Check if Search Bar (input field) is found
        4. Check if Search Button is found
        5. Check if Navigation Menu container is found
        6. Check if Cart Summary is found
        """
        
        logger.info("Starting test: Verify Header Elements are found")
        
        # Step 1: Navigate to homepage
        driver.get(BASE_URL)
        logger.info(f"Navigated to: {BASE_URL}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Verify we're on the correct page
        assert "Your Store" in driver.title, f"Expected 'Your Store' in title, got: {driver.title}"
        logger.info("✓ Homepage loaded successfully")
        
        # Step 2: Check Logo (Your Store)
        logo_selectors = [
            "//h1//a[contains(text(), 'Your Store')]",
            "//*[contains(text(), 'Your Store')]",
            "//a[@title='Your Store']",
            "#logo"
        ]
        logo_found = False
        for selector in logo_selectors:
            try:
                if selector.startswith("//") or selector.startswith("/"):
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info("✓ Logo (Your Store) found")
                logo_found = True
                break
            except TimeoutException:
                continue
        
        if not logo_found:
            logger.error("✗ Logo (Your Store) not found")
        
        # Step 3: Check Search Bar (input field)
        search_input_selectors = [
            "//input[@name='search']",
            "//input[@placeholder='Search']",
            "//input[contains(@class, 'form-control')]",
            "input[name='search']"
        ]
        search_input_found = False
        for selector in search_input_selectors:
            try:
                if selector.startswith("//") or selector.startswith("/"):
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info("✓ Search input field found")
                search_input_found = True
                break
            except TimeoutException:
                continue
        
        if not search_input_found:
            logger.error("✗ Search input field not found")
        
        # Step 4: Check Search Button
        search_button_selectors = [
            "//button[contains(@class, 'btn') and contains(@class, 'btn-default')]",
            "//button[@type='button']",
            "//i[@class='fa fa-search']",
            ".btn.btn-default"
        ]
        search_button_found = False
        for selector in search_button_selectors:
            try:
                if selector.startswith("//") or selector.startswith("/"):
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info("✓ Search button found")
                search_button_found = True
                break
            except TimeoutException:
                continue
        
        if not search_button_found:
            logger.error("✗ Search button not found")
        
        # Step 5: Check Navigation Menu container
        nav_menu_selectors = [
            "//nav[contains(@class, 'navbar')]",
            "//div[contains(@class, 'navbar')]",
            "//ul[contains(@class, 'nav')]",
            ".navbar"
        ]
        nav_menu_found = False
        for selector in nav_menu_selectors:
            try:
                if selector.startswith("//") or selector.startswith("/"):
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info("✓ Navigation menu container found")
                nav_menu_found = True
                break
            except TimeoutException:
                continue
        
        if not nav_menu_found:
            logger.error("✗ Navigation menu container not found")
        
        # Step 6: Check Cart Summary
        cart_summary_selectors = [
            "//button[contains(text(), 'item')]",
            "//button[contains(text(), '$')]",
            "//*[contains(text(), '0 item') or contains(text(), 'item(s)')]",
            ".btn.btn-inverse"
        ]
        cart_summary_found = False
        for selector in cart_summary_selectors:
            try:
                if selector.startswith("//") or selector.startswith("/"):
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                logger.info("✓ Cart summary found")
                cart_summary_found = True
                break
            except TimeoutException:
                continue
        
        if not cart_summary_found:
            logger.error("✗ Cart summary not found")
        
        # Assertions
        assert logo_found, "Logo (Your Store) should be found on the homepage"
        assert search_input_found, "Search input field should be found on the homepage"
        assert search_button_found, "Search button should be found on the homepage"
        assert nav_menu_found, "Navigation menu container should be found on the homepage"
        assert cart_summary_found, "Cart summary should be found on the homepage"
        
        # Final verification
        all_header_elements_found = all([
            logo_found,
            search_input_found,
            search_button_found,
            nav_menu_found,
            cart_summary_found
        ])
        
        assert all_header_elements_found, "All header elements should be found"
        
        logger.info("✅ All header elements found successfully:")
        logger.info("   - Logo (Your Store): ✓ Found")
        logger.info("   - Search Input Field: ✓ Found")
        logger.info("   - Search Button: ✓ Found")
        logger.info("   - Navigation Menu Container: ✓ Found")
        logger.info("   - Cart Summary: ✓ Found")
        logger.info("✅ Test completed successfully")

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