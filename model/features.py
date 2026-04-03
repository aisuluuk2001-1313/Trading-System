import numpy as np
import pandas as pd


def add_features(df, lookback=14, vm=1.0):
    df = df.copy()

    # -------------------------
    # Date and time-of-day
    # -------------------------
    df["date"] = df["datetime"].dt.date
    df["tod"] = df["datetime"].dt.strftime("%H:%M:%S")

    # Keep regular trading hours only
    df = df[(df["tod"] >= "09:30:00") & (df["tod"] <= "16:00:00")].copy()
    df = df.reset_index(drop=True)

    # -------------------------
    # Daily reference prices
    # -------------------------
    daily_rows = []

    for day, g in df.groupby("date", sort=True):
        g = g.sort_values("datetime")

        open_0930_rows = g[g["tod"] == "09:30:00"]
        close_1600_rows = g[g["tod"] == "16:00:00"]

        if not open_0930_rows.empty:
            open_0930 = float(open_0930_rows.iloc[0]["open"])
        else:
            open_0930 = float(g.iloc[0]["open"])

        if not close_1600_rows.empty:
            close_1600 = float(close_1600_rows.iloc[0]["close"])
        else:
            close_1600 = float(g.iloc[-1]["close"])

        daily_rows.append(
            {
                "date": day,
                "open_0930": open_0930,
                "close_1600": close_1600,
            }
        )

    daily = pd.DataFrame(daily_rows).sort_values("date").reset_index(drop=True)
    daily["prev_close_1600"] = daily["close_1600"].shift(1)

    df = df.merge(daily, on="date", how="left")

    # -------------------------
    # VWAP by day  <<< HERE
    # -------------------------
    df["pv"] = df["close"] * df["volume"]
    df["cum_pv"] = df.groupby("date")["pv"].cumsum()
    df["cum_vol"] = df.groupby("date")["volume"].cumsum()
    df["vwap"] = np.where(df["cum_vol"] > 0, df["cum_pv"] / df["cum_vol"], np.nan)

    # -------------------------
    # Sigma by time-of-day
    # -------------------------
    df["move"] = (df["close"] / df["open_0930"] - 1.0).abs()

    sigma_tbl = (
        df.groupby(["tod", "date"], as_index=False)["move"]
        .last()
        .sort_values(["tod", "date"])
        .reset_index(drop=True)
    )

    sigma_tbl["sigma"] = (
        sigma_tbl.groupby("tod")["move"]
        .transform(lambda s: s.rolling(window=lookback, min_periods=lookback).mean().shift(1))
    )

    sigma_tbl = sigma_tbl.drop(columns=["move"])

    df = df.merge(sigma_tbl, on=["tod", "date"], how="left")

    # -------------------------
    # Gap-adjusted bands
    # -------------------------
    df["base_up"] = np.maximum(df["open_0930"], df["prev_close_1600"])
    df["base_dn"] = np.minimum(df["open_0930"], df["prev_close_1600"])

    df["upper"] = df["base_up"] * (1.0 + vm * df["sigma"])
    df["lower"] = df["base_dn"] * (1.0 - vm * df["sigma"])

    df = df.drop(columns=["pv", "cum_pv", "cum_vol", "base_up", "base_dn"])

    return df