"""Template Method pattern: ETL data pipelines.

Before: CSVPipeline, APIPipeline and DatabasePipeline each copy the same 6-step
run() method (connect, extract, transform, validate, load, cleanup).
After : the base class owns run() (the "template method") and the shared steps;
subclasses only write what is unique to them.

Problems with the original code:
1. validate, load and cleanup are copy-pasted 3 times (~60% of the code).
2. Adding logging to all pipelines means editing 3 classes.
3. Changing the workflow order means editing 3 classes, and they can drift apart.
4. Nothing stops a new pipeline from forgetting the validation step.
"""

import time
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    SIMULATED_DELAY = 0.5  # seconds; tests set it to 0

    def __init__(self, source: str):
        self.source = source
        self.data = None
        self.log: list[str] = []

    # ---- The template method: the workflow is written ONCE, here --------------------
    def run(self) -> str:
        self.connect()
        self.data = self.extract()
        self._say(f"Extracted {len(self.data)} records")
        self.data = self.transform(self.data)
        self._say("Transformation complete")
        self.validate(self.data)
        self.before_load()          # hook
        self.load(self.data)
        self.cleanup()
        self.after_run()            # hook
        return f"{self.name} Pipeline finished"

    # ---- Steps EVERY subclass must write (abstract) -----------------------------------
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def required_fields(self) -> tuple[str, ...]: ...

    @abstractmethod
    def extract(self) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    # ---- Shared steps, implemented once (subclasses MAY override) ----------------------
    def connect(self) -> None:
        self._say(f"Connecting to {self.name}: {self.source}")
        time.sleep(self.SIMULATED_DELAY)
        self._say(f"{self.name} connection established")

    def validate(self, data: list[dict]) -> None:
        self._say("Validating data...")
        for record in data:
            if any(field not in record for field in self.required_fields):
                raise ValueError("Invalid record structure")
        self._say("Validation passed")

    def load(self, data: list[dict]) -> None:
        self._say("Loading data to destination...")
        time.sleep(self.SIMULATED_DELAY)
        self._say(f"Loaded {len(data)} records successfully")

    def cleanup(self) -> None:
        self._say("Cleaning up resources...")
        self.data = None
        self._say("Cleanup complete")

    # ---- Hooks: optional, do nothing by default ---------------------------------------
    def before_load(self) -> None:
        pass

    def after_run(self) -> None:
        pass

    # Logging for ALL pipelines: one change, here.
    def _say(self, message: str) -> None:
        self.log.append(message)
        print(message)


class CSVPipeline(DataPipeline):
    name = "CSV"
    required_fields = ("id", "name")

    def extract(self):
        self._say("Extracting data from CSV...")
        return [{"id": 1, "name": "Alice", "age": 30}, {"id": 2, "name": "Bob", "age": 25}]

    def transform(self, data):
        for record in data:
            record["age"] = int(record["age"])
            record["name"] = record["name"].upper()
        return data


class APIPipeline(DataPipeline):
    name = "API"
    required_fields = ("user_id", "username")

    def extract(self):
        self._say("Extracting data from API...")
        return [
            {"user_id": 101, "username": "charlie", "score": 85},
            {"user_id": 102, "username": "diana", "score": 92},
        ]

    def transform(self, data):
        for record in data:
            record["score"] = int(record["score"])
            record["username"] = record["username"].lower()
            record["grade"] = "A" if record["score"] >= 90 else "B"
        return data


class DatabasePipeline(DataPipeline):
    name = "Database"
    required_fields = ("product_id", "price")

    def extract(self):
        self._say("Extracting data from database...")
        return [
            {"product_id": 501, "product_name": "Laptop", "price": 1200},
            {"product_id": 502, "product_name": "Mouse", "price": 25},
        ]

    def transform(self, data):
        for record in data:
            record["price"] = float(record["price"])
            record["product_name"] = record["product_name"].title()
            record["tax"] = record["price"] * 0.2
        return data

    # Uses a hook: only this pipeline needs it.
    def before_load(self):
        self._say("Opening database transaction")


# The validation test from the exercise: a new pipeline, only the unique parts.
class XMLPipeline(DataPipeline):
    name = "XML"
    required_fields = ("order_id", "amount")

    SAMPLE = """<orders>
  <order id="9001" amount="49.90" status="shipped"/>
  <order id="9002" amount="15.00" status="pending"/>
</orders>"""

    def extract(self):
        import xml.etree.ElementTree as ET

        self._say("Extracting data from XML...")
        root = ET.fromstring(self.SAMPLE)
        return [dict(order.attrib) for order in root]

    def transform(self, data):
        return [
            {"order_id": int(r["id"]), "amount": float(r["amount"]), "status": r["status"].upper()}
            for r in data
        ]


if __name__ == "__main__":
    for pipeline in [
        CSVPipeline("data/users.csv"),
        APIPipeline("https://api.example.com/users"),
        DatabasePipeline("postgresql://localhost/mydb"),
        XMLPipeline("data/orders.xml"),
    ]:
        print(f"RUNNING {pipeline.name.upper()} PIPELINE")
        print("=" * 70)
        print(f"\n{pipeline.run()}\n")
