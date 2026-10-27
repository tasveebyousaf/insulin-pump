"""Constants for the simulated insulin pump.

The dose limits are made-up values for this course project, not medical values.
"""

READING_INTERVAL_MIN = 10   # one reading every 10 minutes (Sommerville req. 3.2)

SAFE_MIN = 3.0              # safe sugar zone: 3-7 units
SAFE_MAX = 7.0

SENSOR_MIN_VALID = 0.5      # readings outside this range are treated as sensor failure
SENSOR_MAX_VALID = 35.0

MIN_DOSE = 1                # units of insulin
MAX_SINGLE_DOSE = 4
MAX_DAILY_DOSE = 25
