import numpy as np
from sklearn.linear_model import LinearRegression

def ai_predict_forecast(history, history_labels):
    """
    history: list of past prices
    history_labels: list of timestamps
    returns forecasts (3M, 6M, 1Y), sentiment, aiFactor
    """
    if not history or len(history) < 5:
        return {"3M": "N/A", "6M": "N/A", "1Y": "N/A"}, "Neutral", "0%"

    prices = np.array(history).reshape(-1, 1)
    X = np.arange(len(prices)).reshape(-1, 1)

    # Train regression
    model = LinearRegression()
    model.fit(X, prices)

    # Predict next 1 year (365 steps ahead)
    next_X = np.arange(len(prices), len(prices) + 365).reshape(-1, 1)
    preds = model.predict(next_X).flatten()

    # Forecast ranges
    def forecast_range(preds, days, label):
        horizon = preds[:days] if len(preds) >= days else preds
        low, high = np.percentile(horizon, [25, 75])
        return f"${low:.2f} - ${high:.2f}"

    forecasts = {
        "3M": forecast_range(preds, 90, "3M"),
        "6M": forecast_range(preds, 180, "6M"),
        "1Y": forecast_range(preds, 365, "1Y")
    }

    # Sentiment: Bullish/Bearish
    last_price = prices[-1][0]
    trend = "Bullish" if preds[-1] > last_price else "Bearish"

    # AI Factor: % move expected in next 7 days
    week_pred = preds[7] if len(preds) > 7 else preds[-1]
    pct_change = ((week_pred - last_price) / last_price) * 100
    aiFactor = f"{pct_change:+.2f}% next 7 days"

    return forecasts, trend, aiFactor