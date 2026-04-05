import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_engine

fake = Faker("en_US")
random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────

N_CLIENTS   = 2000
N_MANAGERS  = 80
START_DATE  = datetime(2020, 1, 1)
END_DATE    = datetime(2025, 12, 31)

RISK_PROFILES = {
    "Conservative": {
        "description": "Low risk tolerance. Prefers stable, dividend-paying stocks.",
        "max_stock_weight": 0.10,
        "allowed_sectors": "Utilities, Consumer Staples, Health Care, Financials",
        "avg_positions": 5,
        "transaction_multiplier": 1,
    },
    "Moderate": {
        "description": "Balanced risk. Mix of growth and income stocks.",
        "max_stock_weight": 0.20,
        "allowed_sectors": "Financials, Health Care, Industrials, Consumer Discretionary, Real Estate",
        "avg_positions": 10,
        "transaction_multiplier": 2,
    },
    "Aggressive": {
        "description": "High risk tolerance. Focuses on growth and tech stocks.",
        "max_stock_weight": 0.35,
        "allowed_sectors": "Information Technology, Communication Services, Consumer Discretionary, Energy",
        "avg_positions": 15,
        "transaction_multiplier": 4,
    },
    "Very Aggressive": {
        "description": "Maximum risk. Concentrated positions in high-growth sectors.",
        "max_stock_weight": 0.50,
        "allowed_sectors": "Information Technology, Communication Services, Energy",
        "avg_positions": 20,
        "transaction_multiplier": 6,
    },
}

US_STATES = [
    "California", "Texas", "Florida", "New York", "Pennsylvania",
    "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan",
    "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts",
    "Tennessee", "Indiana", "Missouri", "Maryland", "Wisconsin",
    "Colorado", "Minnesota", "South Carolina", "Alabama", "Louisiana",
    "Kentucky", "Oregon", "Oklahoma", "Connecticut", "Utah",
    "Nevada", "Arkansas", "Iowa", "Mississippi", "Kansas",
    "New Mexico", "Nebraska", "Idaho", "West Virginia", "Hawaii",
]

