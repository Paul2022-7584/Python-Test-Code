"""Typed inputs and validation for the retirement simulator."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any


@dataclass(frozen=True)
class RetirementScenario:
    """All monetary inputs are USD in today's dollars unless stated otherwise.

    Rates are decimals: 0.06 means 6% per year. Contributions occur at year-end.
    The annual spending goal and other income are inflation-adjusted from today.
    """

    name: str = "Baseline"
    current_age: int = 30
    retirement_age: int = 65
    end_age: int = 95
    current_savings: float = 50_000.0
    annual_contribution: float = 12_000.0
    annual_spending: float = 48_000.0
    annual_other_income: float = 18_000.0
    expected_return: float = 0.06
    return_volatility: float = 0.12
    inflation_rate: float = 0.025
    contribution_growth: float = 0.025

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        for field in ("current_age", "retirement_age", "end_age"):
            if type(getattr(self, field)) is not int:
                raise ValueError(f"{field} must be an integer")
        if not (18 <= self.current_age <= 100):
            raise ValueError("current_age must be between 18 and 100")
        if not (self.current_age <= self.retirement_age < self.end_age <= 120):
            raise ValueError("Expected current_age <= retirement_age < end_age <= 120")

        money = ("current_savings", "annual_contribution", "annual_spending", "annual_other_income")
        rates = ("expected_return", "return_volatility", "inflation_rate", "contribution_growth")
        for field in money + rates:
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{field} must be a finite number")
        for field in money:
            if getattr(self, field) < 0:
                raise ValueError(f"{field} cannot be negative")

        bounds = {
            "expected_return": (-0.95, 1.0),
            "return_volatility": (0.0, 1.0),
            "inflation_rate": (-0.10, 0.30),
            "contribution_growth": (-0.10, 0.30),
        }
        for field, (low, high) in bounds.items():
            if not low <= getattr(self, field) <= high:
                raise ValueError(f"{field} must fall between {low} and {high}")

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "RetirementScenario":
        if not isinstance(values, dict):
            raise ValueError("Scenario must be a JSON object")
        try:
            return cls(**values)
        except TypeError as exc:
            raise ValueError(f"Invalid scenario fields: {exc}") from exc

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
