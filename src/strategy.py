"""Moving-average crossover strategy.

Pure functions operating on a pandas Series of closing prices, so they can be
unit tested without hitting the Alpaca API.
"""
from enum import Enum

import pandas as pd


class Signal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


def moving_averages(closes: pd.Series, short_window: int, long_window: int) -> pd.DataFrame:
    """Return a DataFrame with 'short_ma' and 'long_ma' columns."""
    return pd.DataFrame(
        {
            "close": closes,
            "short_ma": closes.rolling(window=short_window).mean(),
            "long_ma": closes.rolling(window=long_window).mean(),
        }
    )


def crossover_signal(closes: pd.Series, short_window: int, long_window: int) -> Signal:
    """Detect a moving-average crossover on the most recent bar.

    Returns BUY if the short MA just crossed above the long MA, SELL if it
    just crossed below, HOLD otherwise (including when there isn't enough
    data yet to compute both averages).
    """
    if len(closes) < long_window + 1:
        return Signal.HOLD

    mas = moving_averages(closes, short_window, long_window)
    if mas["short_ma"].iloc[-2:].isna().any() or mas["long_ma"].iloc[-2:].isna().any():
        return Signal.HOLD

    prev_short, curr_short = mas["short_ma"].iloc[-2], mas["short_ma"].iloc[-1]
    prev_long, curr_long = mas["long_ma"].iloc[-2], mas["long_ma"].iloc[-1]

    crossed_above = prev_short <= prev_long and curr_short > curr_long
    crossed_below = prev_short >= prev_long and curr_short < curr_long

    if crossed_above:
        return Signal.BUY
    if crossed_below:
        return Signal.SELL
    return Signal.HOLD
