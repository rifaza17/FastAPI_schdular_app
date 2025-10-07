import httpx
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from app.ai_core_service.ai_predict_forecast import ai_predict_forecast
from app.models.stock import Stock
from datetime import datetime
import boto3

API_KEY = "f2e7a1bfb28849c0b225f17511b024fe"
ALPHA_VANTAGE_API_KEY = "NZQJL2M6NN6VJBB8"
RAPIDAPI_KEY = "95453aeeabmsh195f28930e124d1p1abe41jsncdc83fc835cc"
INSIDER_TRADING_API_KEY = "821ee0c49fbeb0a2f9e7c8aac95cb1788c7cd6b4"
INSIDER_TRADING_API_URL = "https://api.quiverquant.com/beta/live/insiders"

async def fetch_and_store_stock(symbol: str, db: AsyncSession):
    async with httpx.AsyncClient() as client:
        today = date.today()
        # Quote
        quote = (await client.get(
            f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={API_KEY}"
        )).json()

        # Profile
        profile = (await client.get(
            f"https://api.twelvedata.com/profile?symbol={symbol}&apikey={API_KEY}"
        )).json()

        # RSI/OBV/MACD with daily interval
        rsi_data = (await client.get(
            f"https://api.twelvedata.com/rsi?symbol={symbol}&interval=1day&apikey={API_KEY}"
        )).json()
        rsi_value = float(rsi_data["values"][0]["rsi"]) if "values" in rsi_data else None

        obv_data = (await client.get(
            f"https://api.twelvedata.com/obv?symbol={symbol}&interval=1day&apikey={API_KEY}"
        )).json()
        obv_value = float(obv_data["values"][0]["obv"]) if "values" in obv_data else None

        macd_data = (await client.get(
            f"https://api.twelvedata.com/macd?symbol={symbol}&interval=1day&apikey={API_KEY}"
        )).json()
        macd_value = float(macd_data["values"][0]["macd"]) if "values" in macd_data else None

        # ema_12 data
        ema_12_data = (await client.get(
            f"https://api.twelvedata.com/ema?symbol={symbol}&interval=1min&time_period=12&apikey={API_KEY}"
        )).json()
        ema12 = float(ema_12_data["values"][0]["ema"]) if "values" in ema_12_data else None

        # ema_26_data
        ema_26_data = (await client.get(
            f"https://api.twelvedata.com/ema?symbol={symbol}&interval=1min&time_period=26&apikey={API_KEY}"
        )).json()
        ema26 = float(ema_26_data["values"][0]["ema"]) if "values" in ema_26_data else None

        # earning
        earning_resp = await client.get(
            f"https://api.twelvedata.com/earnings?symbol={symbol}&apikey={API_KEY}"
        )
        earning_data = earning_resp.json()

        # Keep only earnings with non-null eps_actual
        filtered_earnings = [
            e for e in earning_data.get("earnings", []) if e.get("eps_actual") is not None
        ]

        # dividends
        dividend = (await client.get(
            f"https://api.twelvedata.com/dividends?symbol={symbol}&apikey={API_KEY}"
        )).json()

        dividends = dividend.get("dividends", [])

        news = (await client.get(
            f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        )).json()

        news_data = news.get("feed", [])

        # Intervals
        intervals = {
            "1d": "1min",
            "1w": "5min",
            "1m": "1h",
            "3m": "1day",
            "1y": "1month",
            "5y": "1month",
        }

        histories = {}
        for key, interval in intervals.items():
            res = await client.get(
                f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=200&apikey={API_KEY}"
            )
            data = res.json()
            if "values" in data:
                histories[key] = {
                    "prices": [float(v["close"]) for v in data["values"]][::-1],
                    "labels": [v["datetime"] for v in data["values"]][::-1],
                }

        # Pick a base interval for AI forecast (e.g., 1d intraday)
        history = histories.get("1d", {}).get("prices", [])
        history_labels = histories.get("1d", {}).get("labels", [])
        forecast, sentiment, aiFactor = ai_predict_forecast(history, history_labels)

        # insiderTrading
        insider_trading = await get_insider_trading(client, symbol)

        stock = Stock(
            symbol=quote.get("symbol"),
            price=float(quote.get("close") or 0),
            change=float(quote.get("change") or 0),
            change_percent=quote.get("percent_change", "0%"),
            volume=quote.get("volume", "0"),
            sector=profile.get("sector", "Unknown"),
            sub_category=profile.get("industry", "Unknown"),
            rsi=rsi_value,
            macd=macd_value,
            obv=obv_value,
            dividend=dividends,
            earning=filtered_earnings,
            news=news_data,
            forecast=json.dumps(forecast),
            sentiment=sentiment,
            aiFactor=aiFactor,
            ema12=ema12,
            ema26=ema26,
            updated_at=datetime.utcnow(),
            history_1d=histories.get("1d"),
            history_1w=histories.get("1w"),
            history_1m=histories.get("1m"),
            history_3m=histories.get("3m"),
            history_1y=histories.get("1y"),
            history_5y=histories.get("5y"),
            insider_trading=insider_trading
        )

        # Upsert
        result = await db.execute(select(Stock).where(Stock.symbol == stock.symbol))
        existing = result.scalar_one_or_none()

        if existing:
            for field, value in stock.__dict__.items():
                if field != "_sa_instance_state":
                    setattr(existing, field, value)
        else:
            db.add(stock)

        await db.commit()


async def get_insider_trading(client, symbol):
    headers = {"Authorization": f"Token {INSIDER_TRADING_API_KEY}"}
    url = f"{INSIDER_TRADING_API_URL}?ticker={symbol}"
    response = await client.get(url, headers=headers)
    response.raise_for_status()  # raise error if bad response
    insider_trading = response.json()
    return insider_trading


async def fetch_trending_symbols(region: str = "US"):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-trending-tickers"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    params = {"region": region}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

            top5 = data["finance"]["result"][0]["quotes"][:5]
            return [q["symbol"] for q in top5]

        except Exception as e:
            print("Error fetching trending symbols:", e)
            # fallback list
            return ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]



cw = boto3.client("cloudwatch", region_name="us-west-2")  # use your region

def count_api_call(api_name: str):
    try:
        cw.put_metric_data(
            Namespace="TickerService",
            MetricData=[{
                "MetricName": "ExternalAPICall",
                "Dimensions": [{"Name": "API", "Value": api_name}],
                "Value": 1,
                "Unit": "Count"
            }]
        )
    except Exception:
        # metrics must not break main logic
        pass
