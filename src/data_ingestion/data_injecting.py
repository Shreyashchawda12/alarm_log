import streamlit as st
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to initialize the driver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Function to wait for elements
def wait_for_element(driver, locator, timeout=20, condition=EC.presence_of_element_located):
    return WebDriverWait(driver, timeout).until(condition(locator))

# Function to log element details
def log_element_info(element, description):
    try:
        logging.info(f"{description}: Displayed: {element.is_displayed()}, Enabled: {element.is_enabled()}, "
                     f"Location: {element.location}, Size: {element.size}")
    except Exception as e:
        logging.error(f"Error logging element info: {e}")

# Main function to execute the script
def run_selenium_script():
    driver = setup_driver()
    try:
        logging.info("Opening login page.")
        driver.get("https://vnoc.atctower.in/vnoc/Default.aspx")

        logging.info("Filling in login form.")
        wait_for_element(driver, (By.NAME, 'appLogin$UserName')).send_keys('MH_jitendra_Sahoo')
        driver.find_element(By.NAME, 'appLogin$Password').send_keys('Welcome@Atc')
        driver.find_element(By.NAME, 'appLogin$LoginImageButton').click()

        logging.info("Waiting for post-login page.")
        wait_for_element(driver, (By.ID, 'ctl00_Html1'))

        logging.info("Navigating to secured page.")
        driver.get('https://vnoc.atctower.in/vnoc/aspx/TroubleTicketLogDetail.aspx')
        wait_for_element(driver, (By.ID, 'aspnetForm'))

        logging.info("Waiting for 'Loading...' overlay to disappear.")
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(),'Loading....')]"))
        )

        logging.info("Locating the grid menu button.")
        grid_menu_button = wait_for_element(driver, 
            (By.CSS_SELECTOR, "div[role='button'][id*='grid-menu']"), condition=EC.element_to_be_clickable)
        log_element_info(grid_menu_button, "Grid menu button")

        logging.info("Clicking the grid menu button.")
        ActionChains(driver).move_to_element(grid_menu_button).click().perform()

        logging.info("Waiting for the grid menu to become visible.")
        wait_for_element(driver, (By.CSS_SELECTOR, ".ui-grid-menu"), condition=EC.visibility_of_element_located)

        logging.info("Collecting grid menu features.")
        features = driver.find_elements(By.CSS_SELECTOR, ".ui-grid-menu .menu-item")
        for feature in features:
            logging.info(f"Feature found: {feature.text}")

        # Save screenshot to BytesIO
        screenshot_io = BytesIO(driver.get_screenshot_as_png())
        return screenshot_io

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        driver.save_screenshot('error.png')
        logging.info("Saved screenshot as 'error.png'.")
        screenshot_io = BytesIO(open('error.png', 'rb').read())  # Fallback to error screenshot
        return screenshot_io

    finally:
        logging.info("Closing browser.")
        driver.quit()

