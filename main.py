"""
Command-line entry point for the Pokémon Card Price Tracker.

Usage:
python main.py <input.csv> [output.csv]

If no output file is given, the result is saved as <input>_updated_<date>.csv
next to the input file.
"""

import multiprocessing
import os
import re
import sys
import time
from datetime import datetime

import pandas as pd

from scraper import get_cardmarket_prices, get_psa_card_info, setup_driver
from utils import (
    build_card_key,
    extract_card_info,
    load_csv,
    load_price_history,
    parse_euro_price,
    save_csv,
    save_price_history,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "data", "price_history.json")

MAX_WORKERS = max(1, int(os.getenv("NUM_WORKERS", "5")))
STAGGER_DELAY = float(os.getenv("STAGGER_DELAY", "12"))

PSA_URL_COLUMNS = [
    "PSA URL",
    "PSA_URL",
    "PSA",
    "PSA Link",
    "PSA_LINK",
]

PSA_TEXT_COLUMNS = [
    "PSA Cert Number",
    "PSA Item Grade",
    "PSA Year",
    "PSA Brand/Title",
    "PSA Subject",
    "PSA Card Number",
    "PSA Category",
    "PSA Variety/Pedigree",
]


def clean_text_value(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def get_worker_count(total_items):
    """
    Returns the number of browsers to open.

    Logic:
    0 items       -> 0 workers
    1 to 10       -> 1 worker
    11 to 30      -> 2 workers
    31 to 60      -> 3 workers
    61+           -> 5 workers

    The result is always capped by:
    - MAX_WORKERS
    - total_items
    """

    if total_items <= 0:
        return 0

    if total_items <= 10:
        recommended_workers = 1
    elif total_items <= 30:
        recommended_workers = 2
    elif total_items <= 60:
        recommended_workers = 3
    else:
        recommended_workers = 5

    return min(MAX_WORKERS, recommended_workers, total_items)


def split_work_items(items, worker_count):
    if worker_count <= 0:
        return []

    return [items[i::worker_count] for i in range(worker_count)]


def find_psa_url_column(df):
    for column in PSA_URL_COLUMNS:
        if column in df.columns:
            return column

    return None


def extract_psa_cert_number(psa_url):
    """
    Extracts the PSA certificate number from URLs like:
    https://www.psacard.com/cert/120996877/
    """

    if not psa_url:
        return ""

    match = re.search(r"/cert/(\d+)", str(psa_url))

    if not match:
        return ""

    return match.group(1)


def is_valid_psa_url(value):
    if not value:
        return False

    value = str(value).strip()

    return value.startswith("https://www.psacard.com/cert/")


def initialize_psa_columns(df):
    """
    Creates PSA columns.

    PSA Estimate USD is numeric.
    The other PSA columns are text metadata from the certificate page.
    """

    df["PSA Estimate USD"] = pd.Series(
        [pd.NA] * len(df),
        index=df.index,
        dtype="Float64",
    )

    for column in PSA_TEXT_COLUMNS:
        df[column] = ""


def build_history_key(row, psa_url_column=None):
    """
    Builds the history key.

    It starts with the Cardmarket card key from utils.build_card_key().
    If the row has a PSA certificate, the PSA cert number is added.

    This prevents two graded cards of the same raw card from being mixed
    if they have different PSA certificates.
    """

    base_key = build_card_key(row)

    cert_number = clean_text_value(row.get("PSA Cert Number", ""))

    if not cert_number and psa_url_column:
        psa_url = clean_text_value(row.get(psa_url_column, ""))
        cert_number = extract_psa_cert_number(psa_url)

    if cert_number:
        return f"{base_key}|psa={cert_number}"

    return base_key


def worker(worker_id, rows, result_dict, stagger_delay):
    time.sleep(worker_id * stagger_delay)

    driver = setup_driver()

    try:
        for url, name, set_name in rows:
            print(f"[Worker {worker_id}] {name} ({set_name})")

            prices = get_cardmarket_prices(driver, url)
            result_dict[url] = prices

            print(
                f"[Worker {worker_id}] "
                f"Trend: {prices['Trend Price']} | "
                f"30-Day Avg: {prices['30-Day Avg Price']}"
            )

    finally:
        driver.quit()


def psa_worker(worker_id, rows, result_dict, stagger_delay):
    time.sleep(worker_id * stagger_delay)

    driver = setup_driver()

    try:
        for psa_url in rows:
            print(f"[PSA Worker {worker_id}] {psa_url}")

            psa_info = get_psa_card_info(driver, psa_url)
            result_dict[psa_url] = psa_info

            estimate = psa_info.get("PSA Estimate USD")
            subject = psa_info.get("PSA Subject", "")
            brand_title = psa_info.get("PSA Brand/Title", "")
            grade = psa_info.get("PSA Item Grade", "")

            if estimate is None:
                print(f"[PSA Worker {worker_id}] Estimate: Not Found")
            else:
                print(f"[PSA Worker {worker_id}] Estimate: ${estimate:.2f}")

            if subject or brand_title or grade:
                print(
                    f"[PSA Worker {worker_id}] "
                    f"{subject} | {brand_title} | {grade}"
                )

    finally:
        driver.quit()


def scrape_cardmarket_prices(df):
    total = len(df)

    unique_urls = df.drop_duplicates(subset="URL")[["URL", "Pokemons", "Set"]]
    duplicates = total - len(unique_urls)

    if duplicates > 0:
        print(f"Warning: {duplicates} duplicate Cardmarket URL(s) found. Will scrape once and reuse prices.")

    work_items = list(unique_urls.itertuples(index=False, name=None))
    worker_count = get_worker_count(len(work_items))

    print(f"{total} cards ({len(unique_urls)} unique Cardmarket URL(s)).")

    if worker_count == 0:
        print("No Cardmarket URLs to scrape.\n")
        return

    print(f"Starting {worker_count} Cardmarket browser worker(s). Max configured: {MAX_WORKERS}.\n")

    chunks = split_work_items(work_items, worker_count)

    manager = multiprocessing.Manager()
    result_dict = manager.dict()

    processes = []

    for worker_id, chunk in enumerate(chunks):
        if not chunk:
            continue

        process = multiprocessing.Process(
            target=worker,
            args=(worker_id, chunk, result_dict, STAGGER_DELAY),
        )

        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    for process in processes:
        if process.exitcode != 0:
            print(f"Warning: Cardmarket worker process {process.pid} exited with code {process.exitcode}")

    for index, row in df.iterrows():
        prices = result_dict.get(row["URL"])

        if prices:
            df.at[index, "Trend Price"] = prices["Trend Price"]
            df.at[index, "30-Day Avg Price"] = prices["30-Day Avg Price"]


def scrape_psa_estimates(df, psa_url_column):
    initialize_psa_columns(df)

    if not psa_url_column:
        print("No PSA URL column found. Skipping PSA estimates.")
        return

    df[psa_url_column] = df[psa_url_column].fillna("").astype(str).str.strip()

    psa_urls = [
        value
        for value in df[psa_url_column].drop_duplicates().tolist()
        if is_valid_psa_url(value)
    ]

    if not psa_urls:
        print("PSA column found, but no valid PSA certificate URLs were detected.")
        return

    worker_count = get_worker_count(len(psa_urls))

    print(f"\nFound {len(psa_urls)} unique PSA certificate URL(s).")

    if worker_count == 0:
        print("No PSA URLs to scrape.\n")
        return

    print(f"Starting {worker_count} PSA browser worker(s). Max configured: {MAX_WORKERS}.\n")

    chunks = split_work_items(psa_urls, worker_count)

    manager = multiprocessing.Manager()
    result_dict = manager.dict()

    processes = []

    for worker_id, chunk in enumerate(chunks):
        if not chunk:
            continue

        process = multiprocessing.Process(
            target=psa_worker,
            args=(worker_id, chunk, result_dict, STAGGER_DELAY),
        )

        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    for process in processes:
        if process.exitcode != 0:
            print(f"Warning: PSA worker process {process.pid} exited with code {process.exitcode}")

    for index, row in df.iterrows():
        psa_url = clean_text_value(row.get(psa_url_column, ""))

        if not psa_url:
            continue

        psa_info = result_dict.get(psa_url)

        if not psa_info:
            continue

        estimate = psa_info.get("PSA Estimate USD")

        if estimate is not None:
            df.at[index, "PSA Estimate USD"] = float(estimate)

        for column in PSA_TEXT_COLUMNS:
            df.at[index, column] = clean_text_value(psa_info.get(column, ""))


def update_price_history(df, price_history, today_str, psa_url_column=None):
    """
    Updates price_history.json.

    Cardmarket EUR prices are stored as before.
    PSA USD estimate and PSA metadata are also stored when available.
    """

    df["_card_key"] = df.apply(
        lambda row: build_history_key(row, psa_url_column),
        axis=1,
    )

    quantity_map = df["_card_key"].value_counts().to_dict()
    skipped_history_rows = 0

    for index, row in df.iterrows():
        card_key = row["_card_key"]

        trend_value = parse_euro_price(row["Trend Price"])
        avg_value = parse_euro_price(row["30-Day Avg Price"])
        psa_value = pd.to_numeric(row.get("PSA Estimate USD", pd.NA), errors="coerce")

        if pd.isna(psa_value):
            psa_value = None
        else:
            psa_value = float(psa_value)

        quantity = quantity_map.get(card_key, 1)

        if trend_value is None and avg_value is None and psa_value is None:
            skipped_history_rows += 1
            continue

        entry_data = {
            "date": today_str,
            "trend_price": trend_value,
            "avg_30_price": avg_value,
            "psa_estimate_usd": psa_value,
            "quantity": quantity,
            "psa_cert_number": clean_text_value(row.get("PSA Cert Number", "")),
            "psa_item_grade": clean_text_value(row.get("PSA Item Grade", "")),
            "psa_year": clean_text_value(row.get("PSA Year", "")),
            "psa_brand_title": clean_text_value(row.get("PSA Brand/Title", "")),
            "psa_subject": clean_text_value(row.get("PSA Subject", "")),
            "psa_card_number": clean_text_value(row.get("PSA Card Number", "")),
            "psa_category": clean_text_value(row.get("PSA Category", "")),
            "psa_variety_pedigree": clean_text_value(row.get("PSA Variety/Pedigree", "")),
        }

        entries = price_history.setdefault(card_key, [])

        existing = next((entry for entry in entries if entry["date"] == today_str), None)

        if existing:
            existing.update(entry_data)
        else:
            entries.append(entry_data)

    df.drop(columns=["_card_key"], inplace=True)

    if skipped_history_rows > 0:
        print(
            f"Warning: skipped {skipped_history_rows} row(s) from price history "
            "because no valid Cardmarket or PSA price was found."
        )


def convert_price_columns(df):
    df["Trend Price"] = pd.to_numeric(
        df["Trend Price"]
        .astype(str)
        .str.replace(" €", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )

    df["30-Day Avg Price"] = pd.to_numeric(
        df["30-Day Avg Price"]
        .astype(str)
        .str.replace(" €", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )

    df["PSA Estimate USD"] = pd.to_numeric(
        df["PSA Estimate USD"],
        errors="coerce",
    )


def export_failed_rows(df, output_path, today_str):
    failed_rows = df[
        df["Trend Price"].isna()
        | df["30-Day Avg Price"].isna()
    ].copy()

    if failed_rows.empty:
        return

    failed_path = os.path.join(
        os.path.dirname(os.path.abspath(output_path)),
        f"failed_cards_{today_str}.csv",
    )

    failed_rows.to_csv(
        failed_path,
        index=False,
        encoding="utf-8-sig",
        sep=";",
    )

    print(f"Warning: {len(failed_rows)} card(s) had missing Cardmarket price data.")
    print(f"Failed cards saved to: {failed_path}")


def run(csv_path: str, output_path: str | None = None) -> None:
    print(f"\nLoading: {csv_path}")

    df = load_csv(csv_path)

    card_info = df["URL"].apply(extract_card_info).apply(pd.Series)

    for column in card_info.columns:
        df[column] = card_info[column]

    df["Trend Price"] = ""
    df["30-Day Avg Price"] = ""
    initialize_psa_columns(df)

    psa_url_column = find_psa_url_column(df)

    today_str = datetime.today().strftime("%Y-%m-%d")
    price_history = load_price_history(HISTORY_FILE)

    scrape_cardmarket_prices(df)
    scrape_psa_estimates(df, psa_url_column)

    update_price_history(
        df=df,
        price_history=price_history,
        today_str=today_str,
        psa_url_column=psa_url_column,
    )

    convert_price_columns(df)

    trend_sum = round(df["Trend Price"].sum(), 2)
    avg_sum = round(df["30-Day Avg Price"].sum(), 2)
    psa_usd_sum = round(df["PSA Estimate USD"].sum(), 2)

    total_values = {column: "" for column in df.columns}
    total_values["Pokemons"] = "TOTAL"
    total_values["Trend Price"] = trend_sum
    total_values["30-Day Avg Price"] = avg_sum
    total_values["PSA Estimate USD"] = psa_usd_sum

    df = pd.concat([df, pd.DataFrame([total_values])], ignore_index=True)

    if output_path is None:
        base = os.path.splitext(csv_path)[0]
        output_path = f"{base}_updated_{today_str}.csv"

    export_failed_rows(df, output_path, today_str)

    save_csv(df, output_path)

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    save_price_history(price_history, HISTORY_FILE)

    total_cards = len(df) - 1

    print(f"\nSaved to: {output_path}")
    print(f"Trend total: {trend_sum:.2f} € ({total_cards} cards)")
    print(f"30-Day total: {avg_sum:.2f} €")
    print(f"PSA estimate total: ${psa_usd_sum:.2f}")
    print(f"History saved: {HISTORY_FILE}\n")


if __name__ == "__main__":
    multiprocessing.freeze_support()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.isfile(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    run(csv_path, output_path)