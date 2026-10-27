"""Simulated hardware (tech story: sensor and pump interfaces).

The controller only talks to these two small interfaces, so a real device
could replace the simulation later without changing the controller.
"""


class SimulatedSensor:
    """Returns blood sugar readings from a prepared list (a recorded trace)."""

    def __init__(self, readings):
        self._readings = list(readings)
        self._i = 0

    def read_sugar(self):
        """Next reading, or None when the sensor gives no value."""
        if self._i >= len(self._readings):
            return None
        value = self._readings[self._i]
        self._i += 1
        return value


class SimulatedPump:
    """Holds an insulin reservoir and 'delivers' doses from it."""

    def __init__(self, reservoir_units=100):
        self.reservoir = reservoir_units
        self.delivered_total = 0

    def deliver(self, units):
        if units > self.reservoir:
            raise ValueError("not enough insulin in reservoir")
        self.reservoir -= units
        self.delivered_total += units
