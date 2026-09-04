# Alpaca Moving-Average Crossover Bot

A polling trading bot for Alpaca's **paper trading** API that trades a single
symbol using a classic moving-average crossover strategy:

- **BUY** when the short-window moving average crosses **above** the long-window average.
- **SELL** (close position) when the short-window average crosses **below** the long-window average.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env and fill in your Alpaca API key/secret
```

`.env` is git-ignored — your credentials never get committed.

### Configuration (`.env`)

| Variable                | Default                              | Description                                    |
|--------------------------|---------------------------------------|-------------------------------------------------|
| `ALPACA_API_KEY`         | *(required)*                          | Your Alpaca API key                             |
| `ALPACA_SECRET_KEY`      | *(required)*                          | Your Alpaca API secret                          |
| `ALPACA_BASE_URL`        | `https://paper-api.alpaca.markets`   | Paper or live trading endpoint                  |
| `SYMBOL`                 | `AAPL`                                | Ticker to trade                                 |
| `QTY`                    | `1`                                   | Shares per buy order                            |
| `SHORT_WINDOW`           | `10`                                  | Short moving-average window (in bars)           |
| `LONG_WINDOW`            | `30`                                  | Long moving-average window (in bars)            |
| `TIMEFRAME`              | `15Min`                               | Bar timeframe (`1Min`, `5Min`, `15Min`, `1Hour`, `1Day`, ...) |
| `POLL_INTERVAL_SECONDS`  | `60`                                  | Seconds between strategy checks                 |

## Usage

**Verify your credentials work:**

```bash
python check_connection.py
```

**Run the bot (long-running loop):**

```bash
python run.py
```

The bot only trades while the market is open, skips a cycle if there's
already a pending order for the symbol, and only buys when it doesn't
already hold a position (and only sells when it does) — so it won't
double up on orders.

**Run tests:**

```bash
pytest tests/ -v
```

## Project layout

```
src/
  config.py         # Loads and validates settings from .env
  alpaca_client.py  # Thin wrapper around the alpaca-py SDK
  strategy.py        # Pure moving-average crossover logic (unit tested)
  trading_bot.py      # Polling loop that wires strategy + client together
tests/
  test_strategy.py   # Unit tests for the strategy, no network required
run.py                # Entry point: starts the polling loop
check_connection.py   # One-off script to sanity-check API credentials
```

## Safety notes

- This bot is configured for the **paper trading** endpoint by default. Do
  not point `ALPACA_BASE_URL` at the live trading endpoint until you've
  tested thoroughly.
- The strategy is intentionally simple (a starting point, not investment
  advice) — there is no stop-loss, position sizing beyond a fixed `QTY`, or
  multi-symbol risk management. Extend `src/strategy.py` and
  `src/trading_bot.py` before using this with real capital.
