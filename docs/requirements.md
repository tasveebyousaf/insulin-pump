# Requirements (Session 5)

## Stakeholders

| Stakeholder | Uses the system? | Needs something an end-user would not ask for |
|---|---|---|
| Patient | Yes | - |
| Doctor (diabetes specialist) | Yes, reads the log | A dose history to adjust treatment |
| Family carer | Sometimes | Alarms they can hear and understand |
| Medical device regulator | No | Proof the device is safe before it is sold |
| Manufacturer / maintenance engineers | No | A way to test and repair the device |
| Health insurer | No | Evidence it reduces hospital visits |

## Goals turned into testable requirements

**1. "The device should be reliable."**
The pump shall deliver the correctly computed dose in at least 99.9% of control cycles, and shall raise an alarm in every cycle where it cannot.
Metric: rate of failure occurrence. Type: product.

**2. "It should be easy for an elderly patient to use."**
After 30 minutes of training, a patient over 65 shall be able to read their last sugar value and respond to an alarm, with no more than one error per week of use.
Metric: training time, error rate. Type: product.
This is the goal that resists: "easy" depends on the person, and measuring the error rate needs a real user study, which is expensive.

**3. "It should run for a long time on one battery."**
The pump shall run for at least 7 days (1,008 control cycles) of normal operation on one battery.
Metric: operating time. Type: product.
