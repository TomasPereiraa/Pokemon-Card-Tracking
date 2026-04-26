import json
import os
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.style.use("seaborn-v0_8-darkgrid")

# Change this whenever you want, or set an environment variable:
# Windows example:
# set USD_TO_EUR_RATE=0.92
USD_TO_EUR_RATE = float(os.getenv("USD_TO_EUR_RATE", "0.92"))

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

COLORS = {
    "raw": "#2196F3",
    "avg30": "#FF9800",
    "psa": "#673AB7",
    "combined": "#4CAF50",
    "total": "#9C27B0",
    "up": "#4CAF50",
    "down": "#F44336",
    "neutral": "#9E9E9E",
}


def load_price_history(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_price(raw):
    try:
        text = (
            str(raw)
            .replace("€", "")
            .replace("$", "")
            .strip()
        )

        if text.lower() in {"", "none", "nan", "<na>"}:
            return None

        # Handles:
        # 12,34
        # 12.34
        # 1,234.56
        # 1.234,56
        if "," in text and "." in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif "," in text:
            text = text.replace(",", ".")

        return float(text)

    except Exception:
        return None


def usd_to_eur(value):
    if value is None:
        return None

    return value * USD_TO_EUR_RATE


def get_quantity(entry):
    try:
        return int(entry.get("quantity", 1))
    except Exception:
        return 1


def get_latest_entry(card_data):
    if not card_data:
        return {}

    sorted_data = sorted(card_data, key=lambda entry: entry.get("date", ""))
    return sorted_data[-1]


def split_card_key(card_key):
    parts = str(card_key).split("|")

    card = parts[0] if len(parts) > 0 else str(card_key)
    set_name = parts[1] if len(parts) > 1 else ""
    variant_parts = parts[2:] if len(parts) > 2 else []

    return card, set_name, variant_parts


def format_raw_variant_label(variant_parts):
    labels = []

    for part in variant_parts:
        if part.startswith("lang="):
            language_code = part.replace("lang=", "").strip()
            language_name = LANGUAGE_BY_CODE.get(language_code, "")

            if language_code and language_code != "1":
                labels.append(language_name or f"language {language_code}")

        elif part.startswith("reverse="):
            reverse_value = part.replace("reverse=", "").strip().upper()

            if reverse_value == "Y":
                labels.append("Reverse Holo")

        # condition= is intentionally hidden.
        # psa= is intentionally hidden.

    if not labels:
        return ""

    return " · " + ", ".join(labels)


def display_raw_card_label(card_key):
    card, set_name, variant_parts = split_card_key(card_key)
    variant = format_raw_variant_label(variant_parts)

    if set_name:
        return f"{card} [{set_name}]{variant}"

    return f"{card}{variant}"


def display_psa_card_label(card_key, card_data):
    latest_entry = get_latest_entry(card_data)
    subject = str(latest_entry.get("psa_subject", "")).strip()

    if subject:
        return subject

    card, _, _ = split_card_key(card_key)
    return card


def has_raw_data(card_data):
    for entry in card_data:
        trend = parse_price(entry.get("trend_price"))
        avg30 = parse_price(entry.get("avg_30_price"))

        if trend is not None or avg30 is not None:
            return True

    return False


def has_psa_data(card_data):
    for entry in card_data:
        psa_price = parse_price(entry.get("psa_estimate_usd"))

        if psa_price is not None:
            return True

        if str(entry.get("psa_subject", "")).strip():
            return True

        if str(entry.get("psa_cert_number", "")).strip():
            return True

    return False


def filter_raw_history(history):
    return {
        key: value
        for key, value in history.items()
        if has_raw_data(value)
    }


def filter_psa_history(history):
    return {
        key: value
        for key, value in history.items()
        if has_psa_data(value)
    }


def get_series(card_history):
    dates = []
    raw_trend = []
    raw_avg30 = []
    psa_eur = []
    quantities = []

    sorted_history = sorted(card_history, key=lambda entry: entry.get("date", ""))

    for entry in sorted_history:
        try:
            date = datetime.strptime(entry["date"], "%Y-%m-%d")
        except Exception:
            continue

        trend_value = parse_price(entry.get("trend_price"))
        avg30_value = parse_price(entry.get("avg_30_price"))
        psa_usd_value = parse_price(entry.get("psa_estimate_usd"))
        psa_eur_value = usd_to_eur(psa_usd_value)

        dates.append(date)
        raw_trend.append(trend_value)
        raw_avg30.append(avg30_value)
        psa_eur.append(psa_eur_value)
        quantities.append(get_quantity(entry))

    return dates, raw_trend, raw_avg30, psa_eur, quantities


def get_latest_quantity(card_data):
    latest_entry = get_latest_entry(card_data)
    return get_quantity(latest_entry)


def latest_valid(series):
    valid = [value for value in series if value is not None]

    if not valid:
        return None

    return valid[-1]


def price_change_label(series):
    valid = [value for value in series if value is not None]

    if len(valid) < 2:
        return "", COLORS["neutral"]

    diff = valid[-1] - valid[0]
    direction = "UP" if diff >= 0 else "DOWN"
    color = COLORS["up"] if diff >= 0 else COLORS["down"]

    return f"{direction} {abs(diff):.2f} € ({valid[0]:.2f} -> {valid[-1]:.2f} €)", color


def euro_fmt(value, _):
    return f"{value:.2f} €"


def save_chart(fig, name):
    safe_name = (
        str(name)
        .replace("|", "_")
        .replace(" ", "_")
        .replace("/", "-")
        .replace("=", "-")
        .replace("$", "")
        .replace("[", "")
        .replace("]", "")
    )

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, f"{safe_name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")

    print(f"Saved chart to: {path}")


