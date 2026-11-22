"""Strategy pattern: one report, many output formats.

Before: generate_report(format_type) and save_report() each had an if/elif per format.
After : one class per format (a "strategy"); the ReportGenerator (the "context")
holds ONE strategy and can swap it at runtime with set_strategy().

Problems with the original code:
1. Adding XML or Markdown means editing two if/elif chains (violates Open/Closed).
2. The format list is duplicated (in generate_report AND in save_report).
3. Each format can't be tested alone; you must go through the whole class.
4. The format is a raw string: a typo ("pfd") silently gives "Unknown format".
5. The file extension logic is separated from the format it belongs to.
"""

import json
from abc import ABC, abstractmethod


# Strategy interface -------------------------------------------------------------
class ReportFormatStrategy(ABC):
    extension: str = ""

    @abstractmethod
    def format(self, data: list[dict]) -> str:
        """Turn the data into the report text."""


# Concrete strategies: one class per format ------------------------------------------
class PDFFormatStrategy(ReportFormatStrategy):
    extension = "pdf"

    def format(self, data):
        lines = ["PDF REPORT", "=" * 50]
        lines += [f"| {item['name']:20} | {item['value']:10} |" for item in data]
        lines += ["=" * 50, "End of PDF Report"]
        return "\n".join(lines)


class ExcelFormatStrategy(ReportFormatStrategy):
    extension = "xlsx"

    def format(self, data):
        lines = ["EXCEL REPORT", "-" * 50, "Name\tValue"]
        lines += [f"{item['name']}\t{item['value']}" for item in data]
        lines += ["-" * 50]
        return "\n".join(lines) + "\n"


class CSVFormatStrategy(ReportFormatStrategy):
    extension = "csv"

    def format(self, data):
        return "name,value\n" + "".join(f"{item['name']},{item['value']}\n" for item in data)


class JSONFormatStrategy(ReportFormatStrategy):
    extension = "json"

    def format(self, data):
        return json.dumps(data, indent=2)


# The final test from the exercise: a NEW format, zero edits to the classes above.
class HTMLFormatStrategy(ReportFormatStrategy):
    extension = "html"

    def format(self, data):
        rows = "\n".join(f"    <tr><td>{item['name']}</td><td>{item['value']}</td></tr>" for item in data)
        return f"<table>\n    <tr><th>Name</th><th>Value</th></tr>\n{rows}\n</table>"


# Context ----------------------------------------------------------------------------
class ReportGenerator:
    def __init__(self, data: list[dict], strategy: ReportFormatStrategy | None = None):
        self.data = data
        self._strategy = strategy or CSVFormatStrategy()

    def set_strategy(self, strategy: ReportFormatStrategy) -> None:
        """Switch format at runtime."""
        self._strategy = strategy

    def generate_report(self) -> str:
        # Polymorphism: we don't know (or care) which format it is.
        return self._strategy.format(self.data)

    def save_report(self, filename: str) -> str:
        path = f"{filename}.{self._strategy.extension}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.generate_report())
        return path


if __name__ == "__main__":
    data = [
        {"name": "Sales Q1", "value": 15000},
        {"name": "Sales Q2", "value": 18000},
        {"name": "Sales Q3", "value": 22000},
        {"name": "Sales Q4", "value": 25000},
    ]
    generator = ReportGenerator(data)

    for title, strategy in [
        ("PDF", PDFFormatStrategy()),
        ("CSV", CSVFormatStrategy()),
        ("JSON", JSONFormatStrategy()),
        ("HTML (NEW!)", HTMLFormatStrategy()),
    ]:
        print(f"=== {title} FORMAT ===")
        generator.set_strategy(strategy)
        print(generator.generate_report())
        print("\n" + "=" * 60 + "\n")
