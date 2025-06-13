import os
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
    trend_prices = []
    avg_30_prices = []
    for entry in card_history:
        try:
            trend_prices.append(float(entry["trend_price"].replace("€", "").replace(",", ".").strip()))
        except:
            trend_prices.append(None)
        try:
            avg_30_prices.append(float(entry["avg_30_price"].replace("€", "").replace(",", ".").strip()))
        except:
            avg_30_prices.append(None)

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


def visualize_total(history):
    date_history = {}
    for card_data in history.values():
        for entry in card_data:
            date = entry["date"]
            try:
                trend_price = float(entry["trend_price"].replace("€", "").replace(",", ".").strip())
            except:
                trend_price = 0
            try:
                avg_30_price = float(entry["avg_30_price"].replace("€", "").replace(",", ".").strip())
            except:
                avg_30_price = 0
            if date not in date_history:
                date_history[date] = {"trend_total": 0, "avg_30_total": 0}
            date_history[date]["trend_total"] += trend_price
            date_history[date]["avg_30_total"] += avg_30_price

    dates = [datetime.strptime(d, '%Y-%m-%d') for d in sorted(date_history)]
    trend_totals = [date_history[d]["trend_total"] for d in sorted(date_history)]
    avg_totals = [date_history[d]["avg_30_total"] for d in sorted(date_history)]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, trend_totals, marker='o', label='Total Trend Price')
    plt.plot(dates, avg_totals, marker='x', label='Total 30-Day Avg Price')
    plt.xlabel('Date')
    plt.ylabel('Total Price (€)')
    plt.title('Total Collection Price History')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    # Determine JSON path relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, 'data', 'price_history.json')

    # Allow custom path via first CLI argument
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = default_path

    try:
        data = load_price_history(json_path)
    except FileNotFoundError:
        print(f"JSON history file not found at {json_path}")
        sys.exit(1)

    print(f"Loaded price history from: {json_path}")

    while True:
        card_query = input("Enter card name to visualize (or 'total' for collection, 'exit' to quit): ")
        if card_query.lower() == 'exit':
            print("Exiting visualizer.")
            break

        if card_query.lower() == 'total':
            visualize_total(data)
            continue

        matches = search_cards(data, card_query)
        if not matches:
            print(f"No matches found for '{card_query}'.")
            continue

        if len(matches) > 1:
            print("Found multiple matches:")
            for idx, name in enumerate(matches.keys(), 1):
                print(f"{idx}. {name}")
            try:
                selection = int(input("Select the card by number: ")) - 1
                if selection < 0 or selection >= len(matches):
                    print("Invalid selection.")
                    continue
                card_name = list(matches.keys())[selection]
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
        else:
            card_name = next(iter(matches))

        selected_history = matches[card_name]
        visualize_card(card_name, selected_history)

if __name__ == '__main__':
    main()
