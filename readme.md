# 🃏 Pokémon Card Price Tracker

A Windows desktop tool that automatically scrapes **Cardmarket** prices for your Pokémon card collection, tracks price history over time, and visualizes trends through an interactive CLI-based chart viewer.

---

## ✨ Features

- **Parallel scraping** — runs up to 5 browser workers simultaneously to fetch prices fast
- **Price history tracking** — stores daily Trend Price and 30-Day Average per card in a local JSON file
- **Duplicate-aware** — correctly handles multiple copies of the same card (quantity tracking)
- **Interactive visualizer** — CLI-based chart viewer with multiple display modes
- **Chart export** — save any chart as a high-resolution PNG to the `charts/` folder
- **One-click launchers** — `.bat` scripts for install, run, and visualize — no terminal knowledge needed

---

## 📋 Requirements

- Windows 10/11
- [Python 3.10+](https://www.python.org/downloads/) *(mark "Add Python to PATH" during install)*
- [Google Chrome](https://www.google.com/chrome/)

> Python dependencies are installed automatically by `install.bat`.

---

## 🚀 Getting Started

### 1. Install

Double-click `install.bat`. It will:
- Verify Python and Chrome are installed
- Create a local virtual environment (`venv/`)
- Install all dependencies from `requirements.txt`

### 2. Prepare your CSV

Create a `.csv` file (semicolon-separated) with at least a `URL` column containing Cardmarket card links:

```csv
URL
https://www.cardmarket.com/en/Pokemon/Products/Singles/Scarlet-Violet/Pikachu-ex
https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Charizard
```

### 3. Run the scraper

Double-click `run.bat` and select your CSV file via the file picker dialog.

The tool will:
- Scrape Trend Price and 30-Day Average for each card
- Append today's data to `data/price_history.json`
- Save an updated CSV as `<original_name>_updated_<date>.csv`

### 4. Visualize

Double-click `visualizer.bat` to open the interactive chart viewer.

---

## 📊 Visualizer Commands

| Command | Description |
|---|---|
| `list` | List all cards in history (duplicates shown separately) |
| `total` | Plot total collection value over time |
| `top [N]` | Bar chart of top N most valuable cards (default: 10) |
| `compare card1 card2` | Overlay price trends of multiple cards |
| `<card name>` | Plot price history for a specific card |
| `save <card name>` | Save a card chart as PNG |
| `save total` | Save total collection chart as PNG |
| `save top [N]` | Save top N bar chart as PNG |
| `help` | Show all available commands |
| `exit` | Quit the visualizer |

---

## 📁 Project Structure

```
├── main.py           # Scraper entry point — orchestrates workers and history updates
├── scraper.py        # SeleniumBase driver and Cardmarket price extraction logic
├── utils.py          # CSV/JSON helpers and URL parsing
├── visualizer.py     # Interactive CLI chart viewer (matplotlib)
├── run.bat           # One-click scraper launcher with file picker
├── visualizer.bat    # One-click visualizer launcher
├── install.bat       # Automated installer (venv + dependencies)
├── requirements.txt  # Python dependencies
└── data/
    └── price_history.json   # Auto-generated price history database
```

---

## 🛠️ Dependencies

| Package | Version | Purpose |
|---|---|---|
| `pandas` | ~2.2.3 | CSV loading and data manipulation |
| `seleniumbase` | ~4.34.4 | Headless browser scraping with CAPTCHA bypass |
| `matplotlib` | ~3.10.1 | Price history charts and visualizations |

---

## ⚙️ How It Works

1. `run.bat` passes your CSV to `main.py`, which splits card URLs across **5 parallel browser workers** (staggered by 12 seconds each to avoid bot detection).
2. Each worker uses **SeleniumBase in undetected-Chrome mode** (`uc=True`) to bypass Cardmarket's CAPTCHA.
3. Prices are extracted via XPath from the Cardmarket product page and written back into the CSV and `price_history.json`.
4. The visualizer reads `price_history.json` and renders interactive matplotlib charts on demand.

---

## 📌 Notes

- The scraper uses random delays between requests to reduce detection risk.
- Cards with the same URL in your CSV are only scraped **once** — prices are reused for duplicates.
- Price history entries are keyed as `CardName|SetName` for unambiguous tracking.

---

## 📄 License

MIT License — free to use, modify, and distribute.
