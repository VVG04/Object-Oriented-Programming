"""Singleton pattern: a configuration manager.

Before: every module calls load_config() and re-reads config.json (4 reads per request).
After : ConfigManager.get_instance() reads the file ONCE and everybody shares that object.
"""

import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).with_name("config.json")


class ConfigManager:
    _instance = None  # class attribute: shared by the whole program

    def __init__(self, path=DEFAULT_PATH):
        # Guard: building a second one by hand is a mistake, use get_instance().
        if ConfigManager._instance is not None:
            raise RuntimeError("ConfigManager is a singleton: use ConfigManager.get_instance()")
        self.path = Path(path)
        self.load_count = 0
        self._config = self._load()

    def _load(self) -> dict:
        self.load_count += 1
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def get_instance(cls, path=DEFAULT_PATH) -> "ConfigManager":
        """The global access point. Creates the object the first time only."""
        if cls._instance is None:
            cls._instance = cls(path)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Forget the instance. Handy in tests (fresh config for each test)."""
        cls._instance = None

    def get(self, key: str, default=None):
        """Read a nested value with a dotted key: get("database.host")."""
        value = self._config
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value

    def set(self, key: str, value) -> None:
        """Change a value; every module sees it, because they share one object."""
        *parents, last = key.split(".")
        node = self._config
        for part in parents:
            node = node.setdefault(part, {})
        node[last] = value


# The "modules" from the exercise, now using the singleton ---------------------
def connect_database():
    config = ConfigManager.get_instance()
    print(f"Connecting to database at {config.get('database.host')}:{config.get('database.port')}")


def send_email(to: str, subject: str):
    config = ConfigManager.get_instance()
    print(f"Sending email from {config.get('email.sender')} via {config.get('email.smtp_host')}")


def process_payment(amount: float):
    config = ConfigManager.get_instance()
    print(f"Processing {amount}€ in {config.get('payment.environment')} mode")


def start_application():
    config = ConfigManager.get_instance()
    print(f"Starting {config.get('app.name')} (debug={config.get('app.debug')})")


if __name__ == "__main__":
    start_application()
    connect_database()
    send_email("user@test.com", "Welcome")
    process_payment(99.99)

    a = ConfigManager.get_instance()
    b = ConfigManager.get_instance()
    print(f"Same object? {a is b}. File read {a.load_count} time(s).")
