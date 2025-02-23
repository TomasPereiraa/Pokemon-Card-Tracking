import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup undetected ChromeDriver
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # Hide Selenium automation
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start undetected ChromeDriver (not headless, but minimized)
driver = uc.Chrome(options=options)
driver.minimize_window()  # Minimize the browser window

# CSV file location
csv_file = r"C:\Users\tomas\Downloads\pokemons_cards.csv"

# Load CSV file
df = pd.read_csv(csv_file, encoding="utf-8", sep=";")

# Ensure the CSV file has a 'URL' column
if "URL" not in df.columns:
    raise ValueError("❌ The CSV file must have a 'URL' column with Cardmarket links.")

# Function to fetch card prices
def get_cardmarket_prices(url):
    try:
        driver.get(url)
        time.sleep(3)  # Wait for Cloudflare verification to complete

        # Extract Trend Price
        try:
            trend_price = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(text(), 'Price Trend')]/following-sibling::dd/span"))
            ).text
        except:
            trend_price = "Not Found"

        # Extract 30-Day Avg Price
        try:
            avg_30_price = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(text(), '30-days average price')]/following-sibling::dd/span"))
            ).text
        except:
            avg_30_price = "Not Found"

        return {"Trend Price": trend_price, "30-Day Avg Price": avg_30_price}

    except Exception as e:
        return {"Trend Price": "Error", "30-Day Avg Price": "Error"}

# Fetch prices for each card URL
df["Trend Price"] = ""
df["30-Day Avg Price"] = ""

for index, row in df.iterrows():
    url = row["URL"]
    print(f"📢 Fetching prices for: {url}...")

    prices = get_cardmarket_prices(url)

    df.at[index, "Trend Price"] = prices["Trend Price"]
    df.at[index, "30-Day Avg Price"] = prices["30-Day Avg Price"]

# Save updated data to CSV
output_file = r"C:\Users\tomas\Downloads\updated_pokemons_cards.csv"
df.to_csv(output_file, index=False, encoding="utf-8", sep=";")

print(f"\n✅ Updated prices saved to '{output_file}'!")

# Close the browser
driver.quit()
