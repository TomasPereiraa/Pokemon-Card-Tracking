# Pokemon Card Price Tracker

This Python script automates the process of **fetching Pokémon card prices** from **Cardmarket** and saves them into a CSV file.  
It uses **Selenium with undetected_chromedriver** to bypass Cloudflare protection and extract **Trend Price** and **30-Day Avg Price**.

## 🚀 Features
✔ **Fetches live prices from Cardmarket**  
✔ **Bypasses Cloudflare protection** using `undetected_chromedriver`  
✔ **Saves prices into a CSV file**  
✔ **Automatically calculates the total Trend Price & 30-Day Avg Price**  
✔ **Runs minimized so it doesn’t interrupt your workflow**  
✔ **Extracts Pokémon name and set from the URL**  
✔ **Computes the sum of all Trend Price & 30-Day Avg Price**  

---

## 📌 **Installation**
### 1️⃣ Install Python Dependencies
Run the following command to install the required Python packages:
```sh
pip install pandas undetected-chromedriver selenium
```

### 2️⃣ Ensure You Have **Google Chrome**
The script requires **Google Chrome** installed on your system.

### 3️⃣ Download & Setup ChromeDriver
The script automatically downloads the correct version of **ChromeDriver** using `undetected_chromedriver`.

---

## 🛠 **How to Use**
### 1️⃣ **Prepare Your CSV File**
- Save a CSV file named **`pokemons_cards.csv`** in `C:\Users\NAME\Downloads\`
- The CSV should contain one column:
  ```csv
  URL
  https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Giratina-VSTAR-CRZGG69
  https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Arceus-VSTAR-CRZGG70
  ```

### 2️⃣ **Run the Script**
Execute the script using:
```sh
python scraper.py
```

### 3️⃣ **Check Output**
After running, you’ll get:
- **Updated prices saved in** `C:\Users\NAME\Downloads\updated_pokemons_cards.csv`
- The final CSV file will contain:
  ```csv
  Pokemons;Set;URL;Trend Price;30-Day Avg Price
  Giratina VSTAR CRZGG69;Crown Zenith;https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Giratina-VSTAR-CRZGG69;232.3;244.37
  Arceus VSTAR CRZGG70;Crown Zenith;https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Arceus-VSTAR-CRZGG70;208.29;172.72
  ```
  
---

## ❓ Troubleshooting
### 🔹 Chrome Opens and Closes Automatically?
That’s normal. The script opens **a hidden Chrome session** to fetch prices and then closes it automatically.

### 🔹 Getting HTTP 429 (Rate Limit) Error?
Try increasing the `time.sleep(5)` delay in the script to **avoid hitting Cardmarket’s rate limit**.

---

## 💡 **Next Steps**
- ✅ Automate the script to run **daily** using Windows Task Scheduler
- ✅ Store historical data and analyze price trends
- ✅ Create a simple **dashboard** to visualize price changes
- ✅ Compute and display the total **Trend Price** and **30-Day Avg Price** for all fetched cards

