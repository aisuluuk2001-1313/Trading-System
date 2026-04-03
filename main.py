from data.data_client import fetch_data
from model.features import add_features
from model.strategy import generate_signals
from model.backtester import backtest
from analysis.performance import compute_performance
from analysis.benchmark import build_buy_and_hold
from analysis.plots import plot_equity
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TWELVEDATA_API_KEY")

if not API_KEY:
    raise ValueError("TWELVEDATA_API_KEY not found in .env file")

INTERVAL = "15min"
OUTPUTSIZE = 5000
INITIAL_AUM = 100000.0
ASSETS = ["NFLX", "SPY", "QQQ"]


def run_asset(symbol):
    raw_df = fetch_data(
        api_key=API_KEY,
        symbol=symbol,
        interval=INTERVAL,
        outputsize=OUTPUTSIZE,
        months_back=3,
        sleep_sec=8,
    )

    df = add_features(raw_df, lookback=5, vm=1.0)
    df = generate_signals(df)

    result, _ = backtest(
        df,
        INITIAL_AUM,
        commission_per_share=0.0035,
        slippage_per_share=0.001,
    )

    benchmark = build_buy_and_hold(df, INITIAL_AUM)

    strat_perf = compute_performance(result)
    bench_perf = compute_performance(benchmark)

    return strat_perf, bench_perf, result, benchmark


def main():
    print("\nComparison\n")

    for asset in ASSETS:
        strat, bench, result, benchmark = run_asset(asset)

        print(f"--- {asset} ---")
        print(f"Strategy Return: {strat['Total Return']:.2%}")
        print(f"Strategy Sharpe: {strat['Sharpe Ratio']:.2f}")
        print(f"Strategy Max DD: {strat['Max Drawdown']:.2%}")
        print(f"Buy&Hold Return: {bench['Total Return']:.2%}")
        print()

        plot_equity(result, benchmark, asset)


if __name__ == "__main__":
    main()