from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Optional: run in headless mode if not debugging
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment for headless mode

# Path to your chromedriver executable using webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)

def log_element_info(element, description):
    """Logs basic information about the element."""
    try:
        logging.info(f"{description}:")
        logging.info(f" - Displayed: {element.is_displayed()}")
        logging.info(f" - Enabled: {element.is_enabled()}")
        logging.info(f" - Location: {element.location}")
        logging.info(f" - Size: {element.size}")
    except Exception as e:
        logging.error(f"Error logging element info: {e}")

try:
    logging.info("Opening login page.")
    driver.get("https://vnoc.atctower.in/vnoc/Default.aspx")

    logging.info("Filling in login form.")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'appLogin$UserName'))
    ).send_keys('MH_jitendra_Sahoo')
    driver.find_element(By.NAME, 'appLogin$Password').send_keys('Welcome@Atc')

    logging.info("Submitting login form.")
    driver.find_element(By.NAME, 'appLogin$LoginImageButton').click()

    logging.info("Waiting for post-login page.")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'ctl00_Html1'))
    )

    logging.info("Navigating to secured page.")
    driver.get('https://vnoc.atctower.in/vnoc/aspx/TroubleTicketLogDetail.aspx')

    logging.info("Waiting for target page to fully load.")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'aspnetForm'))
    )

    # Wait for the "Loading..." overlay to disappear
    logging.info("Waiting for 'Loading...' overlay to disappear.")
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(),'Loading....')]"))
    )

    logging.info("Locating the grid menu button.")
    try:
        grid_menu_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='button'][id*='grid-menu']"))
        )

        # Log information about the element
        log_element_info(grid_menu_button, "Grid menu button")

        # Ensure the element is clickable
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][id*='grid-menu']"))
        )

        # Using ActionChains to ensure the element is in view and can be interacted with
        logging.info("Attempting to hover and click the grid menu button.")
        actions = ActionChains(driver)
        actions.move_to_element(grid_menu_button).perform()  # Move to the element first
        actions.click(grid_menu_button).perform()  # Then click

        # If regular click fails, try clicking via JavaScript
        if not grid_menu_button.is_displayed():
            logging.info("Attempting to click via JavaScript as a fallback.")
            driver.execute_script("arguments[0].click();", grid_menu_button)

        logging.info("Waiting for the grid menu to be visible.")
        grid_menu = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-grid-menu"))
        )

        logging.info("Grid menu is visible.")

        # Collect all features present in the grid menu
        logging.info("Collecting features from the grid menu.")
        features = driver.find_elements(By.CSS_SELECTOR, ".ui-grid-menu .menu-item")
        for feature in features:
            feature_name = feature.text
            logging.info(f"Feature found: {feature_name}")

    except Exception as e:
        logging.error(f"Error interacting with grid menu button: {e}")
        driver.save_screenshot('grid_menu_error_screenshot.png')  # Save screenshot on error
        logging.info("Screenshot saved as 'grid_menu_error_screenshot.png'.")

except Exception as e:
    logging.error(f"An error occurred: {e}")
    logging.info("Current URL: %s", driver.current_url)
    logging.info("Page Source Length: %d", len(driver.page_source))

    # Take a screenshot to debug the issue
    driver.save_screenshot('error_screenshot.png')
    logging.info("Screenshot saved as 'error_screenshot.png'.")

finally:
    logging.info("Closing browser.")
    driver.quit()
