import os
import json
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime

plt.style.use("seaborn-v0_8-darkgrid")

COLORS = {
    "trend":   "#2196F3",
    "avg30":   "#FF9800",
    "up":      "#4CAF50",
    "down":    "#F44336",
    "neutral": "#9E9E9E",
}

# ── helpers ──────────────────────────────────────────────────────────────────

def load_price_history(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_price(raw):
    try:
        return float(str(raw).replace("€", "").replace(",", ".").strip())
    except Exception:
        return None

def get_series(card_history):
    dates, trend, avg30 = [], [], []
    for entry in card_history:
        dates.append(datetime.strptime(entry["date"], "%Y-%m-%d"))
        trend.append(parse_price(entry.get("trend_price")))
        avg30.append(parse_price(entry.get("avg_30_price")))
    return dates, trend, avg30

def price_change_label(series):
    valid = [v for v in series if v is not None]
    if len(valid) < 2:
        return "", COLORS["neutral"]
    diff = valid[-1] - valid[0]
    symbol = "▲" if diff >= 0 else "▼"
    color  = COLORS["up"] if diff >= 0 else COLORS["down"]
    return f"{symbol} {abs(diff):.2f} €  ({valid[0]:.2f} → {valid[-1]:.2f} €)", color

def euro_fmt(x, _):
    return f"{x:.2f} €"

def save_chart(fig, name):
    safe = name.replace("|", "_").replace(" ", "_").replace("/", "-")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{safe}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  💾 Saved → {path}")

def search_cards(history, query):
    return {k: v for k, v in history.items() if query.lower() in k.lower()}

# ── plot functions ────────────────────────────────────────────────────────────

def visualize_card(card_name, card_history, do_save=False):
    dates, trend, avg30 = get_series(card_history)
    change_label, change_color = price_change_label(trend)

    fig, ax = plt.subplots(figsize=(11, 6))

    # Lines + shaded area
    ax.plot(dates, trend, marker="o", linewidth=2, color=COLORS["trend"], label="Trend Price")
    ax.plot(dates, avg30, marker="x", linewidth=2, linestyle="--", color=COLORS["avg30"], label="30-Day Avg")
    valid_trend = [v if v is not None else 0 for v in trend]
    ax.fill_between(dates, valid_trend, alpha=0.08, color=COLORS["trend"])

    # Annotate latest values
    for series, color in [(trend, COLORS["trend"]), (avg30, COLORS["avg30"])]:
        valid = [(d, v) for d, v in zip(dates, series) if v is not None]
        if valid:
            d, v = valid[-1]
            ax.annotate(f"{v:.2f} €", xy=(d, v),
                        xytext=(8, 0), textcoords="offset points",
                        fontsize=9, color=color, fontweight="bold")

    ax.set_title(f"{card_name}\n{change_label}", fontsize=13,
                 color=change_color if change_label else COLORS["neutral"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (€)")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, card_name)
    plt.show()

def visualize_total(history, do_save=False):
    date_totals = {}
    for card_data in history.values():
        for entry in card_data:
            d = entry["date"]
            t = parse_price(entry.get("trend_price")) or 0
            a = parse_price(entry.get("avg_30_price")) or 0
            if d not in date_totals:
                date_totals[d] = {"trend": 0, "avg30": 0}
            date_totals[d]["trend"] += t
            date_totals[d]["avg30"] += a

    sorted_dates = sorted(date_totals)
    dates       = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_dates]
    trend_tots  = [date_totals[d]["trend"] for d in sorted_dates]
    avg_tots    = [date_totals[d]["avg30"]  for d in sorted_dates]

    change_label, change_color = price_change_label(trend_tots)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(dates, trend_tots, marker="o", linewidth=2, color=COLORS["trend"], label="Total Trend")
    ax.plot(dates, avg_tots,   marker="x", linewidth=2, linestyle="--", color=COLORS["avg30"], label="Total 30-Day Avg")
    ax.fill_between(dates, trend_tots, alpha=0.08, color=COLORS["trend"])

    for series, color in [(trend_tots, COLORS["trend"]), (avg_tots, COLORS["avg30"])]:
        if series:
            ax.annotate(f"{series[-1]:.2f} €", xy=(dates[-1], series[-1]),
                        xytext=(8, 0), textcoords="offset points",
                        fontsize=9, color=color, fontweight="bold")

    ax.set_title(f"Total Collection Value\n{change_label}", fontsize=13,
                 color=change_color if change_label else COLORS["neutral"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Total (€)")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, "total_collection")
    plt.show()

def visualize_top(history, n=10, do_save=False):
    latest = {}
    for card_name, card_data in history.items():
        prices = [parse_price(e.get("trend_price")) for e in card_data]
        valid  = [p for p in prices if p is not None]
        if valid:
            latest[card_name] = valid[-1]

    top = sorted(latest.items(), key=lambda x: x[1], reverse=True)[:n]
    if not top:
        print("  No data available.")
        return

    labels = [k.split("|")[0] for k, _ in top]
    values = [v for _, v in top]
    bar_colors = [COLORS["trend"]] * len(values)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(labels[::-1], values[::-1], color=bar_colors[::-1], edgecolor="none", height=0.6)

    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f} €", va="center", fontsize=9, color=COLORS["trend"], fontweight="bold")

    ax.set_title(f"Top {n} Most Valuable Cards (Trend Price)", fontsize=13)
    ax.set_xlabel("Price (€)")
    ax.xaxis.set_major_formatter(FuncFormatter(euro_fmt))
    plt.tight_layout()

    if do_save:
        save_chart(fig, f"top_{n}_cards")
    plt.show()

def visualize_compare(history, queries, do_save=False):
    fig, ax = plt.subplots(figsize=(11, 6))
    palette = ["#2196F3", "#FF9800", "#9C27B0", "#4CAF50", "#F44336"]
    plotted = []

    for i, query in enumerate(queries):
        matches = search_cards(history, query)
        if not matches:
            print(f"  No match found for '{query}'.")
            continue
        card_name = next(iter(matches))
        dates, trend, _ = get_series(matches[card_name])
        color = palette[i % len(palette)]
        ax.plot(dates, trend, marker="o", linewidth=2, color=color, label=card_name.split("|")[0])
        valid = [(d, v) for d, v in zip(dates, trend) if v is not None]
        if valid:
            ax.annotate(f"{valid[-1][1]:.2f} €", xy=(valid[-1][0], valid[-1][1]),
                        xytext=(8, 0), textcoords="offset points",
                        fontsize=9, color=color, fontweight="bold")
        plotted.append(card_name)

    if not plotted:
        plt.close(fig)
        return

    ax.set_title("Card Price Comparison", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Trend Price (€)")
    ax.yaxis.set_major_formatter(FuncFormatter(euro_fmt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()

    if do_save:
        save_chart(fig, "compare_" + "_".join(queries))
    plt.show()

# ── CLI ───────────────────────────────────────────────────────────────────────

HELP = """
Commands:
  list                    — list all cards in history
  total                   — plot total collection value
  top [n]                 — bar chart of top N most valuable cards (default 10)
  compare <a> <b> [...]   — compare multiple cards on one chart
  save <card name>        — plot and save chart as PNG
  save total              — save total collection chart as PNG
  save top [n]            — save top N chart as PNG
  <card name>             — plot price history for a card
  exit                    — quit
"""

def main():
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, "data", "price_history.json")
    json_path    = sys.argv[1] if len(sys.argv) > 1 else default_path

    try:
        data = load_price_history(json_path)
    except FileNotFoundError:
        print(f"History file not found: {json_path}")
        sys.exit(1)

    print(f"\n📊 Pokémon Card Price Visualizer")
    print(f"   {len(data)} cards in history — type 'help' for commands\n")

    while True:
        try:
            raw = input("› ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd   = parts[0].lower()

        if cmd == "exit":
            print("Exiting.")
            break

        elif cmd == "help":
            print(HELP)

        elif cmd == "list":
            if not data:
                print("  No cards in history yet.")
            else:
                for i, name in enumerate(sorted(data.keys()), 1):
                    card, set_name = name.split("|") if "|" in name else (name, "")
                    print(f"  {i:>3}. {card}  [{set_name}]")

        elif cmd == "total":
            visualize_total(data)

        elif cmd == "top":
            n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
            visualize_top(data, n)

        elif cmd == "compare":
            if len(parts) < 3:
                print("  Usage: compare <card a> <card b> ...")
            else:
                visualize_compare(data, parts[1:])

        elif cmd == "save":
            if len(parts) < 2:
                print("  Usage: save <card name | total | top [n]>")
            elif parts[1].lower() == "total":
                visualize_total(data, do_save=True)
            elif parts[1].lower() == "top":
                n = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
                visualize_top(data, n, do_save=True)
            else:
                query = " ".join(parts[1:])
                matches = search_cards(data, query)
                if not matches:
                    print(f"  No match for '{query}'.")
                elif len(matches) > 1:
                    print("  Multiple matches:")
                    for i, name in enumerate(matches.keys(), 1):
                        print(f"    {i}. {name}")
                    sel = input("  Select number: ").strip()
                    if sel.isdigit():
                        card_name = list(matches.keys())[int(sel) - 1]
                        visualize_card(card_name, matches[card_name], do_save=True)
                else:
                    card_name = next(iter(matches))
                    visualize_card(card_name, matches[card_name], do_save=True)

        else:
            # Default: treat entire input as a card name search
            matches = search_cards(data, raw)
            if not matches:
                print(f"  No match for '{raw}'. Type 'list' to see all cards.")
            elif len(matches) > 1:
                print("  Multiple matches:")
                for i, name in enumerate(matches.keys(), 1):
                    card, set_name = name.split("|") if "|" in name else (name, "")
                    print(f"    {i}. {card}  [{set_name}]")
                sel = input("  Select number: ").strip()
                if sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(matches):
                        card_name = list(matches.keys())[idx]
                        visualize_card(card_name, matches[card_name])
                    else:
                        print("  Invalid selection.")
            else:
                card_name = next(iter(matches))
                visualize_card(card_name, matches[card_name])

if __name__ == "__main__":
    main()