def remove_copy_suffix(card_key):
    return str(card_key).split(" (x")[0]


def get_copy_number(card_key):
    if " (x" not in str(card_key):
        return ""

    return str(card_key).split("x")[-1].replace(")", "")


def expand_history_with_duplicates(history):
    expanded = {}

    for card_key, card_data in history.items():
        quantity = get_latest_quantity(card_data)

        expanded[card_key] = card_data

        for copy_number in range(2, quantity + 1):
            expanded[f"{card_key} (x{copy_number})"] = card_data

    return expanded


def get_value_series(card_data, source):
    dates, raw_trend, raw_avg30, psa_eur, quantities = get_series(card_data)

    if source == "raw":
        return dates, raw_trend, quantities

    if source == "psa":
        return dates, psa_eur, quantities

    return dates, raw_trend, quantities


def get_display_label(card_key, card_data, source):
    base_key = remove_copy_suffix(card_key)

    if source == "psa":
        return display_psa_card_label(base_key, card_data)

    return display_raw_card_label(base_key)


def search_items(history, query, source="all"):
    results = []

    for card_key, card_data in history.items():
        if source in {"all", "raw"} and has_raw_data(card_data):
            label = display_raw_card_label(card_key)

            if query.lower() in label.lower() or query.lower() in card_key.lower():
                results.append({
                    "source": "raw",
                    "key": card_key,
                    "data": card_data,
                    "label": label,
                })

        if source in {"all", "psa"} and has_psa_data(card_data):
            label = display_psa_card_label(card_key, card_data)

            if query.lower() in label.lower() or query.lower() in card_key.lower():
                results.append({
                    "source": "psa",
                    "key": card_key,
                    "data": card_data,
                    "label": label,
                })

    return results


# Card charts

