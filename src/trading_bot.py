"""Polling loop that runs the moving-average crossover strategy."""
import logging
import time

from .alpaca_client import AlpacaClient
from .config import Config
from .strategy import Signal, crossover_signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("trading_bot")


class TradingBot:
    def __init__(self, config: Config, client: AlpacaClient):
        self.config = config
        self.client = client

    def run_once(self) -> Signal:
        """Run a single check-and-trade cycle. Returns the signal that was acted on."""
        cfg = self.config

        if not self.client.is_market_open():
            log.info("Market is closed. Skipping this cycle.")
            return Signal.HOLD

        if self.client.has_open_orders(cfg.symbol):
            log.info("Open order already pending for %s. Skipping this cycle.", cfg.symbol)
            return Signal.HOLD

        lookback = cfg.long_window + 10
        bars = self.client.get_recent_bars(cfg.symbol, cfg.timeframe, limit=lookback)
        if bars.empty:
            log.warning("No bar data returned for %s.", cfg.symbol)
            return Signal.HOLD

        signal = crossover_signal(bars["close"], cfg.short_window, cfg.long_window)
        position_qty = self.client.get_position_qty(cfg.symbol)

        if signal == Signal.BUY:
            if position_qty > 0:
                log.info(
                    "BUY signal for %s but already holding %s shares. Skipping.",
                    cfg.symbol, position_qty,
                )
                return Signal.HOLD
            log.info("BUY signal for %s. Submitting market order for %s shares.",
                      cfg.symbol, cfg.qty)
            self.client.buy(cfg.symbol, cfg.qty)
            return Signal.BUY

        if signal == Signal.SELL:
            if position_qty <= 0:
                log.info("SELL signal for %s but no open position. Skipping.", cfg.symbol)
                return Signal.HOLD
            log.info("SELL signal for %s. Closing position of %s shares.",
                      cfg.symbol, position_qty)
            self.client.sell(cfg.symbol, position_qty)
            return Signal.SELL

        log.info("No crossover for %s. Holding.", cfg.symbol)
        return Signal.HOLD

    def run_forever(self):
        log.info(
            "Starting bot: symbol=%s short_window=%s long_window=%s timeframe=%s "
            "poll_interval=%ss paper=%s",
            self.config.symbol, self.config.short_window, self.config.long_window,
            self.config.timeframe, self.config.poll_interval_seconds, self.config.paper,
        )
        while True:
            try:
                self.run_once()
            except Exception:
                log.exception("Error during trading cycle. Will retry next cycle.")
            time.sleep(self.config.poll_interval_seconds)


def main():
    config = Config.from_env()
    client = AlpacaClient(config)
    bot = TradingBot(config, client)
    bot.run_forever()


if __name__ == "__main__":
    main()
