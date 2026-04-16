import pandas as pd
import json
from datetime import datetime
import os

def extract_name_set(url):
    parts = url.rstrip("/").split("/")
    if len(parts) < 6:
        return "Unknown", "Unknown"
    set_name = parts[-2].replace("-", " ").title()
    card_name = parts[-1].replace("-", " ").title()
    return card_name, set_name

def load_csv(csv_file):
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";")
    if "URL" not in df.columns:
        raise ValueError("❌ The CSV file must have a 'URL' column with Cardmarket links.")
    return df

def save_csv(df, output_file):
    df.to_csv(output_file, index=False, encoding="utf-8-sig", sep=";")

def load_price_history(json_path):
    if not os.path.exists(json_path):
        return {}
    with open(json_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        if not content:          # ← handles empty file
            return {}
        return json.loads(content)

def save_price_history(data, json_path):
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
