# 📊 S&P 500 Stock Analysis — Power BI Portfolio Project

A end-to-end data analytics project that pulls historical and current stock prices for all S&P 500 companies, stores them in a PostgreSQL database, and visualizes them in Power BI.

Built to demonstrate a full data pipeline: **data ingestion → storage → modeling → visualization**.

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Data Source | Yahoo Finance via `yfinance` |
| Data Processing | Python, Pandas |
| Database | PostgreSQL |
| ORM / Connector | SQLAlchemy, psycopg2 |
| Visualization | Power BI Desktop |
| Version Control | Git, GitHub, pbi-tools |

---

## 📁 Project Structure

```
Power_BI/
├── data/
│   ├── raw/               # Raw source files
│   └── processed/         # Cleaned/transformed data
├── dax/                   # DAX measure definitions
├── docs/                  # Documentation and data dictionary
├── queries/               # M query exports
├── reports/
│   ├── Power_BI_Report.pbix          # Power BI report file
│   └── Power_BI_Report/              # Extracted source (pbi-tools)
│       ├── Model/                    # Data model as JSON
│       ├── Report/                   # Report pages as JSON
│       └── StaticResources/
├── scripts/
│   ├── config.py          # Database connection setup
│   ├── fetch_stocks.py    # Pulls S&P 500 data from Yahoo Finance
│   └── load_to_db.py      # Loads data into PostgreSQL
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

### `sp500_companies`
| Column | Type | Description |
|---|---|---|
| ticker | VARCHAR | Stock ticker symbol |
| company | VARCHAR | Company name |
| sector | VARCHAR | GICS Sector |
| industry | VARCHAR | GICS Sub-Industry |
| headquarters | VARCHAR | HQ location |
| date_added | DATE | Date added to S&P 500 |
| founded | VARCHAR | Year founded |

### `stock_prices`
| Column | Type | Description |
|---|---|---|
| ticker | VARCHAR | Stock ticker symbol |
| date | DATE | Trading date |
| open | FLOAT | Opening price |
| high | FLOAT | Daily high |
| low | FLOAT | Daily low |
| close | FLOAT | Closing price |
| volume | BIGINT | Trading volume |

---

## ⚙️ How to Run

### 1. Clone the repo
```bash
git clone https://github.com/your-username/Power_BI.git
cd Power_BI
```

### 2. Install Python dependencies
```bash
pip install yfinance pandas sqlalchemy psycopg2-binary python-dotenv lxml
```

### 3. Set up environment variables
Create a `.env` file in the root (never committed to git):
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stocks_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Create the PostgreSQL database
```sql
CREATE DATABASE stocks_db;
```

### 5. Run the data pipeline
```bash
cd scripts
python load_to_db.py
```

This will:
- Fetch the S&P 500 company list from a public dataset
- Download 5 years of historical prices for all 500+ stocks (~630k records)
- Load everything into PostgreSQL

### 6. Open Power BI
Open `reports/Power_BI_Report.pbix` and refresh the data source pointing to your local `stocks_db`.

---

## 📈 Key DAX Measures

- **Latest Close** — Most recent closing price per ticker
- **52W High / Low** — 52-week price range
- **YTD Return %** — Year-to-date return percentage

---

## 🔄 Updating Data

To refresh with the latest prices, simply re-run:
```bash
cd scripts
python load_to_db.py
```

---

## 📌 Notes

- `.env` file is gitignored — never commit credentials
- `pbi-tools` is used to extract the `.pbix` into diffable source files
- Data source: [Yahoo Finance](https://finance.yahoo.com) via the `yfinance` library
- S&P 500 constituent list: [datasets/s-and-p-500-companies](https://github.com/datasets/s-and-p-500-companies)
