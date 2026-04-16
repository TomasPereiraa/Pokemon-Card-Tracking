"""
Command-line entry point for the Pokémon Card Price Tracker.

Usage:
    python main.py [output.csv]

Examples:
    python main.py my_cards.csv
    python main.py my_cards.csv updated_cards.csv

If no output file is given, the result is saved as _updated_<date>.csv
next to the input file.
"""

import sys
import os
import time
import random
import multiprocessing
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "data", "price_history.json")

from utils import extract_name_set, load_csv, save_csv, load_price_history, save_price_history
from scraper import setup_driver, get_cardmarket_prices

NUM_WORKERS = 5          # Number of parallel browsers — keep at 2 to stay under Cloudflare radar
STAGGER_DELAY = 12       # Seconds between each worker starting up

def worker(worker_id, rows, result_dict, stagger_delay):
    """Each worker runs its own browser and scrapes its chunk of cards."""
    # Stagger startup so browsers don't all hit Cardmarket at the same time
    time.sleep(worker_id * stagger_delay)

    driver = setup_driver()
    try:
        for index, row in rows:
            print(f"  [Worker {worker_id}] [{index + 1}] {row['Pokemons']} ({row['Set']})")
            prices = get_cardmarket_prices(driver, row["URL"])
            result_dict[index] = prices
            print(f"  [Worker {worker_id}] Trend: {prices['Trend Price']} | 30-Day Avg: {prices['30-Day Avg Price']}")
    finally:
        driver.quit()

def run(csv_path: str, output_path: str | None = None) -> None:
    print(f"\n📂 Loading: {csv_path}")
    df = load_csv(csv_path)
    df[["Pokemons", "Set"]] = df["URL"].apply(lambda x: pd.Series(extract_name_set(x)))
    df["Trend Price"] = ""
    df["30-Day Avg Price"] = ""

    today_str = datetime.today().strftime("%Y-%m-%d")
    price_history = load_price_history(HISTORY_FILE)

    total = len(df)
    print(f"🔍 {total} cards found. Starting {NUM_WORKERS} browsers...\n")

    # Split card list into chunks, one per worker
    rows = list(df.iterrows())
    chunks = [rows[i::NUM_WORKERS] for i in range(NUM_WORKERS)]

    manager = multiprocessing.Manager()
    result_dict = manager.dict()

    processes = []
    for worker_id, chunk in enumerate(chunks):
        if not chunk:
            continue
        p = multiprocessing.Process(
            target=worker,
            args=(worker_id, chunk, result_dict, STAGGER_DELAY)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Write results back to dataframe
    for index, prices in result_dict.items():
        df.at[index, "Trend Price"] = prices["Trend Price"]
        df.at[index, "30-Day Avg Price"] = prices["30-Day Avg Price"]

    # Update price history
    for index, row in df.iterrows():
        card_key = f"{row['Pokemons']}|{row['Set']}"
        entries = price_history.setdefault(card_key, [])
        trend_raw = str(row["Trend Price"]).replace(" €", "").replace(",", ".")
        avg_raw = str(row["30-Day Avg Price"]).replace(" €", "").replace(",", ".")
        if not any(e["date"] == today_str for e in entries):
            entries.append({
                "date": today_str,
                "trend_price": trend_raw,
                "avg_30_price": avg_raw,
            })

    df["Trend Price"] = pd.to_numeric(
        df["Trend Price"].astype(str).str.replace(" €", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df["30-Day Avg Price"] = pd.to_numeric(
        df["30-Day Avg Price"].astype(str).str.replace(" €", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )

    trend_sum = round(df["Trend Price"].sum(), 2)
    avg_sum = round(df["30-Day Avg Price"].sum(), 2)

    total_values = {col: "" for col in df.columns}
    total_values["Pokemons"] = "TOTAL"
    total_values["Trend Price"] = trend_sum
    total_values["30-Day Avg Price"] = avg_sum
    df = pd.concat([df, pd.DataFrame([total_values])], ignore_index=True)

    if output_path is None:
        base = os.path.splitext(csv_path)[0]
        output_path = f"{base}_updated_{today_str}.csv"

    save_csv(df, output_path)

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    save_price_history(price_history, HISTORY_FILE)

    print(f"\n✅ Saved to: {output_path}")
    print(f"📊 Trend total: {trend_sum:.2f} €")
    print(f"📊 30-Day total: {avg_sum:.2f} €")
    print(f"📁 History saved: {HISTORY_FILE}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.isfile(csv_path):
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)

    run(csv_path, output_path)
