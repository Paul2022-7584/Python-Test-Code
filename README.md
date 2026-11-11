# RetireLab — Python Retirement Simulation Studio

**From an introductory retirement calculator to a modular Python simulation and visualization project.**

RetireLab expands the original Liberty University CSIS 110 program, preserved as [PaulFarri_Retire.py](PaulFarri_Retire.py), into a portfolio-oriented demonstration of software engineering, numerical modeling, persistence, API development and testing.

> Educational demonstration only. Not financial advice. Success rates and percentiles are hypothetical model outputs, not calibrated forecasts or guarantees.

## Features

- Validated, typed retirement scenarios with configurable savings, contributions, returns, inflation, retirement dates, spending and outside income.
- Deterministic year-by-year projections, with detailed contribution, withdrawal and spending-shortfall records.
- Reproducible Monte Carlo annual-return simulations with percentile bands and modeled funding success.
- Interactive Streamlit dashboard with charts, controls, local SQLite saving and downloadable CSV/JSON data.
- Standard-library CLI with JSON input, SQLite scenario management and machine-readable exports.
- Optional FastAPI service with OpenAPI documentation and JSON responses.
- Automated unit tests and GitHub Actions workflow across Python 3.11–3.13.

## Run from source (Python 3.11+)

Clone this repository and run these commands from its root directory.

### No-dependency CLI

```bash
python -m retirelab demo
python -m retirelab analyze --scenario examples/baseline.json --runs 1000 --seed 42
python -m retirelab analyze --scenario examples/baseline.json --output summary.json --csv trajectory.csv
python -m unittest discover -s tests -v
```

Save a scenario locally in SQLite:

```bash
python -m retirelab save examples/baseline.json
python -m retirelab list
python -m retirelab show 1
```

### Interactive dashboard

```bash
python -m pip install -r requirements-dashboard.txt
streamlit run app.py
```

Streamlit will display a local browser URL (typically http://localhost:8501).

### REST API

```bash
python -m pip install -r requirements-api.txt
uvicorn api:app --reload
```

Explore endpoints at http://127.0.0.1:8000/docs. Available endpoints: GET /health, POST /v1/projections and POST /v1/simulations.

An example JSON request for POST /v1/simulations:

```json
{
  "scenario": {"name": "Example", "current_age": 35, "retirement_age": 65, "end_age": 95},
  "runs": 100,
  "seed": 42
}
```

## Repository structure

```text
PaulFarri_Retire.py           Original course assignment (preserved)
retirelab/models.py           Dataclass inputs and validation
retirelab/engine.py           Deterministic projections and Monte Carlo analysis
retirelab/storage.py          SQLite persistence
retirelab/cli.py              Argument-based command-line interface
retirelab/__main__.py         python -m retirelab entrypoint
app.py                        Streamlit interactive dashboard
api.py                        FastAPI JSON service
examples/baseline.json       Reproducible example configuration
tests/test_engine.py          Regression and edge-case tests
.github/workflows/           CI checks
```

## Modeling choices

RetireLab models years rather than months. Returns and contributions occur once per year; nominal returns are applied first, followed by contributions before retirement or withdrawals after retirement. Today's spending requirements and outside income are adjusted for inflation. Withdrawals cannot exceed available balance; any remaining requirement is recorded as an unfunded shortfall. A simulated path succeeds if it has no spending shortfall through the planning horizon.

Each Monte Carlo path independently samples annual nominal returns from a normal distribution, bounded below at -95%. The seed makes results repeatable; it does not make them accurate predictions. The display also includes an illustrative 4% withdrawal-rate target, not a sustainable-withdrawal guarantee.

**Not modeled:** taxes, investment fees, account types, portfolio rebalancing, historical return dependencies, changing Social Security eligibility, life expectancy uncertainty, medical costs, RMDs, or advanced asset allocation. The optional API has no authentication or rate limiting; do not expose it publicly without production safeguards. Do not enter sensitive personal data into public instances.

## Original project versus expanded project

| Original coursework | RetireLab |
| --- | --- |
| Five terminal prompts | Validated JSON-backed scenario models |
| Two conditional branches | Multi-decade simulations and funding shortfalls |
| Printed messages only | Interactive charts, API responses and exports |
| No persistent saved scenarios | Parameterized SQLite storage |
| No tests | Unit tests and CI configuration |

## Why this is a portfolio project

The preserved original file documents where the idea began. New standalone components demonstrate separation of concerns, type-safe data modeling, input validation, testable business logic, reproducible statistical simulation, persisted records, basic web API design and visual analytics. This is an educational prototype, not a commercial financial-planning platform.

## Potential next milestones

1. Validate simulation calibration and compare results against historical bootstrap scenarios.
2. Extend to taxes, withdrawals from account types, asset allocation and fees.
3. Add scenario comparison tables, sensitivity sweeps, and exportable PDF reports.
4. Add authenticated user accounts and migration-managed persistence before public deployment.
