#!/usr/bin/env python3
"""Quick sanity check: verifies Alpaca credentials work and prints account info."""
from src.alpaca_client import AlpacaClient
from src.config import Config


def main():
    config = Config.from_env()
    client = AlpacaClient(config)

    account = client.get_account()
    print(f"Connected to Alpaca ({'paper' if config.paper else 'LIVE'} trading)")
    print(f"  Account status : {account.status}")
    print(f"  Cash           : ${account.cash}")
    print(f"  Buying power   : ${account.buying_power}")
    print(f"  Portfolio value: ${account.portfolio_value}")
    print(f"  Market open now: {client.is_market_open()}")


if __name__ == "__main__":
    main()
