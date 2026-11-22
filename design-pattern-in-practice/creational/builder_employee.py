"""Builder pattern: HR employee onboarding.

Before: create_employee() with 17 positional parameters ("telescoping constructor").
After : an Employee data class + a fluent EmployeeBuilder whose methods read like a
sentence and can be chained, plus preset builders (DeveloperBuilder, InternBuilder).
"""

from dataclasses import dataclass, asdict
from typing import Optional


# 1. The product: a plain data container -------------------------------------
@dataclass
class Employee:
    # @dataclass writes __init__, __repr__ and __eq__ for us.
    first_name: str
    last_name: str
    email: str
    department: str
    position: str
    salary: float
    start_date: str
    manager_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    has_parking: bool = False
    has_laptop: bool = False
    has_vpn_access: bool = False
    has_admin_rights: bool = False
    office_location: Optional[str] = None
    contract_type: str = "permanent"

    def to_dict(self) -> dict:
        return asdict(self)


# 2. The builder ---------------------------------------------------------------
class EmployeeBuilder:
    """Collect the settings step by step, check them once in build()."""

    def __init__(self):
        self._data: dict = {"start_date": "TBD"}

    # Every with_* method stores a value and returns self -> calls can be chained.
    def with_name(self, first_name: str, last_name: str) -> "EmployeeBuilder":
        self._data["first_name"] = first_name
        self._data["last_name"] = last_name
        return self

    def with_email(self, email: str) -> "EmployeeBuilder":
        self._data["email"] = email
        return self

    def with_job(self, department: str, position: str, salary: float) -> "EmployeeBuilder":
        self._data.update(department=department, position=position, salary=salary)
        return self

    def with_start_date(self, start_date: str) -> "EmployeeBuilder":
        self._data["start_date"] = start_date
        return self

    def with_manager(self, manager_id: int) -> "EmployeeBuilder":
        self._data["manager_id"] = manager_id
        return self

    def with_contact(self, phone=None, address=None, emergency_contact=None) -> "EmployeeBuilder":
        self._data.update(phone=phone, address=address, emergency_contact=emergency_contact)
        return self

    def with_equipment(self, laptop: bool = False, parking: bool = False) -> "EmployeeBuilder":
        self._data.update(has_laptop=laptop, has_parking=parking)
        return self

    def with_access(self, vpn: bool = False, admin: bool = False) -> "EmployeeBuilder":
        self._data.update(has_vpn_access=vpn, has_admin_rights=admin)
        return self

    def with_office(self, office_location: str) -> "EmployeeBuilder":
        self._data["office_location"] = office_location
        return self

    def with_contract(self, contract_type: str) -> "EmployeeBuilder":
        self._data["contract_type"] = contract_type
        return self

    def build(self) -> Employee:
        """Validation lives in ONE place, and runs before the object exists."""
        d = self._data
        if not d.get("first_name") or not d.get("last_name"):
            raise ValueError("Name is required")
        if "@" not in (d.get("email") or ""):
            raise ValueError("Valid email is required")
        if "position" not in d:
            raise ValueError("Job (department, position, salary) is required")
        if d["salary"] < 0:
            raise ValueError("Salary cannot be negative")
        return Employee(**d)


# Presets: subclasses that pre-fill sensible defaults ("hidden logic" made explicit)
class DeveloperBuilder(EmployeeBuilder):
    """A senior developer ALWAYS gets laptop, VPN and admin rights."""

    def __init__(self, first_name: str, last_name: str, email: str):
        super().__init__()
        (
            self.with_name(first_name, last_name)
            .with_email(email)
            .with_job("Engineering", "Senior Developer", 75000)
            .with_equipment(laptop=True)
            .with_access(vpn=True, admin=True)
            .with_office("Paris HQ")
        )


class InternBuilder(EmployeeBuilder):
    """Interns get a laptop but no VPN or admin rights."""

    def __init__(self, first_name: str, last_name: str, email: str, department: str):
        super().__init__()
        (
            self.with_name(first_name, last_name)
            .with_email(email)
            .with_job(department, "Intern", 15000)
            .with_equipment(laptop=True)
            .with_contract("internship")
            .with_office("Paris HQ")
        )


if __name__ == "__main__":
    # Fluent, readable creation: no more guessing what "False, True, True" means.
    employee = (
        EmployeeBuilder()
        .with_name("John", "Doe")
        .with_email("john.doe@company.com")
        .with_job("Engineering", "Senior Developer", 75000)
        .with_start_date("2024-01-15")
        .with_equipment(laptop=True, parking=False)
        .with_access(vpn=True, admin=True)
        .build()
    )
    print(employee)

    # Or use a preset, and still customise it before build()
    dev = DeveloperBuilder("John", "Doe", "john.doe@company.com").with_start_date("2024-01-15").build()
    intern = (
        InternBuilder("Jane", "Smith", "jane.smith@company.com", "Marketing")
        .with_manager(42)
        .with_start_date("2024-02-01")
        .build()
    )
    print(dev)
    print(intern)
