import matplotlib.pyplot as plt
import pandas as pd


def plot_equity(strategy_df, benchmark_df, asset_name):
    strat = strategy_df.copy()
    bench = benchmark_df.copy()

    strat["datetime"] = pd.to_datetime(strat["datetime"])
    bench["date"] = pd.to_datetime(bench["date"])

    strat["date"] = strat["datetime"].dt.date
    strat_daily = strat.groupby("date", as_index=False)["equity"].last()
    strat_daily["date"] = pd.to_datetime(strat_daily["date"])

    bench_daily = bench.copy()
    bench_daily["date"] = pd.to_datetime(bench_daily["date"])

    plt.figure(figsize=(10, 6))
    plt.plot(strat_daily["date"], strat_daily["equity"], label="Strategy")
    plt.plot(bench_daily["date"], bench_daily["equity"], label="Buy & Hold")

    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.title(f"{asset_name}: Strategy vs Buy & Hold")
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{asset_name}_equity.png")
    plt.show()