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


# Extract Pokémon name and set from URL
def extract_name_set(url):
    parts = url.rstrip("/").split("/")

    # Ensure the URL has enough parts
    if len(parts) < 6:
        return "Unknown", "Unknown"

    set_name = parts[-2].replace("-", " ").title()  # Extract correct set name
    card_name = parts[-1].replace("-", " ")  # Extract card name

    return card_name, set_name


# Apply extraction function to the DataFrame
df[["Pokemons", "Set"]] = df["URL"].apply(lambda x: pd.Series(extract_name_set(x)))


# Function to fetch card prices
def get_cardmarket_prices(url):
    try:
        driver.get(url)
        time.sleep(5)  # Wait for Cloudflare verification to complete

        # Extract Trend Price
        try:
            trend_price = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//dt[contains(text(), 'Price Trend')]/following-sibling::dd/span"))
            ).text
        except:
            trend_price = "Not Found"

        # Extract 30-Day Avg Price
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


# Fetch prices for each card URL
df["Trend Price"] = ""
df["30-Day Avg Price"] = ""

for index, row in df.iterrows():
    url = row["URL"]
    print(f"📢 Fetching prices for: {url}...")

    prices = get_cardmarket_prices(url)

    df.at[index, "Trend Price"] = prices["Trend Price"]
    df.at[index, "30-Day Avg Price"] = prices["30-Day Avg Price"]

# Convert Trend Price & 30-Day Avg Price to numeric values
df["Trend Price"] = df["Trend Price"].str.replace(" €", "").str.replace(",", ".").astype(str)
df["30-Day Avg Price"] = df["30-Day Avg Price"].str.replace(" €", "").str.replace(",", ".").astype(str)

# Compute total sums
try:
    df["Trend Price"] = pd.to_numeric(df["Trend Price"], errors="coerce")  # Convert to float
    df["30-Day Avg Price"] = pd.to_numeric(df["30-Day Avg Price"], errors="coerce")  # Convert to float
    total_trend_price = df["Trend Price"].sum()
    total_avg_30_price = df["30-Day Avg Price"].sum()
except Exception as e:
    total_trend_price, total_avg_30_price = "Error", "Error"

# Append total row
total_row = pd.DataFrame([["Total", "", "", total_trend_price, total_avg_30_price]], columns=df.columns)
df = pd.concat([df, total_row], ignore_index=True)

# Save updated data to CSV
output_file = r"C:\Users\tomas\Downloads\updated_pokemons_cards.csv"
df.to_csv(output_file, index=False, encoding="utf-8", sep=";")

print(f"\n✅ Updated prices saved to '{output_file}'!")

# Close the browser
driver.quit()
