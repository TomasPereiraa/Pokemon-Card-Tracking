import time
import random

def setup_driver():
    from seleniumbase import Driver
    driver = Driver(uc=True)
    return driver

def get_cardmarket_prices(driver, url):
    try:
        driver.uc_open_with_reconnect(url, reconnect_time=4)

        try:
            driver.uc_gui_click_captcha()
        except Exception:
            pass

        time.sleep(random.uniform(1.5, 2.5))

        try:
            trend_el = driver.find_element(
                "xpath",
                "//dt[contains(text(), 'Price Trend')]/following-sibling::dd/span"
            )
            trend_price = trend_el.text
        except Exception:
            trend_price = "Not Found"

        try:
            avg_el = driver.find_element(
                "xpath",
                "//dt[contains(text(), '30-days average price')]/following-sibling::dd/span"
            )
            avg_30_price = avg_el.text
        except Exception:
            avg_30_price = "Not Found"

        time.sleep(random.uniform(0.8, 1.5))

        return {"Trend Price": trend_price, "30-Day Avg Price": avg_30_price}

    except Exception as e:
        print(f"[scraper] Error fetching {url}: {e}")
        return {"Trend Price": "Error", "30-Day Avg Price": "Error"}