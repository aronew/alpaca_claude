import pandas as pd
import pytest

from src.strategy import Signal, crossover_signal, moving_averages


def make_closes(values):
    return pd.Series(values, dtype=float)


def test_not_enough_data_holds():
    closes = make_closes([1, 2, 3])
    assert crossover_signal(closes, short_window=2, long_window=5) == Signal.HOLD


def test_bullish_crossover_triggers_buy():
    # Flat, then a dip (short MA falls below long MA), then a sharp spike up
    # that flips the short MA back above the long MA on the very last bar.
    values = [10] * 20 + [5, 6, 30]
    closes = make_closes(values)
    signal = crossover_signal(closes, short_window=3, long_window=10)
    assert signal == Signal.BUY


def test_bearish_crossover_triggers_sell():
    # Mirror image: a rise pulls the short MA above the long MA, then a sharp
    # drop flips it back below on the last bar.
    values = [10] * 20 + [15, 14, -10]
    closes = make_closes(values)
    signal = crossover_signal(closes, short_window=3, long_window=10)
    assert signal == Signal.SELL


def test_no_crossover_holds():
    # Flat, constant series: MAs are equal throughout, never cross.
    closes = make_closes([10] * 20)
    assert crossover_signal(closes, short_window=3, long_window=10) == Signal.HOLD


def test_moving_averages_columns():
    closes = make_closes(range(1, 11))
    mas = moving_averages(closes, short_window=2, long_window=5)
    assert list(mas.columns) == ["close", "short_ma", "long_ma"]
    assert mas["short_ma"].iloc[-1] == pytest.approx((9 + 10) / 2)
    assert mas["long_ma"].iloc[-1] == pytest.approx((6 + 7 + 8 + 9 + 10) / 5)
