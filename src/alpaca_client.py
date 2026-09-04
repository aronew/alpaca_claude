"""Thin wrapper around the alpaca-py SDK for trading + market data."""
import re

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from .config import Config

_TIMEFRAME_UNIT_MAP = {
    "min": TimeFrameUnit.Minute,
    "hour": TimeFrameUnit.Hour,
    "day": TimeFrameUnit.Day,
    "week": TimeFrameUnit.Week,
    "month": TimeFrameUnit.Month,
}

_TIMEFRAME_RE = re.compile(r"^(\d+)\s*(min|hour|day|week|month)s?$", re.IGNORECASE)


def parse_timeframe(value: str) -> TimeFrame:
    """Parse strings like '15Min', '1Hour', '1Day' into a TimeFrame."""
    match = _TIMEFRAME_RE.match(value.strip())
    if not match:
        raise ValueError(
            f"Invalid TIMEFRAME '{value}'. Expected formats like '1Min', '15Min', "
            f"'1Hour', '1Day'."
        )
    amount, unit = match.groups()
    return TimeFrame(int(amount), _TIMEFRAME_UNIT_MAP[unit.lower()])


class AlpacaClient:
    """Wraps the Alpaca trading + market data clients used by the bot."""

    def __init__(self, config: Config):
        self.config = config
        self.trading = TradingClient(
            api_key=config.api_key,
            secret_key=config.secret_key,
            paper=config.paper,
        )
        self.data = StockHistoricalDataClient(
            api_key=config.api_key,
            secret_key=config.secret_key,
        )

    def get_account(self):
        return self.trading.get_account()

    def is_market_open(self) -> bool:
        clock = self.trading.get_clock()
        return bool(clock.is_open)

    def get_recent_bars(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Fetch the most recent `limit` bars for `symbol` as a DataFrame indexed by time."""
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=parse_timeframe(timeframe),
            limit=limit,
        )
        bars = self.data.get_stock_bars(request)
        df = bars.df
        if df.empty:
            return df
        # df is multi-indexed by (symbol, timestamp) when multiple symbols are requested
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level=0)
        return df

    def get_position_qty(self, symbol: str) -> float:
        """Return the current position size for `symbol`, or 0 if none is held."""
        try:
            position = self.trading.get_open_position(symbol)
            return float(position.qty)
        except Exception:
            # Alpaca raises when there's no open position for the symbol.
            return 0.0

    def has_open_orders(self, symbol: str) -> bool:
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus

        request = GetOrdersRequest(status=QueryOrderStatus.OPEN, symbols=[symbol])
        return len(self.trading.get_orders(request)) > 0

    def submit_market_order(self, symbol: str, qty: float, side: OrderSide):
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        return self.trading.submit_order(order_request)

    def buy(self, symbol: str, qty: float):
        return self.submit_market_order(symbol, qty, OrderSide.BUY)

    def sell(self, symbol: str, qty: float):
        return self.submit_market_order(symbol, qty, OrderSide.SELL)
