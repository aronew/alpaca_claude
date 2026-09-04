#!/usr/bin/env python3
"""One-off manual test trade: buy 1 share of AAPL (or $SYMBOL) at market price.

This does NOT use the moving-average strategy — it just places a single
market buy order immediately, so you can confirm your Alpaca paper account
and credentials work end-to-end.

Usage:
    python buy_test.py            # buys 1 share of AAPL
    python buy_test.py MSFT 2     # buys 2 shares of MSFT
"""
import sys

from src.alpaca_client import AlpacaClient
from src.config import Config


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    qty = float(sys.argv[2]) if len(sys.argv) > 2 else 1

    config = Config.from_env()
    client = AlpacaClient(config)

    if not config.paper:
        print("Refusing to run: ALPACA_BASE_URL is not a paper-trading endpoint.")
        print(f"  ALPACA_BASE_URL = {config.base_url}")
        sys.exit(1)

    account = client.get_account()
    print(f"Account status: {account.status} | Buying power: ${account.buying_power}")

    if not client.is_market_open():
        print("Market is currently closed. The order will be queued by Alpaca")
        print("and filled at the next market open (still fine for a paper test).")

    print(f"Submitting market BUY order: {qty} share(s) of {symbol}...")
    order = client.buy(symbol, qty)
    print("Order submitted:")
    print(f"  id            : {order.id}")
    print(f"  symbol        : {order.symbol}")
    print(f"  qty           : {order.qty}")
    print(f"  side          : {order.side}")
    print(f"  type          : {order.order_type}")
    print(f"  status        : {order.status}")


if __name__ == "__main__":
    main()
