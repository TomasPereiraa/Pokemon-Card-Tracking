import json
import matplotlib.pyplot as plt
from datetime import datetime
import sys


def load_price_history(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def search_cards(history, query):
    matches = {name: data for name, data in history.items() if query.lower() in name.lower()}
    return matches


def visualize_card(card_name, card_history):
    dates = [datetime.strptime(entry["date"], '%Y-%m-%d') for entry in card_history]
    trend_prices = [float(entry["trend_price"].replace(",", ".")) if entry["trend_price"].replace('.', '', 1).isdigit() else None for entry in card_history]
    avg_30_prices = [float(entry["avg_30_price"].replace(",", ".")) if entry["avg_30_price"].replace('.', '', 1).isdigit() else None for entry in card_history]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, trend_prices, marker='o', label="Trend Price")
    plt.plot(dates, avg_30_prices, marker='x', label="30-Day Avg Price")
    plt.xlabel('Date')
    plt.ylabel('Price (€)')
    plt.title(f"Price History for {card_name}")
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_total(history_data):
    date_history = {}
    for card_history in history_data.values():
        for entry in card_history:
            date = entry["date"]
            trend_price = float(entry["trend_price"].replace(",", ".")) if entry["trend_price"].replace('.', '', 1).isdigit() else 0
            avg_30_price = float(entry["avg_30_price"].replace(",", ".")) if entry["avg_30_price"].replace('.', '', 1).isdigit() else 0

            if date not in date_history:
                date_history[date] = {"trend_total": 0, "avg_30_total": 0}

            date_history[date]["trend_total"] += trend_price
            date_history[date]["avg_30_total"] += avg_30_price

    dates = [datetime.strptime(date, '%Y-%m-%d') for date in sorted(date_history)]
    trend_totals = [date_history[date]["trend_total"] for date in sorted(date_history)]
    avg_30_totals = [date_history[date]["avg_30_total"] for date in sorted(date_history)]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, trend_totals, marker='o', label='Total Trend Price')
    plt.plot(dates, avg_30_totals, marker='x', label='Total 30-Day Avg Price')
    plt.xlabel('Date')
    plt.ylabel('Total Price (€)')
    plt.title('Total Collection Price History')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    history_file = "data/price_history.json"

    try:
        data = load_price_history(history_file)
    except FileNotFoundError:
        print(f"❌ The file '{history_file}' was not found. Please run 'main.py' first.")
        sys.exit(1)

    card_query = input("Enter Pokémon card name (or type 'total' for total prices): ").strip()

    if card_query.lower() == 'total':
        visualize_total(data)
    else:
        matches = search_cards(data, card_query)

        if not matches:
            print(f"No matches found for '{card_query}'")
            sys.exit()

        if len(matches) > 1:
            print("Found multiple matches:")
            for idx, name in enumerate(matches.keys(), 1):
                print(f"{idx}. {name}")

            selection = int(input("Select the card by number (1, 2, 3...): ")) - 1
            card_name = list(matches.keys())[selection]
        else:
            card_name = next(iter(matches))

        selected_history = matches[card_name]
        visualize_card(card_name, selected_history)
