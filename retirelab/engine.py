"""Dependency-free deterministic and Monte Carlo retirement projection engine.

Model: constant-dollar input assumptions, annual nominal returns (normally
distributed for Monte Carlo), year-end contributions, then inflation-indexed
retirement withdrawals. This is an educational simplified model, not advice.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import random
from typing import Any

from .models import RetirementScenario


@dataclass(frozen=True)
class YearRecord:
    age: int
    balance: float
    contribution: float
    withdrawal: float
    shortfall: float
    phase: str


@dataclass(frozen=True)
class Projection:
    rows: tuple[YearRecord, ...]
    retirement_balance: float
    ending_balance: float
    total_shortfall: float
    success: bool


@dataclass(frozen=True)
class AgeBand:
    age: int
    p10: float
    p50: float
    p90: float


@dataclass(frozen=True)
class SimulationSummary:
    scenario: str
    runs: int
    seed: int
    success_rate: float
    target_at_retirement: float
    deterministic_retirement_balance: float
    deterministic_success: bool
    median_retirement_balance: float
    median_ending_balance: float
    p10_ending_balance: float
    p90_ending_balance: float
    trajectory: tuple[AgeBand, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _percentile(values: list[float], fraction: float) -> float:
    """Linearly interpolate an empirical percentile, with fraction in [0, 1]."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _project(scenario: RetirementScenario, rng: random.Random | None = None) -> Projection:
    balance = float(scenario.current_savings)
    records = [
        YearRecord(scenario.current_age, balance, 0.0, 0.0, 0.0, "starting")
    ]
    total_shortfall = 0.0

    for age in range(scenario.current_age, scenario.end_age):
        elapsed = age - scenario.current_age
        annual_return = (
            scenario.expected_return
            if rng is None or scenario.return_volatility == 0
            else max(-0.95, rng.gauss(scenario.expected_return, scenario.return_volatility))
        )
        available = balance * (1.0 + annual_return)

        if age < scenario.retirement_age:
            contribution = scenario.annual_contribution * (1 + scenario.contribution_growth) ** elapsed
            balance = available + contribution
            withdrawal = 0.0
            shortfall = 0.0
            phase = "saving"
        else:
            spending = scenario.annual_spending * (1 + scenario.inflation_rate) ** elapsed
            other_income = scenario.annual_other_income * (1 + scenario.inflation_rate) ** elapsed
            required = max(0.0, spending - other_income)
            withdrawal = min(available, required)
            shortfall = max(0.0, required - withdrawal)
            total_shortfall += shortfall
            contribution = 0.0
            balance = available - withdrawal
            phase = "retired"

        records.append(YearRecord(age + 1, balance, contribution, withdrawal, shortfall, phase))

    retirement_index = scenario.retirement_age - scenario.current_age
    return Projection(
        rows=tuple(records),
        retirement_balance=records[retirement_index].balance,
        ending_balance=balance,
        total_shortfall=total_shortfall,
        success=total_shortfall < 0.01,
    )


def project(scenario: RetirementScenario) -> Projection:
    """Produce a deterministic projection using the expected annual return."""
    return _project(scenario)


def retirement_target(scenario: RetirementScenario, withdrawal_rate: float = 0.04) -> float:
    """Illustrative 4% rule target, NOT a promised sustainable withdrawal rate."""
    if not 0 < withdrawal_rate <= 1:
        raise ValueError("withdrawal_rate must be in (0, 1]")
    years = scenario.retirement_age - scenario.current_age
    future_net_spending = max(0.0, scenario.annual_spending - scenario.annual_other_income)
    return future_net_spending * (1 + scenario.inflation_rate) ** years / withdrawal_rate


def analyze(
    scenario: RetirementScenario, runs: int = 1000, seed: int = 42
) -> SimulationSummary:
    """Run independently sampled annual-return paths using a local seeded PRNG.

    A path succeeds if its retirement withdrawals have no funding shortfall.
    Success rate is a *model estimate*, not a guarantee or a calibrated forecast.
    """
    if type(runs) is not int or not 1 <= runs <= 10_000:
        raise ValueError("runs must be an integer between 1 and 10000")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")

    baseline = project(scenario)
    rng = random.Random(seed)
    paths = [_project(scenario, rng) for _ in range(runs)]
    success_rate = sum(path.success for path in paths) / runs
    ages = [row.age for row in baseline.rows]
    bands = tuple(
        AgeBand(
            age=age,
            p10=_percentile([path.rows[index].balance for path in paths], 0.10),
            p50=_percentile([path.rows[index].balance for path in paths], 0.50),
            p90=_percentile([path.rows[index].balance for path in paths], 0.90),
        )
        for index, age in enumerate(ages)
    )
    return SimulationSummary(
        scenario=scenario.name,
        runs=runs,
        seed=seed,
        success_rate=success_rate,
        target_at_retirement=retirement_target(scenario),
        deterministic_retirement_balance=baseline.retirement_balance,
        deterministic_success=baseline.success,
        median_retirement_balance=_percentile([p.retirement_balance for p in paths], 0.50),
        median_ending_balance=_percentile([p.ending_balance for p in paths], 0.50),
        p10_ending_balance=_percentile([p.ending_balance for p in paths], 0.10),
        p90_ending_balance=_percentile([p.ending_balance for p in paths], 0.90),
        trajectory=bands,
    )
