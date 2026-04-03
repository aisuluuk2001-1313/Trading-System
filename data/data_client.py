import time
import requests
import pandas as pd


def fetch_chunk(api_key, symbol="NFLX", interval="1min", outputsize=5000, end_date=None):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": api_key,
        "format": "JSON",
    }

    if end_date is not None:
        params["end_date"] = end_date

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "values" not in data:
        raise RuntimeError(f"API error: {data}")

    df = pd.DataFrame(data["values"]).copy()
    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(df["datetime"])

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("datetime").reset_index(drop=True)
    df = df.dropna().reset_index(drop=True)

    return df


def fetch_data(api_key, symbol="NFLX", interval="1min", outputsize=5000, months_back=3, sleep_sec=8):
    end_dt = pd.Timestamp.now()
    start_dt = end_dt - pd.DateOffset(months=months_back)

    chunks = []
    current_end = end_dt

    while True:
        end_str = current_end.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Fetching chunk ending at {end_str} ...")

        df = fetch_chunk(
            api_key=api_key,
            symbol=symbol,
            interval=interval,
            outputsize=outputsize,
            end_date=end_str,
        )

        if df.empty:
            break

        # keep only relevant time range
        df = df[df["datetime"] >= start_dt].copy()
        if df.empty:
            break

        chunks.append(df)

        earliest = df["datetime"].min()
        if pd.isna(earliest):
            break

        if earliest <= start_dt:
            break

        # move one minute earlier for next request
        current_end = earliest - pd.Timedelta(minutes=1)

        time.sleep(sleep_sec)

    if not chunks:
        raise RuntimeError("No data downloaded.")

    full_df = pd.concat(chunks, ignore_index=True)
    full_df = full_df.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

    return full_df