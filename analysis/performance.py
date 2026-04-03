import numpy as np


def compute_performance(result):
    equity = result["equity"].copy()

    returns = equity.pct_change().dropna()

    # Total return 
    total_return = equity.iloc[-1] / equity.iloc[0] - 1

    # Annualization factor 
    # If intraday → approximate with 252 trading days
    periods_per_year = 252

    #  Annualized return 
    n_periods = len(returns)
    if n_periods > 0:
        ann_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
    else:
        ann_return = 0

    # Annualized volatility 
    ann_vol = returns.std() * np.sqrt(periods_per_year)

    # Sharpe ratio 
    if ann_vol != 0:
        sharpe = ann_return / ann_vol
    else:
        sharpe = 0

    # Max Drawdown 
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    max_dd = drawdown.min()

    return {
        "Total Return": total_return,
        "Annualized Return": ann_return,
        "Annualized Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd,
    }


def print_performance(result):
    perf = compute_performance(result)

    print("\nPerformance")
    for k, v in perf.items():
        if "Ratio" in k:
            print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: {v:.2%}")