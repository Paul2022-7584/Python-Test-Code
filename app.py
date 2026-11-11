"""Optional RetireLab dashboard: streamlit run app.py."""
import json
import pandas as pd
import streamlit as st
from retirelab import RetirementScenario, analyze, project
from retirelab.storage import ScenarioStore

st.set_page_config(page_title="RetireLab", page_icon="📊", layout="wide")
st.title("RetireLab | Retirement Scenario Studio")
st.caption("Interactive financial simulations for education and software demonstration. Not financial advice.")
with st.sidebar:
    st.header("Scenario assumptions")
    name = st.text_input("Scenario name", "Baseline")
    age = st.number_input("Current age", 18, 100, 30)
    retirement = st.number_input("Retirement age", int(age), 110, max(int(age), 65))
    horizon = st.number_input("Planning end age", int(retirement) + 1, 120, max(95, int(retirement) + 1))
    savings = st.number_input("Current savings ($)", min_value=0.0, value=50000.0, step=1000.0)
    contribution = st.number_input("Annual contribution ($)", min_value=0.0, value=12000.0, step=1000.0)
    spending = st.number_input("Retirement spending ($/year, today's dollars)", min_value=0.0, value=48000.0, step=1000.0)
    income = st.number_input("Other retirement income ($/year, today's dollars)", min_value=0.0, value=18000.0, step=1000.0)
    rate = st.slider("Expected return (%)", -10.0, 20.0, 6.0, 0.5)
    volatility = st.slider("Return volatility (%)", 0.0, 40.0, 12.0, 0.5)
    inflation = st.slider("Inflation (%)", -2.0, 15.0, 2.5, 0.5)
    growth = st.slider("Contribution growth (%)", -2.0, 15.0, 2.5, 0.5)
    runs = st.select_slider("Simulation paths", [100, 250, 500, 1000, 2000], value=1000)
    seed = st.number_input("Random seed", value=42, step=1)

scenario = RetirementScenario(
    name=name, current_age=int(age), retirement_age=int(retirement), end_age=int(horizon),
    current_savings=savings, annual_contribution=contribution, annual_spending=spending,
    annual_other_income=income, expected_return=rate / 100,
    return_volatility=volatility / 100, inflation_rate=inflation / 100,
    contribution_growth=growth / 100,
)
sim = analyze(scenario, runs=int(runs), seed=int(seed))
baseline = project(scenario)
a, b, c, d = st.columns(4)
a.metric("Modeled success", f"{sim.success_rate:.1%}")
b.metric("Median retirement balance", f"${sim.median_retirement_balance:,.0f}")
c.metric("Median ending balance", f"${sim.median_ending_balance:,.0f}")
d.metric("Illustrative 4% target", f"${sim.target_at_retirement:,.0f}")
st.subheader("Simulated investment trajectories")
bands = pd.DataFrame([{"Age": row.age, "10th percentile": row.p10, "Median": row.p50,
                       "90th percentile": row.p90} for row in sim.trajectory]).set_index("Age")
st.line_chart(bands)
st.caption("Percentiles are hypothetical model outcomes, not calibrated predictions.")
st.subheader("Deterministic annual ledger")
ledger = pd.DataFrame([vars(row) for row in baseline.rows])
st.dataframe(ledger, hide_index=True, use_container_width=True)
st.download_button("Export ledger CSV", ledger.to_csv(index=False), "projection.csv", "text/csv")
st.download_button("Export scenario JSON", json.dumps(scenario.to_dict(), indent=2),
                   "scenario.json", "application/json")
st.subheader("Local scenario database")
if st.button("Save this scenario"):
    identifier = ScenarioStore().save(scenario)
    st.success(f"Scenario saved locally with ID {identifier}")
st.dataframe(pd.DataFrame(ScenarioStore().list()), hide_index=True, use_container_width=True)
st.info("Simplified annual model: no taxes, fees, healthcare costs, account-specific rules, or correlated returns. Use for learning only.")
