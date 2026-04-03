import pandas as pd


def build_buy_and_hold(df, initial_aum):
    bench = df.copy().reset_index(drop=True)

    # if date does not exist for some reason, create it from datetime
    if "date" not in bench.columns:
        bench["date"] = pd.to_datetime(bench["datetime"]).dt.date

    daily = bench.groupby("date", as_index=False).last().copy()
    daily["return"] = daily["close"].pct_change()
    daily["equity"] = initial_aum * (1 + daily["return"].fillna(0)).cumprod()

    return daily