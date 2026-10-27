"""Run the controller over a full day of readings and write the log.

Usage:  python run_simulation.py [trace.csv]
This is the MVP evidence run: 144 cycles, one every 10 minutes.
"""

import csv
import sys

from pump import config
from pump.controller import Controller
from pump.devices import SimulatedPump, SimulatedSensor


def main(trace_path="data/trace_24h.csv", log_path="simulation_log.csv"):
    with open(trace_path) as f:
        rows = list(csv.DictReader(f))
    times = [r["time"] for r in rows]
    readings = [float(r["sugar"]) for r in rows]

    sensor = SimulatedSensor(readings)
    pump = SimulatedPump(reservoir_units=100)
    # assume the two readings before the trace started equal the first reading
    ctrl = Controller(sensor, pump, r0=readings[0], r1=readings[0])

    for t in times:
        ctrl.step(t)

    with open(log_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "reading", "computed", "delivered", "alarm"])
        w.writeheader()
        w.writerows(ctrl.log)

    doses = [r for r in ctrl.log if r["delivered"] > 0]
    alarms = [r for r in ctrl.log if r["alarm"]]
    print(f"Cycles run:        {len(ctrl.log)}")
    print(f"Doses delivered:   {len(doses)} (total {ctrl.daily_total} units)")
    print(f"Largest dose:      {max((r['delivered'] for r in ctrl.log), default=0)} units "
          f"(limit {config.MAX_SINGLE_DOSE})")
    print(f"Daily total limit: {config.MAX_DAILY_DOSE} units -> "
          f"{'OK' if ctrl.daily_total <= config.MAX_DAILY_DOSE else 'EXCEEDED'}")
    print(f"Alarms:            {len(alarms)}")
    print(f"Log written to {log_path}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
