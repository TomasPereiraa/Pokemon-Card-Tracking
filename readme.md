# Pokémon Card Price Tracker

A command-line tool that scrapes current market prices from Cardmarket for a list of Pokémon cards, saves the results to CSV, and tracks price history over time.

***

## Requirements

- Python 3.10+
- Google Chrome installed
- Dependencies listed in `requirements.txt`

Install dependencies by running:

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

***

## Output

- **Updated CSV** — original data with `Trend Price` and `30-Day Avg Price` columns added, plus a `TOTAL` row at the bottom
- **`data/price_history.json`** — cumulative daily price log per card, used by the visualizer

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

- Cardmarket uses Cloudflare protection. The scraper uses SeleniumBase UC mode, which handles the bot challenge automatically. Keep the browser window visible while it runs.
- Prices are scraped in EUR (€).
- Only one entry per card per day is stored in the history file.
