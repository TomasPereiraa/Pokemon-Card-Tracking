# Pokemon Card Price Tracker

This Python script automates the process of **fetching Pokémon card prices** from **Cardmarket** and saves them into a CSV file.  
It uses **Selenium with undetected_chromedriver** to bypass Cloudflare protection and extract **Trend Price** and **30-Day Avg Price**.

## 🚀 Features
✔ **Fetches live prices from Cardmarket**  
✔ **Bypasses Cloudflare protection** using `undetected_chromedriver`  
✔ **Saves prices into a CSV file**  
✔ **Automatically calculates the total Trend Price & 30-Day Avg Price**  
✔ **Runs minimized so it doesn’t interrupt your workflow**  
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
- Save a CSV file named **`pokemons_cards.csv`** in `C:\Users\tomas\Downloads\`
- The CSV should contain two columns:
  ```csv
  Pokemons;URL
  Giratina CZ;https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Giratina-VSTAR-CRZGG69
  Arceus CZ;https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Arceus-VSTAR-CRZGG70
  ```

### 2️⃣ **Run the Script**
Execute the script using:
```sh
python scraper.py
```

### 3️⃣ **Check Output**
After running, you’ll get:
- **Updated prices saved in** `C:\Users\tomas\Downloads\updated_pokemons_cards.csv`
- **Total Trend Price and 30-Day Avg Price printed in the terminal**

---

## 📊 **Output Example**
After running, the script will display:

```
📊 Total Trend Price: 447.56 €
📊 Total 30-Day Avg Price: 418.87 €
✅ Updated prices saved to 'C:\Users\tomas\Downloads\updated_pokemons_cards.csv'!
```

---

## ❓ Troubleshooting
### 🔹 Chrome Opens and Closes Automatically?
That’s normal. The script opens **a hidden Chrome session** to fetch prices and then closes it automatically.

### 🔹 Prices Show "Not Found"?
- Ensure your **Cardmarket URLs** are correct.
- Try increasing the `time.sleep(7)` value to **10 or 15 seconds** to allow more time for pages to load.

---

## 💡 **Next Steps**
- ✅ Automate the script to run **daily** using Windows Task Scheduler
- ✅ Store historical data and analyze price trends
- ✅ Create a simple **dashboard** to visualize price changes
- ✅ Compute and display the total **Trend Price** and **30-Day Avg Price** for all fetched cards

