# Pokemon Card Price Tracker

This Python script automates the process of **fetching Pokémon card prices** from **Cardmarket** and saves them into a CSV file.  
It uses **Selenium with undetected_chromedriver** to bypass Cloudflare protection and extract **Trend Price** and **30-Day Avg Price**.

## 🚀 Features
✔ **Fetches live prices from Cardmarket**  
✔ **Bypasses Cloudflare protection** using `undetected_chromedriver`  
✔ **Saves prices into a CSV file**  
✔ **Automatically calculates total Trend Price & 30-Day Avg Price**  
✔ **Runs minimized so it doesn’t interrupt your workflow**  
✔ **Extracts Pokémon name and set from the URL**  
✔ **Stores historical price data in JSON (`data/price_history.json`)**  
✔ **Visualizes individual and total price history with Matplotlib**  

---

## 📌 **Installation**
### 1️⃣ Install Python Dependencies
Run the following command to install the required Python packages:
```sh
pip install pandas undetected-chromedriver selenium matplotlib
```

### 2️⃣ Ensure You Have **Google Chrome**
The script requires **Google Chrome** installed on your system.

### 3️⃣ Setup Data Directory
Create a `data` folder in your project root directory to store historical data:
```sh
mkdir data
```

## 📂 **CSV File Setup**

Save your Pokémon URLs to:

```csv
C:\Users\NAME\Downloads\pokemons_cards.csv
```

This CSV should have one column labeled `URL`:
```csv
URL
https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Giratina-VSTAR-CRZGG69
https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Arceus-VSTAR-CRZGG70
```

### 2️⃣ **Run the Script**

## 🚀 How to Run the Scripts

### ▶️ Fetch Prices and Update History
Run `main.py` to fetch prices and update your CSV and historical data:
```sh
python main.py
```

- Prices will be saved in:
```text
C:\Users\NAME\Downloads\updated_pokemons_cards.csv
```
- Historical price data stored in:
```text
data/price_history.json
```

---

## 📈 Visualize Price Trends

### 📊 Visualize Historical Prices
You can visualize historical price changes using the provided visualizer script:
```sh
python visualizer.py
```

- Search using partial or full card names.
- See the historical trends visually.
- Visualize total collection price changes by typing `total`.

---

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

## 🖥 **How to Use (Standalone .EXE Version)**
### 1️⃣ **Convert the Script to `.exe`**
To make a standalone `.exe` that does not require Python, follow these steps:

#### ✅ Install PyInstaller
Make sure you have PyInstaller installed by running:
```sh
pip install pyinstaller
```

#### ✅ Create the `.exe`
Run this command inside the folder where your `gui_scraper.py` file is located:
```sh
pyinstaller --onefile --noconsole --hidden-import pandas --hidden-import selenium gui_scraper.py
```
✔ `--onefile` → Creates a **single .exe file**  
✔ `--noconsole` → Hides the **black terminal window**  
✔ `--hidden-import pandas --hidden-import selenium` → Ensures all dependencies are included  
![image](https://github.com/user-attachments/assets/d9314416-ac3f-4ff2-aa0c-c029ae2a4a35)
![image](https://github.com/user-attachments/assets/1cba677c-6072-4d0a-ace8-cfc11de8daba)

#### ✅ Find the `.exe`
After PyInstaller finishes, go to:
```
C:\Pokemon-Card-Tracking-main\dist\
```
You will find:
```
gui_scraper.exe
```

### 2️⃣ **Package and Send to Friends**
- **Create a new folder** (e.g., `PokemonScraperApp`).  
- **Move `gui_scraper.exe` into the folder**.  
- **Right-click the folder → Compress to ZIP**.  
- **Send the `.zip` file** via Google Drive, Discord, or WeTransfer.  

### 3️⃣ **How Your Friends Can Use the App**
1. **Unzip the file** into a folder.  
2. **Double-click `gui_scraper.exe`** to run it.  
3. **Upload their CSV file** when prompted.  
4. **Wait for the updated CSV to be saved in the same folder**.  

---

## ❓ Troubleshooting
### 🔹 Chrome Opens and Closes Automatically?
That’s normal. The script opens **a hidden Chrome session** to fetch prices and then closes it automatically.

### 🔹 Getting HTTP 429 (Rate Limit) Error?
Try increasing the `time.sleep(5)` delay in the script to **avoid hitting Cardmarket’s rate limit**.

### 🔹 `.exe` Doesn’t Work on Another PC?
Ensure your friend has **Google Chrome installed**. The `.exe` uses Chrome to fetch prices.

---

## 💡 **Next Steps**
## 🚀 Features Roadmap
- ✅ Fetch historical data to analyze price trends
- ✅ Visualize historical price trends graphically
- ✅ Autocomplete-like partial card name searching
- ✅ Compute and visualize total **Trend Price** and **30-Day Avg Price**
- ✅ Schedule automatic daily price updates using Windows Task Scheduler
