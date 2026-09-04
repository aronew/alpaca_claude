"""Configuration loaded from environment variables (.env file)."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            f"Copy .env.example to .env and fill in your Alpaca credentials."
        )
    return value


@dataclass(frozen=True)
class Config:
    api_key: str
    secret_key: str
    base_url: str
    symbol: str
    qty: float
    short_window: int
    long_window: int
    timeframe: str
    poll_interval_seconds: int

    @property
    def paper(self) -> bool:
        return "paper" in self.base_url

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_key=_get_required("ALPACA_API_KEY"),
            secret_key=_get_required("ALPACA_SECRET_KEY"),
            base_url=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
            symbol=os.getenv("SYMBOL", "AAPL"),
            qty=float(os.getenv("QTY", "1")),
            short_window=int(os.getenv("SHORT_WINDOW", "10")),
            long_window=int(os.getenv("LONG_WINDOW", "30")),
            timeframe=os.getenv("TIMEFRAME", "15Min"),
            poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "60")),
        )
