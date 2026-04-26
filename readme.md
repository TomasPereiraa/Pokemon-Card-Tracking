# Pokémon Card Price Tracker

A Windows desktop tool that automatically scrapes **Cardmarket** and **PSA** prices for your Pokémon card collection, tracks price history over time, and visualizes trends through an interactive CLI-based chart viewer.

---

## Features

- **Parallel scraping** — runs up to 5 browser workers simultaneously to fetch prices fast
- **Cardmarket prices** — scrapes Trend Price and 30-Day Average per card in EUR
- **PSA integration** — scrapes PSA certificate pages for grade, estimate (USD→EUR) and full card metadata
- **Price history tracking** — stores daily Cardmarket and PSA prices per card in a local JSON file
- **Variant-aware tracking** — distinguishes cards by language, condition, and reverse holo status
- **Duplicate-aware** — correctly handles multiple copies of the same card (quantity tracking)
- **USD→EUR conversion** — configurable exchange rate via `USD_TO_EUR_RATE` environment variable
- **Interactive visualizer** — CLI-based chart viewer with separate raw and PSA display modes
- **Chart export** — save any chart as a high-resolution PNG to the `charts/` folder
- **Failed cards export** — cards with missing prices are saved to a separate `failed_cards_<date>.csv`
- **One-click launchers** — `.bat` scripts for install, run, and visualize — no terminal knowledge needed

---

## Requirements

- Windows 10/11
- [Python 3.10+](https://www.python.org/downloads/) *(mark "Add Python to PATH" during install)*
- [Google Chrome](https://www.google.com/chrome/)

> Python dependencies are installed automatically by `install.bat`.

---

## Getting Started

### 1. Install

Double-click `install.bat`. It will:
- Verify Python and Chrome are installed
- Create a local virtual environment (`venv/`)
- Install all dependencies from `requirements.txt`

### 2. Prepare your CSV

Create a `.csv` file (semicolon-separated) with at least a `URL` column containing Cardmarket card links.

Optionally, add a `PSA URL` column with PSA certificate links to also track graded card values:

```csv
URL;PSA URL
https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Charizard;https://www.psacard.com/cert/120996877/
https://www.cardmarket.com/en/Pokemon/Products/Singles/Scarlet-Violet/Pikachu-ex;
```

URLs can include query parameters for variant filtering:

| Parameter | Example | Description |
|---|---|---|
| `language` | `?language=7` | Filter by language (7 = Japanese) |
| `isReverseHolo` | `?isReverseHolo=Y` | Reverse holo variant |
| `minCondition` | `?minCondition=2` | Minimum condition (2 = Near Mint) |

### 3. Run the scraper

Double-click `run.bat` and select your CSV file via the file picker dialog.

The tool will:
- Scrape Trend Price and 30-Day Average for each card from Cardmarket
- Scrape PSA estimate (USD), grade, and metadata for each PSA certificate URL
- Append today's data to `data/price_history.json`
- Save an updated CSV as `<original_name>_updated_<date>.csv`
- Save a `failed_cards_<date>.csv` if any cards had missing price data

### 4. Visualize

Double-click `visualizer.bat` to open the interactive chart viewer.

---

## Visualizer Commands

### Listing Cards

| Command | Description |
|---|---|
| `list` | List all raw and PSA cards separately |
| `list raw` | List only raw Cardmarket cards |
| `list psa` | List only PSA graded cards |

### Charts

| Command | Description |
|---|---|
| `total` | Plot raw, PSA (converted), and combined total in EUR over time |
| `top [N]` | Bar chart of top N cards by EUR value (raw + PSA combined, default: 10) |
| `top raw [N]` | Top N raw Cardmarket cards by EUR value |
| `top psa [N]` | Top N PSA graded cards by EUR value |
| `raw <card name>` | Plot Cardmarket price history for a specific card |
| `psa <card name>` | Plot PSA estimate history for a specific card (converted to EUR) |
| `compare <card1> <card2>` | Overlay price trends of multiple cards |

### Saving Charts

| Command | Description |
|---|---|
| `save total` | Save total collection chart as PNG |
| `save top [N]` | Save combined top N chart as PNG |
| `save top raw [N]` | Save raw top N chart as PNG |
| `save top psa [N]` | Save PSA top N chart as PNG |
| `save raw <card name>` | Save raw card chart as PNG |
| `save psa <card name>` | Save PSA card chart as PNG |

### Other

| Command | Description |
|---|---|
| `help` | Show all available commands and current USD→EUR rate |
| `exit` | Quit the visualizer |

---

## Project Structure

```
├── main.py              # Scraper entry point — orchestrates workers and history updates
├── scraper.py           # SeleniumBase driver, Cardmarket and PSA scraping logic
├── utils.py             # CSV/JSON helpers, URL parsing, and card key building
├── visualizer.py        # Interactive CLI chart viewer (matplotlib)
├── run.bat              # One-click scraper launcher with file picker
├── visualizer.bat       # One-click visualizer launcher
├── install.bat          # Automated installer (venv + dependencies)
├── requirements.txt     # Python dependencies
└── data/
    └── price_history.json   # Auto-generated price history database
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `pandas` | ~2.2.3 | CSV loading and data manipulation |
| `seleniumbase` | ~4.34.4 | Headless browser scraping with CAPTCHA bypass |
| `matplotlib` | ~3.10.1 | Price history charts and visualizations |

---

## How It Works

1. `run.bat` passes your CSV to `main.py`, which splits card URLs across **parallel browser workers** (staggered by 12 seconds each to avoid bot detection).
2. Each worker uses **SeleniumBase in undetected-Chrome mode** (`uc=True`) to bypass Cardmarket's CAPTCHA and PSA's bot protection.
3. **Cardmarket prices** (Trend Price + 30-Day Average in EUR) are extracted via XPath from each product page.
4. **PSA certificates** are also scraped when a `PSA URL` column is present — extracting the PSA Estimate (USD), grade, year, subject, and other metadata.
5. All data is written back to the CSV and to `data/price_history.json` using a unique card key (`CardName|SetName|lang=...|reverse=...|psa=<cert>`).
6. The visualizer reads `price_history.json` and renders interactive matplotlib charts on demand, with PSA values converted from USD to EUR using the configured rate.

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `USD_TO_EUR_RATE` | `0.92` | Exchange rate used to convert PSA USD estimates to EUR in the visualizer |
| `NUM_WORKERS` | `5` | Maximum number of parallel browser workers |
| `STAGGER_DELAY` | `12` | Seconds between each worker starting (reduces bot detection) |

**Example (Windows CMD):**
```cmd
set USD_TO_EUR_RATE=0.90
visualizer.bat
```

---

## Notes

- The scraper uses random delays between requests to reduce detection risk.
- Cards with the same Cardmarket URL are only scraped **once** — prices are reused for duplicates.
- Cards are tracked by a composite key `CardName|SetName|lang=X|condition=X|reverse=Y|psa=<cert>` — ensuring different variants and graded copies are stored separately.
- PSA certificate metadata (grade, year, subject, brand) is stored in history and shown in the visualizer labels.
- Cards with no valid Cardmarket or PSA price are exported to `failed_cards_<date>.csv` for review.

---

## License

MIT License — free to use, modify, and distribute.
