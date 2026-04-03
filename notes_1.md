# Task 1: Model Review and Improvement

## 1. Objective

The goal of this task was to review the original intraday momentum strategy, identify its weaknesses, and improve both the model design and code structure. The implementation was rewritten in Python with a focus on modularity, clarity, and reproducibility.


## 2. Weaknesses of the Original Implementation

The original version (R-based) had several limitations:

* Monolithic structure: all logic was implemented in a single script.
* No separation between data handling, feature engineering, and backtesting.
* Limited extensibility and poor readability.


## 3. Improvements in the Python Implementation

### 3.1 Modular Architecture

The system was refactored into a structured project:

* `data/` → data acquisition (Twelve Data API)
* `model/` → features, strategy logic, backtesting
* `analysis/` → performance metrics and plotting
* `main.py` → full pipeline orchestration

This improves maintainability and scalability.


### 3.2 Feature Engineering

The model includes:

* Time-of-day (`tod`)
* Daily reference levels:

  * `open_0930`
  * `close_1600`
  * `prev_close_1600`
* Intraday VWAP
* Time-dependent volatility (`sigma`)
* Gap-adjusted upper and lower bands (noise area)

These features align the implementation with the intraday momentum framework described in the reference paper.


### 3.3 Strategy Logic

The strategy was implemented as:

* Long position when price exceeds the upper band
* Short position when price falls below the lower band
* Trades only at semi-hour intervals (HH:00 and HH:30)

This reduces noise and overtrading.


### 3.4 Backtesting Improvements

A structured backtesting module was developed:

* Explicit position management (long, short, flat)
* Trade logging (entries, exits, PnL)
* End-of-day position closing
* Transaction cost modeling (commission and slippage)
* Avoidance of look-ahead bias

Additionally, a trailing stop mechanism was implemented using:

* current band
* VWAP


### 3.5 Benchmark Comparison

A buy-and-hold benchmark was added to evaluate performance relative to passive investment.



### 3.6 Visualization

Equity curves are plotted for:

* strategy performance
* buy-and-hold benchmark

This enables visual comparison over time.


### 3.7 Multi-Period Data Handling

Instead of a single API request, data is downloaded in multiple chunks to allow analysis over several months.


## 4. Results and Observations

The strategy was tested on multiple assets:

* NFLX:

  * Strong performance
  * High volatility leads to frequent breakout signals

* SPY / QQQ:

  * Weaker performance
  * Lower volatility results in fewer meaningful signals

## 5. Interpretation

The model is sensitive to asset characteristics.

It performs better on high-volatility individual stocks (e.g., NFLX) than on diversified ETFs (e.g., SPY, QQQ).

This suggests that the strategy captures idiosyncratic intraday movements rather than a universal market pattern.


## 6. Limitations

* No dynamic volatility-based position sizing
* Limited historical sample (few months)
* No regime filtering (e.g., VIX conditions)
* Backtesting is partially custom and not based on a full framework
* No real-time trading or broker integration
* Performance varies significantly across assets


## 7. Conclusion

The Python implementation significantly improves the original model in terms of:

* structure
* clarity
* feature richness
* evaluation

However, the strategy remains dependent on asset volatility and is not universally robust. Further improvements could include dynamic position sizing, regime filtering, and integration with a live trading system.
