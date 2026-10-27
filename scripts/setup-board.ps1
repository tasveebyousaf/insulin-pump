# Creates the Session 6 milestone board for the Insulin Pump project on GitHub Projects.
# What it changes on your GitHub account:
#   - creates the repo (private) if it does not exist yet
#   - creates labels in the repo (epic, user-story, tech-story, spike, MoSCoW, story points)
#   - creates 1 epic, 6 user stories, 1 tech story, 1 spike and 5 "won't this time" items as issues
#   - creates a GitHub Project (board) and adds all issues plus 2 notes (MVP sentence, review findings)
#
# Requirements: GitHub CLI installed (winget install GitHub.cli), then:
#   gh auth login
#   gh auth refresh -s project
# Run:  powershell -ExecutionPolicy Bypass -File .\setup-insulin-pump-board.ps1 -Owner tasveebyousaf -RepoName insulin-pump

param(
    [string]$Owner = "tasveebyousaf",
    [string]$RepoName = "insulin-pump",
    [string]$ProjectTitle = "Insulin Pump - Backlog and MVP"
)

$ErrorActionPreference = "Stop"
$Repo = "$Owner/$RepoName"

# ---------- repo ----------
gh repo view $Repo *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Repo $Repo not found - creating it (private)."
    gh repo create $Repo --private --description "Insulin pump control software - SE practice project"
}

# ---------- labels ----------
$labels = @(
    @("epic","5319e7"), @("user-story","0e8a16"), @("tech-story","1d76db"), @("spike","fbca04"),
    @("must","b60205"), @("should","d93f0b"), @("could","c5def5"), @("wont-this-time","cccccc"),
    @("sp-1","ededed"), @("sp-2","ededed"), @("sp-3","ededed"), @("sp-5","ededed"),
    @("sp-8","ededed"), @("sp-13","ededed")
)
foreach ($l in $labels) { gh label create $l[0] --repo $Repo --color $l[1] --force | Out-Null }

# ---------- helper ----------
$tmp = Join-Path $env:TEMP "issue-body.md"
$created = @()
function New-Issue([string]$Title, [string]$Body, [string]$Labels) {
    Set-Content -Path $tmp -Value $Body -Encoding UTF8
    $url = gh issue create --repo $Repo --title $Title --body-file $tmp --label $Labels
    Write-Host "Created: $Title -> $url"
    $script:created += $url
    return $url
}

# ---------- epic ----------
$epicUrl = New-Issue "EPIC: Automatic insulin delivery cycle" @'
**Epic.** Every 10 minutes the pump reads blood sugar, decides whether insulin is needed, delivers a safe dose, and records what it did - without the patient having to intervene.

Too big for one sprint. Split into the user stories, tech story and spike linked below.

Rationale (Sommerville 3.2): blood sugar changes slowly, so measuring every 10 minutes is enough; measuring less often risks high sugar levels.
'@ "epic,must"
$epic = ($epicUrl -split "/")[-1]

# ---------- user stories ----------
New-Issue "US1: Read blood sugar every 10 minutes" @"
Part of #$epic

**As a** patient **I want** the pump to read my blood sugar every 10 minutes **so that** my insulin is adjusted without me doing anything.

Acceptance criteria (summary): a reading is taken and stored every 10 minutes (+/- 10 s); the previous two readings are kept (r0, r1) so the rate of change can be computed.
"@ "user-story,must,sp-3" | Out-Null

New-Issue "US2: Compute and deliver a dose when sugar is rising" @"
Part of #$epic

**As a** patient **I want** the pump to compute and deliver insulin when my sugar is rising **so that** my sugar stays in the safe zone (3-7 units).

Dose rule (Sommerville insulin pump spec, safe zone): if sugar is rising and the rate of increase is increasing, CompDose = round((r2 - r1) / 4); if that rounds to 0, deliver MinimumDose. If sugar is falling or steady, CompDose = 0.

### Acceptance criteria - HAPPY PATH
**Given** the previous readings are r0 = 4.0 and r1 = 4.6, the reservoir holds at least MaxSingleDose, and today's total is below MaxDailyDose
**When** the control cycle runs and the sensor returns r2 = 5.6
**Then** the pump delivers MinimumDose (1 unit), because round((5.6 - 4.6) / 4) = 0
**And** the dose, readings and timestamp are written to the log
**And** r0 becomes 4.6 and r1 becomes 5.6

Also tested: falling sugar (r0 = 6.0, r1 = 5.5, r2 = 5.0) -> dose 0, nothing delivered.
"@ "user-story,must,sp-5" | Out-Null

New-Issue "US3: Never exceed the maximum single or daily dose" @"
Part of #$epic

**As a** patient **I want** the pump to refuse any dose above the single-dose and daily limits **so that** I can never be harmed by an overdose.