def visualize_raw_card(card_key, card_history, do_save=False):
    base_key = remove_copy_suffix(card_key)

    dates, raw_trend, raw_avg30, _, quantities = get_series(card_history)

    if not dates:
        print("No date history available for this raw card.")
        return

    if not any(value is not None for value in raw_trend + raw_avg30):
        print("No Cardmarket price data available for this card.")
        return

    change_label, change_color = price_change_label(raw_trend)

    latest_quantity = quantities[-1] if quantities else 1
    quantity_label = f" x{latest_quantity} copies" if latest_quantity > 1 else ""

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        dates,
        raw_trend,
        marker="o",
        linewidth=2,
        color=COLORS["raw"],
        label="Cardmarket Trend EUR",
    )

    ax.plot(
        dates,
        raw_avg30,
        marker="x",
        linewidth=2,
        linestyle="--",
        color=COLORS["avg30"],
        label="Cardmarket 30-Day Avg EUR",
    )

    valid_trend_area = [value if value is not None else 0 for value in raw_trend]
    ax.fill_between(dates, valid_trend_area, alpha=0.08, color=COLORS["raw"])

    if latest_quantity > 1:
        total_trend = [
            value * quantity if value is not None else None
            for value, quantity in zip(raw_trend, quantities)
        ]

        ax.plot(
            dates,
            total_trend,
            marker="s",
            linewidth=1.5,
            linestyle=":",
            color=COLORS["total"],
            label=f"Total EUR x{latest_quantity}",
        )

    for series, color in [(raw_trend, COLORS["raw"]), (raw_avg30, COLORS["avg30"])]:
        valid = [
            (date, value)
            for date, value in zip(dates, series)
            if value is not None
        ]

        if valid:
            date, value = valid[-1]

            ax.annotate(
                f"{value:.2f} €",
                xy=(date, value),
                xytext=(8, 0),
                textcoords="offset points",
                fontsize=9,
                color=color,
                fontweight="bold",
            )

    display_name = display_raw_card_label(base_key)

    ax.set_title(
        f"{display_name}{quantity_label}\n{change_label}",
        fontsize=13,
        color=change_color if change_label else COLORS["neutral"],
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Value EUR")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, f"raw_{display_name}")

    plt.show()


def visualize_psa_card(card_key, card_history, do_save=False):
    base_key = remove_copy_suffix(card_key)

    dates, _, _, psa_eur, quantities = get_series(card_history)

    if not dates:
        print("No date history available for this PSA card.")
        return

    if not any(value is not None for value in psa_eur):
        print("No PSA estimate data available for this card.")
        return

    change_label, change_color = price_change_label(psa_eur)

    latest_quantity = quantities[-1] if quantities else 1
    quantity_label = f" x{latest_quantity} copies" if latest_quantity > 1 else ""

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        dates,
        psa_eur,
        marker="D",
        linewidth=2,
        linestyle="-.",
        color=COLORS["psa"],
        label=f"PSA Estimate EUR, rate {USD_TO_EUR_RATE}",
    )

    if latest_quantity > 1:
        total_psa = [
            value * quantity if value is not None else None
            for value, quantity in zip(psa_eur, quantities)
        ]

        ax.plot(
            dates,
            total_psa,
            marker="s",
            linewidth=1.5,
            linestyle=":",
            color=COLORS["total"],
            label=f"Total PSA EUR x{latest_quantity}",
        )

    valid_psa = [
        (date, value)
        for date, value in zip(dates, psa_eur)
        if value is not None
    ]

    if valid_psa:
        date, value = valid_psa[-1]

        ax.annotate(
            f"{value:.2f} €",
            xy=(date, value),
            xytext=(8, 0),
            textcoords="offset points",
            fontsize=9,
            color=COLORS["psa"],
            fontweight="bold",
        )

    display_name = display_psa_card_label(base_key, card_history)

    ax.set_title(
        f"{display_name}{quantity_label}\n{change_label}",
        fontsize=13,
        color=change_color if change_label else COLORS["neutral"],
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Value EUR")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, f"psa_{display_name}")

    plt.show()


def visualize_item(item, do_save=False):
    if item["source"] == "psa":
        visualize_psa_card(item["key"], item["data"], do_save=do_save)
    else:
        visualize_raw_card(item["key"], item["data"], do_save=do_save)


# Total charts

def visualize_total(history, do_save=False):
    if not history:
        print("No history data available.")
        return

    date_totals = {}

    for card_data in history.values():
        for entry in card_data:
            date = entry.get("date")

            if not date:
                continue

            raw_value = parse_price(entry.get("trend_price")) or 0
            psa_usd_value = parse_price(entry.get("psa_estimate_usd"))
            psa_value_eur = usd_to_eur(psa_usd_value) or 0
            quantity = get_quantity(entry)

            if date not in date_totals:
                date_totals[date] = {
                    "raw": 0,
                    "psa": 0,
                    "combined": 0,
                }

            date_totals[date]["raw"] += raw_value * quantity
            date_totals[date]["psa"] += psa_value_eur * quantity
            date_totals[date]["combined"] += (raw_value + psa_value_eur) * quantity

    sorted_dates = sorted(date_totals)

    if not sorted_dates:
        print("No dated history available.")
        return

    dates = [datetime.strptime(date, "%Y-%m-%d") for date in sorted_dates]
    raw_totals = [date_totals[date]["raw"] for date in sorted_dates]
    psa_totals = [date_totals[date]["psa"] for date in sorted_dates]
    combined_totals = [date_totals[date]["combined"] for date in sorted_dates]

    change_label, change_color = price_change_label(combined_totals)

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        dates,
        raw_totals,
        marker="o",
        linewidth=2,
        color=COLORS["raw"],
        label="Raw Cardmarket Total EUR",
    )

    ax.plot(
        dates,
        psa_totals,
        marker="D",
        linewidth=2,
        linestyle="-.",
        color=COLORS["psa"],
        label=f"PSA Total EUR, rate {USD_TO_EUR_RATE}",
    )

    ax.plot(
        dates,
        combined_totals,
        marker="s",
        linewidth=2.4,
        linestyle="-",
        color=COLORS["combined"],
        label="Combined Total EUR",
    )

    ax.fill_between(dates, combined_totals, alpha=0.08, color=COLORS["combined"])

    for series, color in [
        (raw_totals, COLORS["raw"]),
        (psa_totals, COLORS["psa"]),
        (combined_totals, COLORS["combined"]),
    ]:
        if series:
            ax.annotate(
                f"{series[-1]:.2f} €",
                xy=(dates[-1], series[-1]),
                xytext=(8, 0),
                textcoords="offset points",
                fontsize=9,
                color=color,
                fontweight="bold",
            )

    ax.set_title(
        f"Collection Value EUR\n{change_label}",
        fontsize=13,
        color=change_color if change_label else COLORS["neutral"],
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Value EUR")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, "total_collection_eur")

    plt.show()


# Top charts

def build_ranked_items(history, source="all"):
    ranked = []

    for card_key, card_data in history.items():
        quantity = get_latest_quantity(card_data)

        if source in {"all", "raw"} and has_raw_data(card_data):
            dates, raw_trend, _, _, _ = get_series(card_data)
            latest_value = latest_valid(raw_trend)

            if latest_value is not None:
                for copy_number in range(1, quantity + 1):
                    label = display_raw_card_label(card_key)

                    if copy_number > 1:
                        label = f"{label} copy {copy_number}"

                    ranked.append({
                        "source": "raw",
                        "label": f"[Raw] {label}",
                        "value": latest_value,
                        "key": card_key,
                        "data": card_data,
                    })

        if source in {"all", "psa"} and has_psa_data(card_data):
            dates, _, _, psa_eur, _ = get_series(card_data)
            latest_value = latest_valid(psa_eur)

            if latest_value is not None:
                for copy_number in range(1, quantity + 1):
                    label = display_psa_card_label(card_key, card_data)

                    if copy_number > 1:
                        label = f"{label} copy {copy_number}"

                    ranked.append({
                        "source": "psa",
                        "label": f"[PSA] {label}",
                        "value": latest_value,
                        "key": card_key,
                        "data": card_data,
                    })

    return sorted(ranked, key=lambda item: item["value"], reverse=True)


def visualize_top(history, n=10, source="all", do_save=False):
    ranked = build_ranked_items(history, source=source)[:n]

    if not ranked:
        print("No price data available.")
        return

    labels = [item["label"] for item in ranked]
    values = [item["value"] for item in ranked]
    colors = [
        COLORS["psa"] if item["source"] == "psa" else COLORS["raw"]
        for item in ranked
    ]

    fig, ax = plt.subplots(figsize=(12, max(5, len(ranked) * 0.6)))

    bars = ax.barh(
        labels[::-1],
        values[::-1],
        color=colors[::-1],
        edgecolor="none",
        height=0.6,
    )

    for bar, value in zip(bars, values[::-1]):
        ax.text(
            bar.get_width() + 0.2,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f} €",
            va="center",
            fontsize=9,
            color=COLORS["neutral"],
            fontweight="bold",
        )

    if source == "raw":
        title = f"Top {n} Raw Cards by EUR Value"
        save_name = f"top_{n}_raw_cards_eur"
    elif source == "psa":
        title = f"Top {n} PSA Cards by EUR Value"
        save_name = f"top_{n}_psa_cards_eur"
    else:
        title = f"Top {n} Cards by EUR Value, Raw and PSA"
        save_name = f"top_{n}_all_cards_eur"

    ax.set_title(title, fontsize=13)
    ax.set_xlabel("Value EUR")
    ax.xaxis.set_major_formatter(FuncFormatter(euro_fmt))

    plt.tight_layout()

    if do_save:
        save_chart(fig, save_name)

    plt.show()


