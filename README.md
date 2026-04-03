# Trading System Backtest

## Overview
This project implements a simple trading system using market data from the Twelve Data API.  
It includes data fetching, feature engineering, signal generation, backtesting with transaction costs, and performance evaluation.  
The strategy is compared against a buy-and-hold benchmark.

## Project Structure
trading-system/

analysis/        # Performance metrics, benchmark, plots  
data/            # Data fetching from API  
model/           # Features, strategy logic, backtesting  
main.py          # Main execution script  
requirements.txt # Dependencies  
Dockerfile       # Optional container setup  

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Create .env file
Create a file named `.env` in the project root:

TWELVEDATA_API_KEY=your_api_key_here

## Run the Project
python main.py

## Functionality
- Fetches historical data via API  
- Applies feature engineering  
- Generates trading signals  
- Runs a backtest with transaction costs and slippage  
- Computes performance metrics  
- Compares results to buy-and-hold  
- Plots equity curves  

## Design Decisions
- Modular structure (data / model / analysis separation)  
- Use of environment variables for API key security  
- Inclusion of transaction costs  
- Benchmark comparison
## Notes
- `.env` is not included for security reasons  
- Each user must provide their own API key
## Future Improvements

- Integration with broker APIs (Alpaca, IBKR)
- Real-time data via WebSocket
- Order execution layer
- Live trading deployment

## Cloud Deployment

The system was containerized using Docker and successfully executed on Google Cloud, confirming that the full pipeline can run in a remote environment.

## Notes
- `.env` is not included for security reasons  
- Each user must provide their own API ke
