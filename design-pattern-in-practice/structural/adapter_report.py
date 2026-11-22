"""Adapter pattern: plug a legacy XML report generator into a JSON dashboard.

We CANNOT modify LegacyReportGenerator (external library) and the dashboard only
reads JSON. The adapter sits in between, like a travel plug adapter: same device,
different socket.
"""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


# Legacy reporting system (can't modify - external library) --------------------
class LegacyReportGenerator:
    def generate_report(self, data: dict) -> str:
        """Returns XML format - old system"""
        xml = "<report>\n"
        for key, value in data.items():
            xml += f"  <{key}>{value}</{key}>\n"
        xml += "</report>"
        return xml


# New analytics dashboard expects JSON -----------------------------------------
class AnalyticsDashboard:
    def display(self, json_data: str):
        data = json.loads(json_data)
        print("=== Analytics Dashboard ===")
        for key, value in data.items():
            print(f"  {key}: {value}")


# The interface the client (our code) expects ------------------------------------
class ReportGeneratorInterface(ABC):
    @abstractmethod
    def generate(self, data: dict) -> str:
        """Return the report as a JSON string."""


# The adapter -------------------------------------------------------------------
class LegacyReportAdapter(ReportGeneratorInterface):
    """Implements the NEW interface by calling the OLD object and translating.

    It uses COMPOSITION (it *has* a legacy generator) rather than inheritance,
    so any object with a generate_report() method can be adapted.
    """

    def __init__(self, legacy: LegacyReportGenerator):
        self._legacy = legacy

    def generate(self, data: dict) -> str:
        xml_report = self._legacy.generate_report(data)  # 1. ask the old system
        return self._xml_to_json(xml_report)              # 2. translate its answer

    @staticmethod
    def _xml_to_json(xml_report: str) -> str:
        """Real conversion from the XML text (no cheating with the original dict).

        XML only stores text, so we turn "150000" back into a number when possible.
        """
        root = ET.fromstring(xml_report)
        result = {}
        for child in root:
            result[child.tag] = LegacyReportAdapter._parse_value(child.text or "")
        return json.dumps(result)

    @staticmethod
    def _parse_value(text: str):
        for cast in (int, float):
            try:
                return cast(text)
            except ValueError:
                pass
        return text


# Business code: knows nothing about XML anymore -----------------------------------
def show_report(generator: ReportGeneratorInterface, dashboard: AnalyticsDashboard, data: dict):
    dashboard.display(generator.generate(data))


if __name__ == "__main__":
    report_generator = LegacyReportAdapter(LegacyReportGenerator())
    dashboard = AnalyticsDashboard()

    show_report(report_generator, dashboard, {"total_sales": 150000, "orders": 1234, "avg_order": 121.55})
    show_report(report_generator, dashboard, {"total_items": 5000, "low_stock": 45, "out_of_stock": 12})
