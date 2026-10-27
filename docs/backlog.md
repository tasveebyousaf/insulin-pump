# Backlog and MVP (Session 6 milestone)

## Epic

**Automatic insulin delivery cycle.** Every 10 minutes the pump reads blood sugar, decides whether insulin is needed, delivers a safe dose, and logs what it did, without the patient having to do anything.

## Items

| ID | Item | Type | MoSCoW | Points |
|---|---|---|---|---|
| US1 | Read blood sugar every 10 minutes | User story | Must | 3 |
| US2 | Compute and deliver a dose when sugar is rising | User story | Must | 5 |
| US3 | Never exceed the maximum single or daily dose | User story | Must | 3 |
| US4 | Alarm on low reservoir or sensor failure | User story | Should | 3 |
| US5 | Doctor can view the reading and dose log | User story | Should | - |
| US6 | Display shows latest reading and last dose | User story | Could | - |
| TECH | Define sensor and pump interfaces and the log schema | Tech story | Must | 5 |
| SPIKE | How do we test the control loop without a real sensor? (timebox 4 h) | Spike | Must | timeboxed |

Points are a starting suggestion. Replace them with the group's planning poker results.

## User stories

- **US1:** As a patient I want the pump to read my blood sugar every 10 minutes so that my insulin is adjusted without me doing anything.
- **US2:** As a patient I want the pump to compute and deliver insulin when my sugar is rising so that it stays in the safe zone (3-7).
- **US3:** As a patient I want the pump to refuse any dose above the single and daily limits so that I can never get an overdose.
- **US4:** As a patient I want an alarm when the reservoir is low or the sensor fails so that I can act before the pump stops working.
- **US5:** As a doctor I want to see the log of readings, doses and alarms so that I can check the pump and adjust treatment.
- **US6:** As a patient I want the display to show my latest reading and last dose so that I know what the pump just did.

## Tech story

Define the sensor interface (`read_sugar`), the pump interface (`deliver`, `reservoir`), the log record (time, reading, computed dose, delivered dose, alarm) and the constants. Done in `pump/devices.py` and `pump/config.py`.

## Spike

**Question:** How do we feed the control loop realistic sugar values to prove it works over a whole day? **Timebox:** 4 hours.
**Decision:** a generated 24-hour trace (144 readings, three meals) in `data/trace_24h.csv`. It is simple, repeatable and needs no external dataset.

## Acceptance criteria

**US2, happy path**
- **Given** the previous readings are r0 = 4.0 and r1 = 4.6, and the reservoir and daily total are fine
- **When** the sensor reads r2 = 5.6
- **Then** the pump delivers the minimum dose (1 unit), because round((5.6 - 4.6) / 4) = 0
- **And** the cycle is logged, and r0 becomes 4.6 and r1 becomes 5.6

**US3, unhappy path**
- **Given** today's delivered total already equals the daily maximum
- **When** a cycle computes a dose above 0
- **Then** no insulin is delivered
- **And** a DAILY_LIMIT_REACHED alarm is raised and logged

Both are automated in `tests/test_controller.py`.

## Won't (this time)

1. Manual dose button / meal dose
2. Real hardware integration
3. Mobile app or Bluetooth connection
4. Sensor calibration workflow
5. Medical certification and clinical validation

## MVP

The MVP is done when a **simulated patient** can go through **a full day of automatic 10-minute control cycles** (reading, dose, delivery, safety limits), evidenced by **a 144-cycle run over `data/trace_24h.csv` whose log shows no dose or daily limit was ever exceeded** (`python run_simulation.py`).

## Review findings (from the reviewing group)

1. _to fill in during Round 4_
2. _to fill in during Round 4_
