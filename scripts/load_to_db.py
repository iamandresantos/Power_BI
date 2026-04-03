from config import get_engine
from fetch_stocks import get_sp500_tickers, get_stock_prices

def load():
    engine = get_engine()

    # Load S&P 500 company list
    print("Fetching S&P 500 company list...")
    companies = get_sp500_tickers()
    companies.to_sql("sp500_companies", engine, if_exists="replace", index=False)
    print(f"Loaded {len(companies)} companies.")

    # Load historical prices
    tickers = companies["ticker"].tolist()
    prices = get_stock_prices(tickers, period="5y")
    prices = prices[["ticker", "date", "open", "high", "low", "close", "volume"]]
    prices.to_sql("stock_prices", engine, if_exists="replace", index=False, chunksize=1000)
    print(f"Loaded {len(prices)} price records.")

if __name__ == "__main__":
    load()
