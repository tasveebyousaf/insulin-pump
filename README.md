# Insulin Pump

Course project for Software Development Methodologies, University of Debrecen.

A simulation of insulin pump control software: every 10 minutes it reads a blood sugar value, decides whether insulin is needed, delivers a safe dose and logs it. Based on the insulin pump case study in Sommerville, *Software Engineering*. Not real medical software.

## Run it

Needs Python 3, no extra packages.

```
python run_simulation.py     # one simulated day, writes simulation_log.csv
python -m unittest           # tests from the acceptance criteria
```

## Files

| Path | What it is |
|---|---|
| `pump/controller.py` | Dose rule and control loop |
| `pump/devices.py` | Simulated sensor and pump |
| `pump/config.py` | Safe zone and dose limits |
| `data/trace_24h.csv` | 24-hour test sugar trace (144 readings) |
| `tests/` | Tests for the acceptance criteria |
| `docs/requirements.md` | Stakeholders and testable requirements (Session 5) |
| `docs/backlog.md` | Epic, stories, MoSCoW, MVP (Session 6) |
| `scripts/setup-board.ps1` | Creates the GitHub Projects board |
