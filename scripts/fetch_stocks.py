import yfinance as yf
import pandas as pd

def get_sp500_tickers():
    """Get S&P 500 tickers from GitHub."""
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
    df = pd.read_csv(url)
    df = df[["Symbol", "Security", "GICS Sector", "GICS Sub-Industry", "Headquarters Location", "Date added", "Founded"]]
    df.columns = ["ticker", "company", "sector", "industry", "headquarters", "date_added", "founded"]
    df["ticker"] = df["ticker"].str.replace(".", "-", regex=False)
    return df

def get_stock_prices(tickers, period="5y"):
    """Download historical prices for a list of tickers."""
    print(f"Downloading prices for {len(tickers)} stocks...")
    raw = yf.download(tickers, period=period, group_by="ticker", auto_adjust=True)

    all_data = []
    for ticker in tickers:
        try:
            df = raw[ticker].copy()
            df["ticker"] = ticker
            df.reset_index(inplace=True)
            df.columns = [c.lower() for c in df.columns]
            all_data.append(df)
        except Exception as e:
            print(f"Skipping {ticker}: {e}")

    return pd.concat(all_data, ignore_index=True)