"""Run: python -m retirelab demo|analyze|save|list|show."""
import argparse
import csv
import json
from pathlib import Path
from .engine import analyze, project
from .models import RetirementScenario
from .storage import ScenarioStore

def main(argv=None):
    parser = argparse.ArgumentParser(description="RetireLab retirement simulator")
    parser.add_argument("--db", default="retirelab.sqlite3")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("demo", "analyze"):
        p = commands.add_parser(command)
        p.add_argument("--scenario")
        if command == "analyze":
            p.add_argument("--runs", type=int, default=1000)
            p.add_argument("--seed", type=int, default=42)
            p.add_argument("--output")
            p.add_argument("--csv")
    p = commands.add_parser("save")
    p.add_argument("file")
    commands.add_parser("list")
    p = commands.add_parser("show")
    p.add_argument("id", type=int)
    args = parser.parse_args(argv)
    try:
        if args.command in ("demo", "analyze"):
            scenario = RetirementScenario.from_dict(json.loads(Path(args.scenario).read_text())) if args.scenario else RetirementScenario()
            if args.command == "demo":
                result = project(scenario)
                print(f"Retirement balance: ${result.retirement_balance:,.0f}")
                print(f"Ending balance: ${result.ending_balance:,.0f}")
                print(f"Unfunded spending: ${result.total_shortfall:,.0f}")
                print(f"Fully funded: {result.success}")
            else:
                result = analyze(scenario, args.runs, args.seed)
                print(f"Modeled success: {result.success_rate:.1%}")
                print(f"Median retirement balance: ${result.median_retirement_balance:,.0f}")
                print(f"Median ending balance: ${result.median_ending_balance:,.0f}")
                if args.output:
                    Path(args.output).write_text(json.dumps(result.to_dict(), indent=2))
                if args.csv:
                    with Path(args.csv).open("w", newline="") as handle:
                        writer = csv.writer(handle)
                        writer.writerow(("age", "p10", "p50", "p90"))
                        for row in result.trajectory:
                            writer.writerow((row.age, row.p10, row.p50, row.p90))
        elif args.command == "save":
            scenario = RetirementScenario.from_dict(json.loads(Path(args.file).read_text()))
            print(f"Saved ID: {ScenarioStore(args.db).save(scenario)}")
        elif args.command == "list":
            print(json.dumps(ScenarioStore(args.db).list(), indent=2))
        elif args.command == "show":
            scenario = ScenarioStore(args.db).get(args.id)
            if scenario is None:
                parser.error("Scenario not found")
            print(json.dumps(scenario.to_dict(), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
