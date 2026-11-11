"""Optional RetireLab API: uvicorn api:app --reload."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from retirelab import RetirementScenario, analyze, project

app = FastAPI(title="RetireLab API", version="1.0.0")

class SimulationRequest(BaseModel):
    scenario: dict
    runs: int = Field(default=1000, ge=1, le=10000)
    seed: int = 42

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/simulations")
def simulate(request: SimulationRequest):
    try:
        return analyze(RetirementScenario.from_dict(request.scenario),
                       runs=request.runs, seed=request.seed).to_dict()
    except (ValueError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/projections")
def projection(payload: dict):
    try:
        result = project(RetirementScenario.from_dict(payload))
        return {"retirement_balance": result.retirement_balance,
                "ending_balance": result.ending_balance,
                "total_shortfall": result.total_shortfall,
                "success": result.success,
                "rows": [vars(row) for row in result.rows]}
    except (ValueError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
