import pandas as pd
from utils import extract_name_set, load_csv, save_csv, load_price_history, save_price_history
from scraper import setup_driver, get_cardmarket_prices
from datetime import datetime


def main():
    csv_file = r"C:\Users\tomas\Downloads\pokemons_cards.csv"
    output_file = r"C:\Users\tomas\Downloads\updated_pokemons_cards.csv"
    history_file = "data/price_history.json"

    df = load_csv(csv_file)
    df[["Pokemons", "Set"]] = df["URL"].apply(lambda x: pd.Series(extract_name_set(x)))

    driver = setup_driver()

    today_str = datetime.today().strftime('%Y-%m-%d')
    price_history = load_price_history(history_file)

    df["Trend Price"] = ""
    df["30-Day Avg Price"] = ""

    for index, row in df.iterrows():
        url = row["URL"]
        print(f"📢 Fetching prices for: {url}...")
        prices = get_cardmarket_prices(driver, url)

        df.at[index, "Trend Price"] = prices["Trend Price"]
        df.at[index, "30-Day Avg Price"] = prices["30-Day Avg Price"]

        # Store history
        card_name = row["Pokemons"]
        if card_name not in price_history:
            price_history[card_name] = []

        price_history[card_name].append({
            "date": today_str,
            "trend_price": prices["Trend Price"].replace(" €", "").replace(",", "."),
            "avg_30_price": prices["30-Day Avg Price"].replace(" €", "").replace(",", ".")
        })

    driver.quit()

    # Convert prices to numeric for CSV summary
    df["Trend Price"] = pd.to_numeric(df["Trend Price"].str.replace(" €", "").str.replace(",", "."), errors="coerce")
    df["30-Day Avg Price"] = pd.to_numeric(df["30-Day Avg Price"].str.replace(" €", "").str.replace(",", "."),
                                           errors="coerce")

    total_trend_price = df["Trend Price"].sum()
    total_avg_30_price = df["30-Day Avg Price"].sum()

    total_row = pd.DataFrame([["Total", "", "", total_trend_price, total_avg_30_price]], columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)

    save_csv(df, output_file)
    save_price_history(price_history, history_file)

    print(f"\n✅ Updated prices saved to '{output_file}' and history saved to '{history_file}'!")


if __name__ == "__main__":
    main()
