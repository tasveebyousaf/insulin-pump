"""Control loop: read sugar -> compute dose -> apply safety limits -> deliver -> log."""

import math

from pump import config


def round_half_up(x):
    return int(math.floor(x + 0.5))


def compute_dose(r0, r1, r2):
    """Dose rule based on Sommerville's insulin pump specification (US2).

    r0, r1 = previous two readings, r2 = current reading.
    """
    rise = r2 - r1
    previous_rise = r1 - r0

    if r2 < config.SAFE_MIN:
        return 0                                   # sugar low: never give insulin

    if r2 <= config.SAFE_MAX:
        # safe zone: only act when sugar rises and the rise is speeding up
        if rise > 0 and rise > previous_rise:
            return max(round_half_up(rise / 4), config.MIN_DOSE)
        return 0

    # above the safe zone: act unless sugar is already falling
    if rise >= 0:
        return max(round_half_up(rise / 4), config.MIN_DOSE)
    return 0


class Controller:
    def __init__(self, sensor, pump, r0, r1):
        self.sensor = sensor
        self.pump = pump
        self.r0 = r0
        self.r1 = r1
        self.daily_total = 0
        self.log = []

    def new_day(self):
        """Called at midnight: daily dose total starts again (US3)."""
        self.daily_total = 0

    def step(self, time_label=""):
        """Run one 10-minute control cycle and return its log record."""
        r2 = self.sensor.read_sugar()
        record = {"time": time_label, "reading": r2, "computed": 0,
                  "delivered": 0, "alarm": ""}

        # US4: sensor failure
        if r2 is None or not (config.SENSOR_MIN_VALID <= r2 <= config.SENSOR_MAX_VALID):
            record["alarm"] = "SENSOR_FAILURE"
            self.log.append(record)
            return record          # keep old readings, deliver nothing

        dose = compute_dose(self.r0, self.r1, r2)
        record["computed"] = dose

        # US3: safety limits
        if dose > config.MAX_SINGLE_DOSE:
            dose = config.MAX_SINGLE_DOSE
        if dose > 0 and self.daily_total + dose > config.MAX_DAILY_DOSE:
            dose = config.MAX_DAILY_DOSE - self.daily_total
            if dose <= 0:
                dose = 0
                record["alarm"] = "DAILY_LIMIT_REACHED"

        # US4: reservoir check
        if dose > 0 and self.pump.reservoir < dose:
            dose = 0
            record["alarm"] = "RESERVOIR_LOW"

        if dose > 0:
            self.pump.deliver(dose)
            self.daily_total += dose

        record["delivered"] = dose
        self.log.append(record)

        # postcondition from the spec: r0 <- r1, r1 <- r2
        self.r0, self.r1 = self.r1, r2
        return record
