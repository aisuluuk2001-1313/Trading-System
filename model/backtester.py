import pandas as pd
import numpy as np


def backtest(
    df,
    initial_aum,
    commission_per_share=0.0035,
    slippage_per_share=0.001,
):
    dt = df.copy().reset_index(drop=True)

    aum = initial_aum
    position = 0          # 1 = long, -1 = short, 0 = flat
    shares = 0
    entry_price = np.nan

    equity_rows = []
    trade_log = []

    for day in sorted(dt["date"].dropna().unique()):
        day_df = dt[dt["date"] == day].copy().reset_index(drop=True)
        if day_df.empty:
            continue

        px_open = float(day_df.loc[0, "open_0930"])
        if pd.isna(px_open) or px_open <= 0:
            continue

        shares_day = int(np.floor(aum / px_open))
        if shares_day <= 0:
            continue

        day_pnl = 0.0

        for i in range(len(day_df)):
            row = day_df.loc[i]

            if pd.isna(row["upper"]) or pd.isna(row["lower"]) or pd.isna(row["vwap"]):
                continue

            price = float(row["close"])
            open_price_bar = float(row["open"])

            # entry signal: outside noise area
            desired = 0
            if price > row["upper"]:
                desired = 1
            elif price < row["lower"]:
                desired = -1

            # trailing stops from paper:
            # long stop = max(current upper band, VWAP)
            # short stop = min(current lower band, VWAP)
            long_stop = max(float(row["upper"]), float(row["vwap"]))
            short_stop = min(float(row["lower"]), float(row["vwap"]))

            # -------------------------
            # STOP OUT
            # -------------------------
            if position == 1 and price < long_stop:
                exit_px = open_price_bar - slippage_per_share
                pnl = shares * (exit_px - entry_price)
                pnl -= commission_per_share * shares
                day_pnl += pnl

                trade_log.append(
                    {
                        "datetime": row["datetime"],
                        "date": row["date"],
                        "action": "CLOSE_LONG_STOP",
                        "price": exit_px,
                        "shares": shares,
                        "pnl": pnl,
                    }
                )

                position = 0
                shares = 0
                entry_price = np.nan

            elif position == -1 and price > short_stop:
                exit_px = open_price_bar + slippage_per_share
                pnl = shares * (entry_price - exit_px)
                pnl -= commission_per_share * shares
                day_pnl += pnl

                trade_log.append(
                    {
                        "datetime": row["datetime"],
                        "date": row["date"],
                        "action": "CLOSE_SHORT_STOP",
                        "price": exit_px,
                        "shares": shares,
                        "pnl": pnl,
                    }
                )

                position = 0
                shares = 0
                entry_price = np.nan

            # -------------------------
            # ENTER / FLIP
            # -------------------------
            if position == 0 and desired != 0:
                position = desired
                shares = shares_day

                if position == 1:
                    entry_price = open_price_bar + slippage_per_share
                    action = "OPEN_LONG"
                else:
                    entry_price = open_price_bar - slippage_per_share
                    action = "OPEN_SHORT"

                day_pnl -= commission_per_share * shares

                trade_log.append(
                    {
                        "datetime": row["datetime"],
                        "date": row["date"],
                        "action": action,
                        "price": entry_price,
                        "shares": shares,
                        "pnl": np.nan,
                    }
                )

            elif position != 0 and desired != 0 and desired != position:
                # close old
                if position == 1:
                    exit_px = open_price_bar - slippage_per_share
                    pnl = shares * (exit_px - entry_price)
                    close_action = "CLOSE_LONG_FLIP"
                else:
                    exit_px = open_price_bar + slippage_per_share
                    pnl = shares * (entry_price - exit_px)
                    close_action = "CLOSE_SHORT_FLIP"

                pnl -= commission_per_share * shares
                day_pnl += pnl

                trade_log.append(
                    {
                        "datetime": row["datetime"],
                        "date": row["date"],
                        "action": close_action,
                        "price": exit_px,
                        "shares": shares,
                        "pnl": pnl,
                    }
                )

                # open new
                position = desired
                shares = shares_day

                if position == 1:
                    entry_price = open_price_bar + slippage_per_share
                    open_action = "OPEN_LONG"
                else:
                    entry_price = open_price_bar - slippage_per_share
                    open_action = "OPEN_SHORT"

                day_pnl -= commission_per_share * shares

                trade_log.append(
                    {
                        "datetime": row["datetime"],
                        "date": row["date"],
                        "action": open_action,
                        "price": entry_price,
                        "shares": shares,
                        "pnl": np.nan,
                    }
                )

        # -------------------------
        # END-OF-DAY CLOSE
        # -------------------------
        if position != 0 and shares > 0:
            last_row = day_df.iloc[-1]
            last_close = float(last_row["close"])

            if position == 1:
                exit_px = last_close - slippage_per_share
                pnl = shares * (exit_px - entry_price)
                action = "CLOSE_LONG_EOD"
            else:
                exit_px = last_close + slippage_per_share
                pnl = shares * (entry_price - exit_px)
                action = "CLOSE_SHORT_EOD"

            pnl -= commission_per_share * shares
            day_pnl += pnl

            trade_log.append(
                {
                    "datetime": last_row["datetime"],
                    "date": last_row["date"],
                    "action": action,
                    "price": exit_px,
                    "shares": shares,
                    "pnl": pnl,
                }
            )

            position = 0
            shares = 0
            entry_price = np.nan

        aum += day_pnl
        equity_rows.append(
            {
                "datetime": day_df.iloc[-1]["datetime"],
                "date": day,
                "equity": aum,
            }
        )

    result = pd.DataFrame(equity_rows)
    trades = pd.DataFrame(trade_log)

    return result, trades