STATE_CITIES = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "New York": ["New York City", "Buffalo", "Albany", "Rochester"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown"],
    "Illinois": ["Chicago", "Aurora", "Naperville"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
    "Georgia": ["Atlanta", "Augusta", "Savannah"],
    "North Carolina": ["Charlotte", "Raleigh", "Durham"],
    "Michigan": ["Detroit", "Grand Rapids", "Ann Arbor"],
    "New Jersey": ["Newark", "Jersey City", "Trenton"],
    "Virginia": ["Virginia Beach", "Richmond", "Arlington"],
    "Washington": ["Seattle", "Spokane", "Tacoma"],
    "Arizona": ["Phoenix", "Tucson", "Scottsdale"],
    "Massachusetts": ["Boston", "Worcester", "Springfield"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville"],
    "Missouri": ["Kansas City", "St. Louis", "Springfield"],
    "Maryland": ["Baltimore", "Annapolis", "Rockville"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora"],
    "Minnesota": ["Minneapolis", "St. Paul", "Rochester"],
    "South Carolina": ["Columbia", "Charleston", "Greenville"],
    "Alabama": ["Birmingham", "Montgomery", "Huntsville"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport"],
    "Kentucky": ["Louisville", "Lexington", "Bowling Green"],
    "Oregon": ["Portland", "Salem", "Eugene"],
    "Oklahoma": ["Oklahoma City", "Tulsa", "Norman"],
    "Connecticut": ["Bridgeport", "New Haven", "Hartford"],
    "Utah": ["Salt Lake City", "West Valley City", "Provo"],
    "Nevada": ["Las Vegas", "Henderson", "Reno"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville"],
    "Iowa": ["Des Moines", "Cedar Rapids", "Davenport"],
    "Mississippi": ["Jackson", "Gulfport", "Southaven"],
    "Kansas": ["Wichita", "Overland Park", "Kansas City"],
    "New Mexico": ["Albuquerque", "Santa Fe", "Las Cruces"],
    "Nebraska": ["Omaha", "Lincoln", "Bellevue"],
    "Idaho": ["Boise", "Meridian", "Nampa"],
    "West Virginia": ["Charleston", "Huntington", "Morgantown"],
    "Hawaii": ["Honolulu", "Pearl City", "Hilo"],
}

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]

INCOME_BY_RISK = {
    "Conservative":    (40000,  90000),
    "Moderate":        (70000,  150000),
    "Aggressive":      (120000, 300000),
    "Very Aggressive": (200000, 1000000),
}

BALANCE_BY_RISK = {
    "Conservative":    (10000,  100000),
    "Moderate":        (50000,  300000),
    "Aggressive":      (100000, 800000),
    "Very Aggressive": (300000, 3000000),
}


# ─────────────────────────────────────────
# 1. RISK PROFILES
# ─────────────────────────────────────────

def generate_risk_profiles():
    rows = []
    for name, details in RISK_PROFILES.items():
        rows.append({
            "risk_profile":       name,
            "description":        details["description"],
            "max_stock_weight":   details["max_stock_weight"],
            "allowed_sectors":    details["allowed_sectors"],
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# 2. MANAGERS
# ─────────────────────────────────────────

def generate_managers():
    rows = []
    for i in range(1, N_MANAGERS + 1):
        region = random.choice(REGIONS)
        hire_date = fake.date_between(start_date="-15y", end_date="-1y")
        rows.append({
            "manager_id":    f"MGR{i:04d}",
            "name":          fake.name(),
            "email":         fake.company_email(),
            "phone":         fake.numerify("(###) ###-####"),
            "region":        region,
            "hire_date":     hire_date,
            "years_at_firm": (datetime.today().date() - hire_date).days // 365,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# 3. CLIENTS
# ─────────────────────────────────────────

def generate_clients(managers_df):
    manager_ids = managers_df["manager_id"].tolist()
    risk_weights = [0.30, 0.35, 0.25, 0.10]  # Conservative, Moderate, Aggressive, Very Aggressive
    risk_names   = list(RISK_PROFILES.keys())

    rows = []
    for i in range(1, N_CLIENTS + 1):
        state       = random.choice(US_STATES)
        cities      = STATE_CITIES.get(state, [fake.city()])
        city        = random.choice(cities)
        risk        = random.choices(risk_names, weights=risk_weights)[0]
        inc_lo, inc_hi = INCOME_BY_RISK[risk]
        bal_lo, bal_hi = BALANCE_BY_RISK[risk]
        client_since = fake.date_between(start_date="-5y", end_date="today")

        rows.append({
            "account_id":        f"ACC{i:05d}",
            "name":              fake.name(),
            "email":             fake.email(),
            "phone":             fake.numerify("(###) ###-####"),
            "client_since":      client_since,
            "state":             state,
            "city":              city,
            "risk_profile":      risk,
            "manager_id":        random.choice(manager_ids),
            "annual_income":     round(random.uniform(inc_lo, inc_hi), 2),
            "account_balance":   round(random.uniform(bal_lo, bal_hi), 2),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# 4. PORTFOLIOS
# ─────────────────────────────────────────

def generate_portfolios(clients_df, sp500_df):
    rows = []

    sector_tickers = {}
    for _, row in sp500_df.iterrows():
        sector = row["sector"]
        if sector not in sector_tickers:
            sector_tickers[sector] = []
        sector_tickers[sector].append(row["ticker"])

    all_tickers = sp500_df["ticker"].tolist()

    for _, client in clients_df.iterrows():
        risk    = client["risk_profile"]
        profile = RISK_PROFILES[risk]
        n_pos   = profile["avg_positions"] + random.randint(-2, 2)
        n_pos   = max(2, n_pos)

        allowed = profile["allowed_sectors"].split(", ")
        pool    = []
        for sec in allowed:
            pool.extend(sector_tickers.get(sec, []))
        if len(pool) < n_pos:
            pool = all_tickers

        tickers_chosen = random.sample(pool, min(n_pos, len(pool)))
        bal_lo, bal_hi = BALANCE_BY_RISK[risk]
        total_value    = round(random.uniform(bal_lo * 0.5, bal_hi * 0.8), 2)
        created_at     = client["client_since"]

        for j, ticker in enumerate(tickers_chosen):
            weight       = round(random.uniform(0.03, profile["max_stock_weight"]), 4)
            pos_value    = round(total_value * weight, 2)
            avg_price    = round(random.uniform(10, 500), 2)
            quantity     = max(1, int(pos_value / avg_price))
            current_val  = round(quantity * avg_price * random.uniform(0.7, 1.5), 2)

            rows.append({
                "portfolio_id":       f"PRT{client['account_id'][3:]}{j+1:02d}",
                "account_id":         client["account_id"],
                "ticker":             ticker,
                "quantity":           quantity,
                "avg_buy_price":      avg_price,
                "current_value":      current_val,
                "initial_investment": round(quantity * avg_price, 2),
                "created_at":         created_at,
                "status":             random.choices(["active", "closed"], weights=[0.85, 0.15])[0],
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# 5. TRANSACTIONS  (~150k–200k rows)
# ─────────────────────────────────────────

def generate_transactions(clients_df, portfolios_df):
    rows = []
    client_risk = dict(zip(clients_df["account_id"], clients_df["risk_profile"]))

    for _, pos in portfolios_df.iterrows():
        risk        = client_risk.get(pos["account_id"], "Moderate")
        multiplier  = RISK_PROFILES[risk]["transaction_multiplier"]
        n_tx        = random.randint(5 * multiplier, 15 * multiplier)

        created     = pd.to_datetime(pos["created_at"])
        tx_dates    = sorted([
            fake.date_time_between(start_date=created, end_date=END_DATE)
            for _ in range(n_tx)
        ])

        buy_price = pos["avg_buy_price"]

        for k, tx_date in enumerate(tx_dates):
            tx_type   = "buy" if k % 3 != 2 else "sell"
            price     = round(buy_price * random.uniform(0.85, 1.20), 2)
            quantity  = random.randint(1, max(1, pos["quantity"] // 3))
            value     = round(price * quantity, 2)
            commission= round(value * 0.01, 2)  # 1% fee

            if tx_type == "sell":
                sell_price = round(price * random.uniform(0.90, 1.30), 2)
                gain_loss  = round((sell_price - price) * quantity, 2)
                status     = "closed"
            else:
                sell_price = None
                gain_loss  = None
                status     = "open"

            rows.append({
                "transaction_id":   str(uuid.uuid4()),
                "account_id":       pos["account_id"],
                "portfolio_id":     pos["portfolio_id"],
                "ticker":           pos["ticker"],
                "transaction_type": tx_type,
                "quantity":         quantity,
                "price":            price,
                "sell_price":       sell_price,
                "transaction_value":value,
                "commission_fee":   commission,
                "transaction_date": tx_date,
                "status":           status,
                "gain_loss":        gain_loss,
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# 6. DAILY SUMMARY CSV
# ─────────────────────────────────────────

def generate_daily_summary(transactions_df):
    df = transactions_df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date

    summary = df.groupby("transaction_date").agg(
        total_transactions  = ("transaction_id",    "count"),
        total_volume        = ("transaction_value", "sum"),
        total_commissions   = ("commission_fee",    "sum"),
        buy_count           = ("transaction_type",  lambda x: (x == "buy").sum()),
        sell_count          = ("transaction_type",  lambda x: (x == "sell").sum()),
        unique_clients      = ("account_id",        "nunique"),
        unique_tickers      = ("ticker",            "nunique"),
        total_gain_loss     = ("gain_loss",         "sum"),
    ).reset_index()

    summary["avg_commission_per_tx"] = round(
        summary["total_commissions"] / summary["total_transactions"], 2
    )
    summary = summary.round(2)
    return summary


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    engine = get_engine()

    # Load S&P 500 companies from DB
    print("Loading S&P 500 tickers from database...")
    sp500_df = pd.read_sql("SELECT ticker, sector FROM sp500_companies", engine)

    # Generate
    print("Generating risk profiles...")
    risk_df = generate_risk_profiles()

    print("Generating managers...")
    managers_df = generate_managers()

    print("Generating clients...")
    clients_df = generate_clients(managers_df)

    print("Generating portfolios...")
    portfolios_df = generate_portfolios(clients_df, sp500_df)
    print(f"  → {len(portfolios_df):,} portfolio positions")

    print("Generating transactions (this may take a moment)...")
    transactions_df = generate_transactions(clients_df, portfolios_df)
    print(f"  → {len(transactions_df):,} transactions")

    print("Generating daily summary...")
    daily_df = generate_daily_summary(transactions_df)

    # Save Excel (clients + managers + risk profiles)
    print("Saving Excel file...")
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/clients.xlsx")
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        clients_df.to_excel(writer,   sheet_name="clients",       index=False)
        managers_df.to_excel(writer,  sheet_name="managers",      index=False)
        risk_df.to_excel(writer,      sheet_name="risk_profiles",  index=False)
    print(f"  → Saved to {excel_path}")

    # Save CSV
    print("Saving daily summary CSV...")
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/daily_summary.csv")
    daily_df.to_csv(csv_path, index=False)
    print(f"  → Saved to {csv_path}")

    # Save to PostgreSQL
    print("Loading portfolios to PostgreSQL...")
    portfolios_df.to_sql("portfolios", engine, if_exists="replace", index=False, chunksize=1000)

    print("Loading transactions to PostgreSQL...")
    transactions_df.to_sql("transactions", engine, if_exists="replace", index=False, chunksize=1000)

    print("\n✅ All done!")
    print(f"   Clients:      {len(clients_df):,}")
    print(f"   Managers:     {len(managers_df):,}")
    print(f"   Portfolios:   {len(portfolios_df):,}")
    print(f"   Transactions: {len(transactions_df):,}")
    print(f"   Daily rows:   {len(daily_df):,}")


if __name__ == "__main__":
    main()
