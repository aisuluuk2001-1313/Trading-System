def generate_signals(df):
    df = df.copy()

    # trade only at HH:00 and HH:30 using datetime column
    df = df[df["datetime"].dt.minute.isin([0, 30])].copy()
    df = df.reset_index(drop=True)

    df["signal"] = 0
    df.loc[df["close"] > df["upper"], "signal"] = 1
    df.loc[df["close"] < df["lower"], "signal"] = -1

    return df