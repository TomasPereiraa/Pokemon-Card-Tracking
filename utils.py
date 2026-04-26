import json
import os
from urllib.parse import parse_qs, unquote, urlparse

import pandas as pd


LANGUAGE_BY_CODE = {
    "1": "English",
    "2": "French",
    "3": "German",
    "4": "Spanish",
    "5": "Italian",
    "6": "S-Chinese",
    "7": "Japanese",
    "8": "Portuguese",
    "10": "Korean",
    "11": "T-Chinese",
}

CONDITION_BY_CODE = {
    "1": "Mint",
    "2": "Near Mint",
    "3": "Excellent",
    "4": "Good",
    "5": "Light Played",
    "6": "Played",
    "7": "Poor",
}


def prettify_slug(value: str) -> str:
    return unquote(str(value)).replace("-", " ").title()


def get_query_value(query: dict, key: str, default: str = "") -> str:
    values = query.get(key)
    if not values:
        return default
    return values[0]


def extract_card_info(url: str) -> dict:
    """
    Extracts useful card metadata from a Cardmarket URL.

    Example:
    https://www.cardmarket.com/en/Pokemon/Products/Singles/HeartGold-SoulSilver/Ninetales-HS7?language=1&isReverseHolo=Y

    Returns columns such as:
    - Pokemons
    - Set
    - Card Slug
    - Language Code
    - Language
    - Min Condition Code
    - Min Condition
    - Reverse Holo
    """

    parsed = urlparse(str(url).strip())
    path_parts = parsed.path.rstrip("/").split("/")
    query = parse_qs(parsed.query)

    if len(path_parts) < 2:
        return {
            "Pokemons": "Unknown",
            "Set": "Unknown",
            "Card Slug": "Unknown",
            "Language Code": "",
            "Language": "",
            "Min Condition Code": "",
            "Min Condition": "",
            "Reverse Holo": "",
        }

    set_slug = unquote(path_parts[-2])
    card_slug = unquote(path_parts[-1])

    language_code = get_query_value(query, "language")
    condition_code = get_query_value(query, "minCondition")
    reverse_holo = get_query_value(query, "isReverseHolo")

    return {
        "Pokemons": prettify_slug(card_slug),
        "Set": prettify_slug(set_slug),
        "Card Slug": card_slug,
        "Language Code": language_code,
        "Language": LANGUAGE_BY_CODE.get(language_code, ""),
        "Min Condition Code": condition_code,
        "Min Condition": CONDITION_BY_CODE.get(condition_code, ""),
        "Reverse Holo": reverse_holo,
    }


def extract_name_set(url: str):
    """
    Backwards-compatible helper.

    Kept so old code importing extract_name_set does not immediately break.
    """
    info = extract_card_info(url)
    return info["Pokemons"], info["Set"]


def build_card_key(row) -> str:
    """
    Builds the key used in price_history.json.

    Simple URLs keep this format:
    Card Name|Set Name

    URLs with variants become:
    Card Name|Set Name|lang=1|condition=6|reverse=Y

    This avoids mixing prices from different versions of the same card.
    """

    base_key = f"{row['Pokemons']}|{row['Set']}"

    variant_parts = []

    language_code = str(row.get("Language Code", "")).strip()
    condition_code = str(row.get("Min Condition Code", "")).strip()
    reverse_holo = str(row.get("Reverse Holo", "")).strip()

    if language_code:
        variant_parts.append(f"lang={language_code}")

    if condition_code:
        variant_parts.append(f"condition={condition_code}")

    if reverse_holo:
        variant_parts.append(f"reverse={reverse_holo}")

    if not variant_parts:
        return base_key

    return base_key + "|" + "|".join(variant_parts)


def parse_euro_price(value):
    """
    Converts Cardmarket price strings into floats.

    Examples:
    '12,34 €' -> 12.34
    '12.34'   -> 12.34
    'Error'   -> None
    """

    try:
        cleaned = (
            str(value)
            .replace("€", "")
            .replace(",", ".")
            .strip()
        )
        return float(cleaned)
    except Exception:
        return None


def load_csv(csv_file):
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";")

    if "URL" not in df.columns:
        raise ValueError("The CSV file must have a 'URL' column with Cardmarket links.")

    df["URL"] = df["URL"].astype(str).str.strip()
    df = df[df["URL"] != ""].copy()

    return df


def save_csv(df, output_file):
    df.to_csv(output_file, index=False, encoding="utf-8-sig", sep=";")


def load_price_history(json_path):
    if not os.path.exists(json_path):
        return {}

    with open(json_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

        if not content:
            return {}

        return json.loads(content)


def save_price_history(data, json_path):
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)