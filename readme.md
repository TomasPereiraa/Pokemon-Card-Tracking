# Pokémon Card Price Tracker

A command-line tool that scrapes current market prices from Cardmarket for a list of Pokémon cards, saves the results to CSV, and tracks price history over time.

***

## Requirements

- Python 3.10+
- Google Chrome installed
- Dependencies listed in `requirements.txt`

***

## First-Time Setup

### For non-technical users

1. Install Python 3.10+ from https://www.python.org/downloads/
   - During installation, check **"Add Python to PATH"** before clicking Install
2. Run `install.bat` — this sets up everything automatically
3. Run `run.bat` whenever you want to check prices

### For developers

    pip install -r requirements.txt

***

## Usage

### Via `run.bat` (Windows)

Double-click `run.bat` or run it from the terminal. If no CSV file is passed as an argument, a file picker dialog will open automatically.

    run.bat [path\to\cards.csv]

### Via Python directly

    python main.py path\to\cards.csv [output.csv]

If no output path is provided, the result is saved as `<input>_updated_<date>.csv` next to the input file.

***

## Input Format

The input CSV must use `;` as the delimiter and include a `URL` column with valid Cardmarket product links.

    URL
    https://www.cardmarket.com/en/Pokemon/Products/Singles/Scarlet-Obsidian-Flames/Charizard-ex
    https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Pikachu

***

## Output

- **Updated CSV** — original data with `Trend Price` and `30-Day Avg Price` columns added, plus a `TOTAL` row at the bottom
- **`data/price_history.json`** — cumulative daily price log per card, used by the visualizer

***

## Performance

The scraper runs multiple browsers in parallel to speed up large lists. You can adjust the number of workers at the top of `main.py`:

    NUM_WORKERS = 5       # Number of parallel browsers
    STAGGER_DELAY = 8     # Seconds between each worker starting

Recommended values:

- 2 workers — safest, slowest
- 5 workers — good balance, tested and working
- 10 workers — fastest, higher chance of Cloudflare flagging

If you start getting flagged, reduce `NUM_WORKERS` to 2 and increase `STAGGER_DELAY` to 12.

***

## Price History Visualizer

Run `visualizer.py` separately to plot price trends from the history file.

    python visualizer.py

Commands at the prompt:

- Type a card name to search and plot its price history
- Type `total` to see the total collection value over time
- Type `exit` to quit

***

## Notes

- Cardmarket uses Cloudflare bot protection. The scraper uses SeleniumBase UC mode to handle this automatically. Keep all browser windows visible while it runs — minimizing them can break the bot challenge.
- Prices are scraped in EUR (€).
- Only one entry per card per day is stored in the history file.
