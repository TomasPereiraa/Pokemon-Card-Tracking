import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.minimize_window()
    return driver


def get_cardmarket_prices(driver, url):
    try:
        driver.get(url)
        time.sleep(5)

        try:
            trend_price = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//dt[contains(text(), 'Price Trend')]/following-sibling::dd/span"))
            ).text
        except:
            trend_price = "Not Found"

        try:
            avg_30_price = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//dt[contains(text(), '30-days average price')]/following-sibling::dd/span"))
            ).text
        except:
            avg_30_price = "Not Found"

        return {"Trend Price": trend_price, "30-Day Avg Price": avg_30_price}

    except Exception as e:
        return {"Trend Price": "Error", "30-Day Avg Price": "Error"}
