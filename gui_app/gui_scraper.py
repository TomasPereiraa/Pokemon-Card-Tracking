import os
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Setup GUI
root = tk.Tk()
root.title("Pokémon Card Price Tracker")
root.geometry("500x400")

# GUI Elements
label = tk.Label(root, text="Upload your Pokémon CSV file:")
label.pack(pady=10)

log_box = tk.Text(root, height=10, width=50)
log_box.pack(pady=10)

def log_message(message):
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        start_scraping(file_path)

def extract_name_set(url):
    parts = url.rstrip("/").split("/")
    if len(parts) < 6:
        return "Unknown", "Unknown"
    set_name = parts[-2].replace("-", " ").title()
    card_name = parts[-1].replace("-", " ")
    return card_name, set_name

def get_cardmarket_prices(url, driver):
    try:
        driver.get(url)
        time.sleep(5)

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
    except:
        return {"Trend Price": "Error", "30-Day Avg Price": "Error"}

def start_scraping(file_path):
    def scrape():
        log_message("📢 Loading CSV file...")
        df = pd.read_csv(file_path, encoding="utf-8", sep=";")

        if "URL" not in df.columns:
            messagebox.showerror("Error", "The CSV file must have a 'URL' column.")
            return

        df[["Pokemons", "Set"]] = df["URL"].apply(lambda x: pd.Series(extract_name_set(x)))
        df["Trend Price"] = ""
        df["30-Day Avg Price"] = ""

        log_message("🚀 Starting browser...")
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options)
        driver.minimize_window()

        for index, row in df.iterrows():
            url = row["URL"]
            log_message(f"Fetching prices for: {url}...")
            prices = get_cardmarket_prices(url, driver)
            df.at[index, "Trend Price"] = prices["Trend Price"]
            df.at[index, "30-Day Avg Price"] = prices["30-Day Avg Price"]

        driver.quit()

        # Compute total sums
        try:
            df["Trend Price"] = df["Trend Price"].str.replace(" €", "").str.replace(",", ".").astype(float)
            df["30-Day Avg Price"] = df["30-Day Avg Price"].str.replace(" €", "").str.replace(",", ".").astype(float)

            total_trend_price = df["Trend Price"].sum()
            total_avg_30_price = df["30-Day Avg Price"].sum()

            # Format total prices
            total_trend_price = f"{total_trend_price:.2f} €"
            total_avg_30_price = f"{total_avg_30_price:.2f} €"
        except:
            total_trend_price, total_avg_30_price = "Error", "Error"

        # Append total row properly
        total_row = pd.DataFrame([["TOTAL", "", "SUM", total_trend_price, total_avg_30_price]], columns=df.columns)
        df = pd.concat([df, total_row], ignore_index=True)

        # Save the updated CSV
        output_file = os.path.join(os.path.dirname(file_path), "updated_pokemons_cards.csv")
        df.to_csv(output_file, index=False, encoding="utf-8-sig", sep=";")
        log_message(f"✅ Prices saved to {output_file}")
        messagebox.showinfo("Success", "Updated CSV file saved!")

    thread = threading.Thread(target=scrape)
    thread.start()

upload_button = tk.Button(root, text="Select CSV File", command=select_file)
upload_button.pack(pady=20)

root.mainloop()