### Acceptance criteria - UNHAPPY PATH
**Given** today's cumulative delivered dose already equals MaxDailyDose
**When** the control cycle computes a dose greater than 0
**Then** no insulin is delivered
**And** an alarm is raised saying the daily limit was reached
**And** the refused dose and the reason are written to the log

Also tested: a computed dose above MaxSingleDose is capped at MaxSingleDose; the daily total resets at midnight.
"@ "user-story,must,sp-3" | Out-Null

New-Issue "US4: Alarm on low reservoir or sensor failure" @"
Part of #$epic

**As a** patient **I want** an alarm when the insulin reservoir is low or the sensor stops giving valid readings **so that** I can act before the pump stops working.

Acceptance criteria (summary): reservoir below MaxSingleDose -> alarm, no delivery; sensor returns no reading or a value outside the physically possible range -> alarm, no delivery, event logged.
"@ "user-story,should,sp-3" | Out-Null

New-Issue "US5: Doctor can view the reading and dose log" @"
Part of #$epic

**As a** doctor **I want** to see a log of readings, doses and alarms for a chosen day **so that** I can check the pump behaved correctly and adjust treatment.
"@ "user-story,should" | Out-Null

New-Issue "US6: Patient sees latest reading and last dose on the display" @"
Part of #$epic

**As a** patient **I want** the display to show my latest sugar reading and the last dose delivered **so that** I know what the pump just did.
"@ "user-story,could" | Out-Null

# ---------- tech story ----------
New-Issue "TECH: Define sensor and pump interfaces and the log schema" @"
Part of #$epic

**Tech story** - no user-visible behaviour, but every story above depends on it.

- Define the interface for the blood sugar sensor (readSugar) and the insulin pump (deliver(units), reservoirLevel) so the control loop can run against a simulated device now and a real one later.
- Define the log record: timestamp, r2, computed dose, delivered dose, alarm (if any), reason.
- Fix the constants: MinimumDose, MaxSingleDose, MaxDailyDose, safe zone 3-7.

Done when: interfaces and schema are written down in the repo and the simulated sensor/pump implement them.
"@ "tech-story,must,sp-5" | Out-Null

# ---------- spike ----------
New-Issue "SPIKE: How do we test the control loop without a real sensor? (timebox 4 h)" @"
Part of #$epic

**Spike - timebox: 4 hours.**

**Question to answer:** How do we feed the control loop realistic blood sugar values so we can prove the dose rule and safety limits work over a whole day?

Options to look at: a public glucose dataset, a hand-written 24-hour trace (144 readings), or a simple generated curve with meals.

**Deliverable:** a written decision (which option and why) plus one 24-hour trace file committed to the repo. No feature code.
"@ "spike,must" | Out-Null

# ---------- won't this time ----------
New-Issue "WON'T (this time): Manual dose button / meal bolus" "Explicitly excluded from the MVP. The MVP is automatic delivery only." "wont-this-time" | Out-Null
New-Issue "WON'T (this time): Real hardware integration" "Explicitly excluded. The MVP runs against a simulated sensor and pump." "wont-this-time" | Out-Null
New-Issue "WON'T (this time): Mobile app / Bluetooth connection" "Explicitly excluded from the MVP." "wont-this-time" | Out-Null
New-Issue "WON'T (this time): Sensor calibration workflow" "Explicitly excluded from the MVP." "wont-this-time" | Out-Null
New-Issue "WON'T (this time): Medical certification and clinical validation" "Explicitly excluded. Out of scope for a course project." "wont-this-time" | Out-Null

# ---------- project board ----------
$proj = gh project create --owner $Owner --title $ProjectTitle --format json | ConvertFrom-Json
$num = $proj.number
Write-Host "Created project #$num"
try { gh project link $num --owner $Owner --repo $Repo | Out-Null } catch { Write-Host "Could not link project to repo (optional) - skipping." }

foreach ($u in $created) { gh project item-add $num --owner $Owner --url $u | Out-Null }

gh project item-create $num --owner $Owner --title "MVP sentence" --body "The MVP is done when a patient (simulated) can go through a full day of automatic 10-minute control cycles - reading, dose computation, delivery and safety limits - evidenced by a test run over a recorded 24-hour sugar trace (144 cycles) whose log shows every dose matches the dose rule and no limit was ever exceeded." | Out-Null
gh project item-create $num --owner $Owner --title "Review findings (from reviewing group)" --body "Finding 1: (fill in during Round 4)`nFinding 2: (fill in during Round 4)" | Out-Null

Remove-Item $tmp -ErrorAction SilentlyContinue
Write-Host "`nDone. Open: https://github.com/users/$Owner/projects/$num"
Write-Host "Tip: in the project, switch to Board layout and group by Labels or add a Status column."
