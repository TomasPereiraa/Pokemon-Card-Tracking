import random
import re
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    from seleniumbase import Driver

    driver = Driver(uc=True)
    return driver


def wait_for_page_ready(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda current_driver: current_driver.execute_script("return document.readyState") == "complete"
    )


def parse_usd_price(text):
    """
    Converts strings like '$70.02', '$1,234.56', or '70.02' into a float.
    """

    if not text:
        return None

    match = re.search(r"\$?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", str(text))

    if not match:
        return None

    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


def get_cardmarket_prices(driver, url, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            driver.uc_open_with_reconnect(url, reconnect_time=4)

            try:
                driver.uc_gui_click_captcha()
            except Exception:
                pass

            wait_for_page_ready(driver)

            time.sleep(random.uniform(1.5, 2.5))

            try:
                trend_el = driver.find_element(
                    "xpath",
                    "//dt[contains(normalize-space(), 'Price Trend')]/following-sibling::dd[1]//span",
                )
                trend_price = trend_el.text.strip()
            except Exception:
                trend_price = "Not Found"

            try:
                avg_el = driver.find_element(
                    "xpath",
                    "//dt[contains(normalize-space(), '30-days average price')]/following-sibling::dd[1]//span",
                )
                avg_30_price = avg_el.text.strip()
            except Exception:
                avg_30_price = "Not Found"

            if trend_price != "Not Found" or avg_30_price != "Not Found":
                time.sleep(random.uniform(0.8, 1.5))

                return {
                    "Trend Price": trend_price,
                    "30-Day Avg Price": avg_30_price,
                }

            print(f"[Cardmarket] Attempt {attempt}/{max_attempts}: prices not found for {url}")

        except TimeoutException:
            print(f"[Cardmarket] Attempt {attempt}/{max_attempts}: page timeout for {url}")

        except Exception as error:
            print(f"[Cardmarket] Attempt {attempt}/{max_attempts} failed for {url}: {error}")

        time.sleep(random.uniform(2.0, 4.0))

    return {
        "Trend Price": "Error",
        "30-Day Avg Price": "Error",
    }


def get_empty_psa_info():
    return {
        "PSA Estimate USD": None,
        "PSA Cert Number": "",
        "PSA Item Grade": "",
        "PSA Year": "",
        "PSA Brand/Title": "",
        "PSA Subject": "",
        "PSA Card Number": "",
        "PSA Category": "",
        "PSA Variety/Pedigree": "",
    }


def extract_psa_detail_table(driver):
    """
    Extracts the PSA certificate detail table.

    Example labels:
    - Cert Number
    - Item Grade
    - Year
    - Brand/Title
    - Subject
    - Card Number
    - Category
    - Variety/Pedigree
    """

    details = {}

    try:
        rows = driver.find_elements("xpath", "//dl//div[.//dt and .//dd]")

        for row in rows:
            try:
                label = row.find_element("xpath", ".//dt").text.strip()
                value = row.find_element("xpath", ".//dd").text.strip()

                if label:
                    details[label] = value

            except NoSuchElementException:
                continue

    except Exception:
        pass

    return details


def extract_psa_estimate(driver):
    """
    Extracts the PSA Estimate dollar value.
    """

    xpaths = [
        "//*[contains(normalize-space(), 'PSA Estimate')]/ancestor::*[@role='group'][1]//*[contains(normalize-space(), '$')]",
        "//*[contains(normalize-space(), 'PSA Estimate')]/following::p[contains(normalize-space(), '$')][1]",
        "//*[contains(normalize-space(), 'PSA Estimate')]/following::*[contains(normalize-space(), '$')][1]",
    ]

    for xpath in xpaths:
        try:
            element = driver.find_element("xpath", xpath)
            text = element.text.strip()
            value = parse_usd_price(text)

            if value is not None:
                return value

        except NoSuchElementException:
            continue

    # Fallback: scan visible elements with dollar values.
    try:
        dollar_elements = driver.find_elements("xpath", "//*[contains(normalize-space(), '$')]")

        for element in dollar_elements:
            text = element.text.strip()
            value = parse_usd_price(text)

            if value is not None:
                return value

    except Exception:
        pass

    return None


def get_psa_card_info(driver, url, max_attempts=3):
    """
    Scrapes PSA certificate page data.

    Example:
    https://www.psacard.com/cert/120996877/

    Returns:
    - PSA Estimate USD
    - PSA Cert Number
    - PSA Item Grade
    - PSA Year
    - PSA Brand/Title
    - PSA Subject
    - PSA Card Number
    - PSA Category
    - PSA Variety/Pedigree
    """

    if not url or str(url).strip() == "":
        return get_empty_psa_info()

    url = str(url).strip()

    for attempt in range(1, max_attempts + 1):
        try:
            driver.uc_open_with_reconnect(url, reconnect_time=4)
            wait_for_page_ready(driver)

            time.sleep(random.uniform(2.0, 3.5))

            estimate_usd = extract_psa_estimate(driver)
            details = extract_psa_detail_table(driver)

            info = get_empty_psa_info()
            info["PSA Estimate USD"] = estimate_usd
            info["PSA Cert Number"] = details.get("Cert Number", "")
            info["PSA Item Grade"] = details.get("Item Grade", "")
            info["PSA Year"] = details.get("Year", "")
            info["PSA Brand/Title"] = details.get("Brand/Title", "")
            info["PSA Subject"] = details.get("Subject", "")
            info["PSA Card Number"] = details.get("Card Number", "")
            info["PSA Category"] = details.get("Category", "")
            info["PSA Variety/Pedigree"] = details.get("Variety/Pedigree", "")

            if estimate_usd is not None or info["PSA Subject"] or info["PSA Brand/Title"]:
                return info

            print(f"[PSA] Attempt {attempt}/{max_attempts}: PSA data not found for {url}")

        except TimeoutException:
            print(f"[PSA] Attempt {attempt}/{max_attempts}: page timeout for {url}")

        except Exception as error:
            print(f"[PSA] Attempt {attempt}/{max_attempts} failed for {url}: {error}")

        time.sleep(random.uniform(2.0, 4.0))

    return get_empty_psa_info()