# Compare

def visualize_compare(history, queries, do_save=False):
    fig, ax = plt.subplots(figsize=(11, 6))

    palette = [
        COLORS["raw"],
        COLORS["psa"],
        "#FF9800",
        "#9C27B0",
        "#4CAF50",
        "#F44336",
    ]

    plotted = []

    for index, query in enumerate(queries):
        matches = search_items(history, query, source="all")

        if not matches:
            print(f"No match found for '{query}'.")
            continue

        item = matches[0]
        dates, series, _ = get_value_series(item["data"], item["source"])

        color = palette[index % len(palette)]
        label_prefix = "PSA" if item["source"] == "psa" else "Raw"
        label = f"[{label_prefix}] {item['label']}"

        ax.plot(
            dates,
            series,
            marker="o",
            linewidth=2,
            color=color,
            label=label,
        )

        valid = [
            (date, value)
            for date, value in zip(dates, series)
            if value is not None
        ]

        if valid:
            ax.annotate(
                f"{valid[-1][1]:.2f} €",
                xy=(valid[-1][0], valid[-1][1]),
                xytext=(8, 0),
                textcoords="offset points",
                fontsize=9,
                color=color,
                fontweight="bold",
            )

        plotted.append(item)

    if not plotted:
        plt.close(fig)
        return

    ax.set_title("Price Comparison EUR", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Value EUR")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, "compare_" + "_".join(queries))

    plt.show()


# Lists

def print_raw_list(history):
    raw_history = filter_raw_history(history)

    print("\nRaw Cardmarket Cards")

    if not raw_history:
        print("  None")
        return

    index = 1

    for card_key in sorted(raw_history.keys(), key=lambda key: display_raw_card_label(key).lower()):
        quantity = get_latest_quantity(raw_history[card_key])
        label = display_raw_card_label(card_key)

        if quantity > 1:
            for copy_number in range(1, quantity + 1):
                suffix = f" copy {copy_number}" if copy_number > 1 else ""
                print(f"{index:>3}. {label}{suffix}")
                index += 1
        else:
            print(f"{index:>3}. {label}")
            index += 1


def print_psa_list(history):
    psa_history = filter_psa_history(history)

    print(f"\nPSA Cards, converted to EUR at rate {USD_TO_EUR_RATE}")

    if not psa_history:
        print("  None")
        return

    index = 1

    for card_key in sorted(psa_history.keys(), key=lambda key: display_psa_card_label(key, psa_history[key]).lower()):
        quantity = get_latest_quantity(psa_history[card_key])
        label = display_psa_card_label(card_key, psa_history[card_key])

        if quantity > 1:
            for copy_number in range(1, quantity + 1):
                suffix = f" copy {copy_number}" if copy_number > 1 else ""
                print(f"{index:>3}. {label}{suffix}")
                index += 1
        else:
            print(f"{index:>3}. {label}")
            index += 1


def choose_and_visualize(items, do_save=False):
    if not items:
        print("No matches found.")
        return

    if len(items) == 1:
        visualize_item(items[0], do_save=do_save)
        return

    print("Multiple matches:")

    for index, item in enumerate(items, 1):
        label_prefix = "PSA" if item["source"] == "psa" else "Raw"
        print(f"{index}. [{label_prefix}] {item['label']}")

    selection = input("Select number: ").strip()

    if not selection.isdigit():
        print("Invalid selection.")
        return

    selected_index = int(selection) - 1

    if selected_index < 0 or selected_index >= len(items):
        print("Invalid selection.")
        return

    visualize_item(items[selected_index], do_save=do_save)


HELP = f"""
Commands:
  list                 - list raw and PSA cards separately
  list raw             - list only raw Cardmarket cards
  list psa             - list only PSA cards

  total                - plot raw, PSA converted, and combined total in EUR

  top [n]              - top N cards by EUR value, raw and PSA together
  top raw [n]          - top N raw cards by EUR value
  top psa [n]          - top N PSA cards by EUR value

  raw <card name>      - plot raw Cardmarket history for a card
  psa <card name>      - plot PSA estimate history for a card, converted to EUR

  compare <c1> <c2>    - compare raw and/or PSA entries in EUR

  save total           - save total chart as PNG
  save top [n]         - save combined top N chart as PNG
  save top raw [n]     - save raw top N chart as PNG
  save top psa [n]     - save PSA top N chart as PNG
  save raw <card>      - save raw card chart as PNG
  save psa <card>      - save PSA card chart as PNG

  exit                 - quit

Current USD to EUR rate used by visualizer: {USD_TO_EUR_RATE}
"""


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, "data", "price_history.json")

    json_path = sys.argv[1] if len(sys.argv) > 1 else default_path

    try:
        data = load_price_history(json_path)
    except FileNotFoundError:
        print(f"History file not found: {json_path}")
        sys.exit(1)

    raw_data = filter_raw_history(data)
    psa_data = filter_psa_history(data)

    total_raw_cards = sum(get_latest_quantity(card_data) for card_data in raw_data.values())
    total_psa_cards = sum(get_latest_quantity(card_data) for card_data in psa_data.values())

    print("\nPokemon Card Price Visualizer")
    print(f"{len(raw_data)} raw entries, {total_raw_cards} raw total copies.")
    print(f"{len(psa_data)} PSA entries, {total_psa_cards} PSA total copies.")
    print(f"PSA USD values are converted to EUR using rate: {USD_TO_EUR_RATE}")
    print("Type 'help' for commands.\n")

    while True:
        try:
            raw_input_text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw_input_text:
            continue

        parts = raw_input_text.split()
        command = parts[0].lower()

        if command == "exit":
            print("Exiting.")
            break

        elif command == "help":
            print(HELP)

        elif command == "list":
            if len(parts) > 1 and parts[1].lower() == "raw":
                print_raw_list(data)

            elif len(parts) > 1 and parts[1].lower() == "psa":
                print_psa_list(data)

            else:
                print_raw_list(data)
                print_psa_list(data)

        elif command == "total":
            visualize_total(data)

        elif command == "top":
            if len(parts) > 1 and parts[1].lower() == "raw":
                n = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
                visualize_top(data, n, source="raw")

            elif len(parts) > 1 and parts[1].lower() == "psa":
                n = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
                visualize_top(data, n, source="psa")

            else:
                n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
                visualize_top(data, n, source="all")

        elif command == "raw":
            if len(parts) < 2:
                print("Usage: raw <card name>")
            else:
                query = " ".join(parts[1:])
                matches = search_items(data, query, source="raw")
                choose_and_visualize(matches)

        elif command == "psa":
            if len(parts) < 2:
                print("Usage: psa <card name>")
            else:
                query = " ".join(parts[1:])
                matches = search_items(data, query, source="psa")
                choose_and_visualize(matches)

        elif command == "compare":
            if len(parts) < 3:
                print("Usage: compare <card1> <card2>")
            else:
                visualize_compare(data, parts[1:])

        elif command == "save":
            if len(parts) < 2:
                print("Usage: save total OR save top [n] OR save raw <card> OR save psa <card>")

            elif parts[1].lower() == "total":
                visualize_total(data, do_save=True)

            elif parts[1].lower() == "top":
                if len(parts) > 2 and parts[2].lower() == "raw":
                    n = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 10
                    visualize_top(data, n, source="raw", do_save=True)

                elif len(parts) > 2 and parts[2].lower() == "psa":
                    n = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 10
                    visualize_top(data, n, source="psa", do_save=True)

                else:
                    n = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
                    visualize_top(data, n, source="all", do_save=True)

            elif parts[1].lower() == "raw":
                if len(parts) < 3:
                    print("Usage: save raw <card>")
                else:
                    query = " ".join(parts[2:])
                    matches = search_items(data, query, source="raw")
                    choose_and_visualize(matches, do_save=True)

            elif parts[1].lower() == "psa":
                if len(parts) < 3:
                    print("Usage: save psa <card>")
                else:
                    query = " ".join(parts[2:])
                    matches = search_items(data, query, source="psa")
                    choose_and_visualize(matches, do_save=True)

            else:
                print("Usage: save total OR save top [n] OR save raw <card> OR save psa <card>")

        else:
            matches = search_items(data, raw_input_text, source="all")

            if not matches:
                print(f"No match for '{raw_input_text}'. Type 'list' to see all cards.")
            else:
                choose_and_visualize(matches)


if __name__ == "__main__":
    main()