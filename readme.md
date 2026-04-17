# Pokémon Card Price Tracker

A Python tool that automatically fetches live Pokémon card prices from [Cardmarket](https://www.cardmarket.com), stores historical data, and generates visual price charts — all with a simple double-click.

## Features

- **Live price scraping** — fetches Trend Price and 30-Day Average Price directly from Cardmarket
- **Cloudflare bypass** — uses `seleniumbase` to reliably avoid bot detection
- **Parallel scraping** — runs multiple browsers simultaneously for faster results
- **Price history** — stores all fetched prices in a local JSON file for trend tracking
- **Collection valuation** — automatically calculates the total value of your collection
- **Price visualizer** — interactive charts for individual cards, total value, and top rankings
- **No-code setup** — includes `.bat` launchers for install, run, and visualize

## Requirements

- [Python 3.10+](https://www.python.org/downloads/) — tick **"Add Python to PATH"** during installation
- [Google Chrome](https://www.google.com/chrome/)

> All Python dependencies are installed automatically by `install.bat`.

## Getting Started

### 1. Install

Double-click `install.bat`. It will:
- Detect your Python installation
- Create an isolated virtual environment (`venv/`)
- Install all required packages automatically

### 2. Prepare your CSV

Create a `.csv` file with a single column named `URL`, one Cardmarket card URL per line:

```csv
URL
https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Giratina-VSTAR-CRZGG69
https://www.cardmarket.com/en/Pokemon/Products/Singles/Crown-Zenith/Arceus-VSTAR-CRZGG70
```

### 3. Fetch prices

Double-click `run.bat` and select your CSV file when prompted.

The output will be saved as `<your_file>_updated_<date>.csv` in the same folder:

```csv
Pokemons;Set;URL;Trend Price;30-Day Avg Price
Giratina VSTAR CRZGG69;Crown Zenith;https://...;232.30;244.37
Arceus VSTAR CRZGG70;Crown Zenith;https://...;208.29;172.72
```

### 4. Visualize

Double-click `visualizer.bat` to open the interactive chart interface.

## Visualizer Commands

| Command | Description |
|---|---|
| `list` | List all cards in history |
| `total` | Plot total collection value over time |
| `top [N]` | Bar chart of the top N most valuable cards |
| `compare <card1> <card2>` | Compare price trends across multiple cards |
| `save <card>` | Save a chart as a PNG image |
| `save total` | Save the total collection chart as PNG |
| `save top [N]` | Save the top N chart as PNG |
| `<card name>` | Search and plot a specific card |
| `exit` | Quit the visualizer |

Charts are saved to the `charts/` folder.

## Project Structure

```
├── main.py               # Entry point — orchestrates scraping workers
├── scraper.py            # Selenium scraper for Cardmarket
├── utils.py              # CSV/JSON helpers and URL parsing
├── visualizer.py         # Interactive price chart interface
├── requirements.txt      # Python dependencies
├── install.bat           # One-click installer
├── run.bat               # One-click price fetcher
├── visualizer.bat        # One-click chart launcher
└── data/
    └── price_history.json  # Accumulated price history (auto-generated)
```
