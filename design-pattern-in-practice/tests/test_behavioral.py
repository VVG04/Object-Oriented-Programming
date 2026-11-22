import json

import pytest

from strategy_report import (
    CSVFormatStrategy,
    ExcelFormatStrategy,
    HTMLFormatStrategy,
    JSONFormatStrategy,
    PDFFormatStrategy,
    ReportGenerator,
)
from template_etl import APIPipeline, CSVPipeline, DatabasePipeline, DataPipeline, XMLPipeline

DATA = [{"name": "Sales Q1", "value": 15000}, {"name": "Sales Q2", "value": 18000}]


# ---- Strategy ------------------------------------------------------------------
def test_csv_strategy():
    assert CSVFormatStrategy().format(DATA) == "name,value\nSales Q1,15000\nSales Q2,18000\n"


def test_json_strategy_round_trip():
    assert json.loads(JSONFormatStrategy().format(DATA)) == DATA


@pytest.mark.parametrize(
    "strategy, marker",
    [(PDFFormatStrategy(), "PDF REPORT"), (ExcelFormatStrategy(), "EXCEL REPORT"), (HTMLFormatStrategy(), "<table>")],
)
def test_each_strategy_alone(strategy, marker):
    assert marker in strategy.format(DATA)


def test_switch_strategy_at_runtime():
    gen = ReportGenerator(DATA)
    gen.set_strategy(CSVFormatStrategy())
    csv = gen.generate_report()
    gen.set_strategy(JSONFormatStrategy())
    assert gen.generate_report() != csv


def test_save_uses_the_strategy_extension(tmp_path):
    gen = ReportGenerator(DATA, HTMLFormatStrategy())
    path = gen.save_report(str(tmp_path / "sales_report"))
    assert path.endswith(".html")
    assert "<td>Sales Q1</td>" in open(path).read()


# ---- Template Method -------------------------------------------------------------
@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(DataPipeline, "SIMULATED_DELAY", 0)


@pytest.mark.parametrize(
    "cls, name", [(CSVPipeline, "CSV"), (APIPipeline, "API"), (DatabasePipeline, "Database"), (XMLPipeline, "XML")]
)
def test_every_pipeline_runs_the_same_workflow(cls, name, capsys):
    pipeline = cls("somewhere")
    assert pipeline.run() == f"{name} Pipeline finished"
    steps = [line for line in pipeline.log if line in ("Validation passed", "Cleanup complete")]
    assert steps == ["Validation passed", "Cleanup complete"]
    assert pipeline.data is None  # cleanup ran


def test_transform_steps_are_specific():
    assert CSVPipeline("x").transform([{"id": 1, "name": "bob", "age": "3"}])[0] == {"id": 1, "name": "BOB", "age": 3}
    assert APIPipeline("x").transform([{"user_id": 1, "username": "Al", "score": "95"}])[0]["grade"] == "A"
    assert DatabasePipeline("x").transform([{"product_id": 1, "product_name": "pc", "price": 10}])[0]["tax"] == 2.0


def test_hook_only_in_database_pipeline():
    db, csv = DatabasePipeline("x"), CSVPipeline("x")
    db.run()
    csv.run()
    assert "Opening database transaction" in db.log
    assert "Opening database transaction" not in csv.log


def test_validation_is_enforced_for_everyone():
    class BrokenPipeline(DataPipeline):
        name = "Broken"
        required_fields = ("id", "name")

        def extract(self):
            return [{"id": 1}]  # missing "name"

        def transform(self, data):
            return data

    with pytest.raises(ValueError, match="Invalid record structure"):
        BrokenPipeline("x").run()


def test_base_class_is_abstract():
    with pytest.raises(TypeError):
        DataPipeline("x")
