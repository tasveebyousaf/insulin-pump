"""Tests written from the acceptance criteria in docs/backlog.md.

Run with:  python -m unittest
"""

import unittest

from pump import config
from pump.controller import Controller, compute_dose
from pump.devices import SimulatedPump, SimulatedSensor


def make(readings, r0, r1, reservoir=100):
    pump = SimulatedPump(reservoir)
    return Controller(SimulatedSensor(readings), pump, r0, r1), pump


class TestUS2DoseRule(unittest.TestCase):
    def test_happy_path_rising_sugar_gets_minimum_dose(self):
        # Given r0=4.0, r1=4.6 / When sensor reads 5.6 / Then MinimumDose is delivered
        ctrl, pump = make([5.6], r0=4.0, r1=4.6)
        rec = ctrl.step()
        self.assertEqual(rec["delivered"], config.MIN_DOSE)
        self.assertEqual(pump.delivered_total, config.MIN_DOSE)
        self.assertEqual(len(ctrl.log), 1)                 # logged
        self.assertEqual((ctrl.r0, ctrl.r1), (4.6, 5.6))   # readings shifted

    def test_falling_sugar_gets_no_dose(self):
        self.assertEqual(compute_dose(6.0, 5.5, 5.0), 0)

    def test_low_sugar_never_gets_insulin(self):
        self.assertEqual(compute_dose(2.0, 2.5, 2.9), 0)

    def test_high_rising_sugar_gets_bigger_dose(self):
        self.assertEqual(compute_dose(8.0, 9.0, 15.0), 2)   # round(6/4) = 2


class TestUS3SafetyLimits(unittest.TestCase):
    def test_unhappy_path_daily_limit_reached(self):
        # Given today's total equals MaxDailyDose / When a dose > 0 is computed
        # Then nothing is delivered, an alarm is raised, and it is logged
        ctrl, pump = make([5.6], r0=4.0, r1=4.6)
        ctrl.daily_total = config.MAX_DAILY_DOSE
        rec = ctrl.step()
        self.assertGreater(rec["computed"], 0)
        self.assertEqual(rec["delivered"], 0)
        self.assertEqual(rec["alarm"], "DAILY_LIMIT_REACHED")
        self.assertEqual(pump.delivered_total, 0)
        self.assertIn(rec, ctrl.log)

    def test_single_dose_is_capped(self):
        ctrl, _ = make([30.0], r0=8.0, r1=9.0)   # round(21/4) = 5 > max 4
        rec = ctrl.step()
        self.assertEqual(rec["delivered"], config.MAX_SINGLE_DOSE)

    def test_daily_total_resets(self):
        ctrl, _ = make([5.6], r0=4.0, r1=4.6)
        ctrl.daily_total = config.MAX_DAILY_DOSE
        ctrl.new_day()
        self.assertEqual(ctrl.step()["delivered"], config.MIN_DOSE)


class TestUS4Alarms(unittest.TestCase):
    def test_sensor_failure_raises_alarm(self):
        ctrl, pump = make([None], r0=4.0, r1=4.6)
        rec = ctrl.step()
        self.assertEqual(rec["alarm"], "SENSOR_FAILURE")
        self.assertEqual(pump.delivered_total, 0)

    def test_impossible_reading_raises_alarm(self):
        ctrl, _ = make([99.0], r0=4.0, r1=4.6)
        self.assertEqual(ctrl.step()["alarm"], "SENSOR_FAILURE")

    def test_low_reservoir_blocks_delivery(self):
        ctrl, pump = make([5.6], r0=4.0, r1=4.6, reservoir=0)
        rec = ctrl.step()
        self.assertEqual(rec["alarm"], "RESERVOIR_LOW")
        self.assertEqual(rec["delivered"], 0)


class TestMVPFullDay(unittest.TestCase):
    def test_full_day_never_breaks_limits(self):
        import csv
        with open("data/trace_24h.csv") as f:
            readings = [float(r["sugar"]) for r in csv.DictReader(f)]
        ctrl, _ = make(readings, readings[0], readings[0])
        for _ in readings:
            ctrl.step()
        self.assertEqual(len(ctrl.log), 144)
        self.assertTrue(all(r["delivered"] <= config.MAX_SINGLE_DOSE for r in ctrl.log))
        self.assertLessEqual(ctrl.daily_total, config.MAX_DAILY_DOSE)


if __name__ == "__main__":
    unittest.main()
