# Network Metrics (v2 – Tier-Aware, Workflow-Aligned)

A minimal, append-only networking metrics logger and reporter aligned to **Networking Workflow v4.5**.

This tool is designed to:

- Track outbound networking activity
- Segment performance by Tier (A/B/C)
- Enforce give–give–ask discipline
- Produce stable, cohort-safe KPIs
- Avoid spreadsheet sprawl
- Minimise friction

No external dependencies. Standard library only.

---

# Design Philosophy

This tool is not a CRM.

It is a **behaviour tracking instrument**.

Primary objective:

> Improve signal acquisition for entering VC.

Secondary objectives:

- Reduce escalation anxiety
- Monitor tier allocation
- Detect funnel bottlenecks
- Maintain mechanical discipline

The script is:

- Append-only (events.jsonl)
- Human-readable
- Git-friendly
- Backwards compatible

---

# Data Model

## people.json

```json
{
  "person_id": {
    "name": "Full Name",
    "notes": "Optional notes",
    "created_at": "2026-01-15T09:30:00Z",
    "tier": "A"
  }
}
```

## Tier Definitions

- A — Associates / peers / operators
- B — Principals / senior associates
- C — Partners / very senior
- U — Unknown (auto-assigned if tier missing)

Tier is optional. Missing tiers are bucketed as U automatically.

## events.jsonl

Append-only JSON lines file.
Each line:
```json
{
  "ts": "2026-01-16T10:05:00Z",
  "person_id": "jdoe",
  "event": "legibility_sent",
  "meta": {}
}
```

---

# Supported Events (Workflow v4.5 Aligned)

## Core Funnel Events

- ```connection_accepted```
- ```legibility_sent```
- ```value_ping_sent``` ← proactive give
- ```public_comment``` ← proactive give
- ```question_sent```
- ```reprompt_sent```
- ```reply_received```
- ```call_ask_sent```
- ```call_agreed```
- ```call_scheduled```
- ```call_completed```
- ```bow_out_sent```
- ```closed_dormant```

---

# Contribution Model (Give–Give–Ask)

Two contribution types:

## Proactive Give

- ```value_ping_sent```
- ```public_comment```

## Conversational Give

Not explicitly logged — inferred from engagement discipline.

Call asks should follow:
- ≥1 proactive give
- ≥1 meaningful conversational give

---

# Installation

No installation required.

Place the script in your project folder:
```
network_metrics.py
people.json
events.jsonl
```

Run with:
```
python network_metrics.py <command>
```

---

# CLI Commands

## Add person
```Bash
python network_metrics.py add-person \
  --id advikaj \
  --name "Advika Jalan" \
  --tier A
```
Tier is optional.

## Set Tier (Recommended)
Assign tier as you touch people:
```Bash
python network_metrics.py set-tier \
  --id advikaj \
  --tier B
```

## Log event

```Bash
python network_metrics.py log \
  --id advikaj \
  --event legibility_sent
```

With meta:
```Bash
python network_metrics.py log \
  --id advikaj \
  --event question_sent \
  --meta '{"q":"Q3"}'
```

## Generate Metrics

```Bash
python network_metrics.py metrics
```
With date window:
```Bash
python network_metrics.py metrics \
  --since 2026-01-26 \
  --until 2026-02-23
```
Dates are inclusive.

---

# Output Structure

The report includes:

## Overall

- Raw counts
- Cohort-safe ratios
- Headline KPI band

## Per Tier (A/B/C/U)

- Counts
- Ratios

This prevents Tier B/C from distorting Tier A performance.

---

# KPIs (Cohort-Safe)

The script avoids unstable denominators such as "accepted".
Key ratios include:

## Engagement Quality

- ```reply_rate_legibility```
- ```reply_rate_value_ping```
- ```reply_rate_questions```

## Call Funnel Health

- ```call_yes_rate```
- ```schedule_rate_from_yes```
- ```completion_rate```

## Stable Success Indicators

- ```calls_completed_per_legibility```
- ```calls_completed_per_call_ask```

## Give Intensity

- ```proactive_gives_per_legibility```

---

# Headline Band

Primary headline metric:
```
calls_completed_per_legibility
```

Interpretation bands:

- <5% — Early / conservative call volume
- 5–8% — Working; improveable
- 8–12% — Target band
- 12% — Strong; scale volume

---

# Workflow Alignment

This metrics tool assumes:
- 5 working days after legibility
- 5 working days after value ping
- 10 working days after question
- 5 working days after reprompt
- One reprompt maximum
- Tier B shallow depth
- Tier C legibility-only unless engaged
The tool does not enforce the workflow — it reflects it.

---

# Backwards Compatibility

You do NOT need to restart data.
- Missing tier → bucketed as "U"
- Old events remain valid
- New events simply extend the model
No migration required.

---

# Recommended Operating Practice

1. Assign tier only when person becomes active.
2. Log events immediately after they occur.
3. Review metrics weekly.
4. Log friction separately.
5. Avoid redesign during active cycles.

---

# Non-Goals

This tool is NOT:
- A CRM
- A relationship database
- A pipeline forecasting tool
- A lead scoring engine
It is a behaviour instrumentation layer.

---

# Future Extensions (Optional)

- Tier coverage percentage
- Automatic give compliance check
- Per-person funnel state summary
- CSV export
- Streak tracking
- Weekly delta reports

---

# Example Minimal Workflow

```Bash
python network_metrics.py add-person --id jdoe --name "Jane Doe" --tier A
python network_metrics.py log --id jdoe --event connection_accepted
python network_metrics.py log --id jdoe --event legibility_sent
python network_metrics.py log --id jdoe --event value_ping_sent
python network_metrics.py log --id jdoe --event question_sent
python network_metrics.py log --id jdoe --event reply_received
python network_metrics.py log --id jdoe --event call_ask_sent
python network_metrics.py log --id jdoe --event call_agreed
python network_metrics.py log --id jdoe --event call_completed
python network_metrics.py metrics
```

---

# Core Principle

Track behaviour.
Segment by tier.
Optimise signal acquisition.
Avoid emotional interpretation.
Iterate slowly.

---

# License

MIT
