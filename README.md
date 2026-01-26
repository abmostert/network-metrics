# network_metrics

A **minimal, local‑first CLI tool** for logging and evaluating networking activity.

This tool is designed to answer one question reliably:

> **Is my networking system converting attention into real conversations?**

It deliberately avoids dashboards, charts, and premature optimisation. It records facts once, then derives ratios on demand.

---

## Design philosophy

* **Event‑based, append‑only** (nothing is overwritten)
* **Standard library only** (portable, durable)
* **Low cognitive load** (log once, analyse periodically)
* **Metrics serve behaviour, not emotion**

The tool pairs with:

* *Networking Workflow v4.2* (frozen)
* *Snippet Set v1.0* (frozen)

---

## Files created

The CLI uses two files in the working directory:

* `people.json`
  Minimal registry of people you interact with.

* `events.jsonl`
  Append‑only event log (one JSON object per line, timestamped in UTC).

Both are plain text and safe to version‑control if you wish.

---

## Event types

The following events are supported:

* `connection_requested`
* `connection_accepted`
* `legibility_sent`
* `question_sent`
* `reply_received`
* `call_ask_sent`
* `call_agreed`
* `scheduling_sent`
* `call_scheduled`
* `call_completed`

These map directly to the steps in the networking workflow.

---

## Installation

No installation required beyond Python 3.8+.

Place the script in your project directory:

```
./network_metrics.py
```

(Optional) make executable:

```
chmod +x network_metrics.py
```

---

## Basic usage

### 1. Add a person (once)

```
python network_metrics.py add-person \
  --id person \
  --name "Person A."
```

You only need an ID and a display name. Notes are optional.

---

### 2. Log events as they happen

#### Connection request sent

```
python network_metrics.py log \
  --id person \
  --event connection_requested
```

#### Connection accepted

```
python network_metrics.py log \
  --id person \
  --event connection_accepted
```

#### Legibility message sent (L1 / L2)

```
python network_metrics.py log \
  --id person \
  --event legibility_sent \
  --meta '{"snippet":"L1"}'
```

#### Handshake question sent (Q1–Q5)

```
python network_metrics.py log \
  --id person \
  --event question_sent \
  --meta '{"q":"Q1"}'
```

#### Any reply received

```
python network_metrics.py log \
  --id person \
  --event reply_received
```

#### Call ask sent (C1)

```
python network_metrics.py log \
  --id person \
  --event call_ask_sent \
  --meta '{"snippet":"C1c"}'
```

#### Call agreed

```
python network_metrics.py log \
  --id person \
  --event call_agreed
```

#### Scheduling message sent (C2)

```
python network_metrics.py log \
  --id person \
  --event scheduling_sent
```

#### Call scheduled

```
python network_metrics.py log \
  --id person \
  --event call_scheduled
```

#### Call completed (primary success event)

```
python network_metrics.py log \
  --id person \
  --event call_completed
```

---

## Viewing metrics

### Overall metrics

```
python network_metrics.py metrics
```

This prints:

* raw event counts
* derived ratios
* your **chat rate** (primary KPI)

Target chat rate: **8–12%**

---

### Metrics for a time window

Example: January 2026

```
python network_metrics.py metrics \
  --since 2026-01-01 \
  --until 2026-01-31
```

This allows you to compare periods without tracking daily noise.

---

## Key ratios reported

* **Acceptance rate**
  connections accepted / requests sent

* **Reply rate (legibility)**
  replies / L1–L2 sent

* **Reply rate (questions)**
  replies / Q sent

* **Call yes rate**
  calls agreed / C1 sent

* **Booking rate**
  calls scheduled / connections accepted

* **Chat rate (primary KPI)**
  calls completed / connections accepted

* **Completion rate**
  calls completed / calls scheduled

---

## Operating cadence

Recommended rhythm:

* **Log events immediately** when they happen
* **Review metrics weekly** (5–10 minutes)
* **Compare time windows bi‑weekly**
* **Do not change language mid‑trial**

---

## What this tool does *not* do

By design, it does not:

* track likes or comments
* measure impressions or profile views
* show dashboards or charts
* compute rolling averages
* optimise in real time

Those add noise before you have volume.

---

## Mental model

> **Record facts once.
> Interpret patterns periodically.**

If your chat rate sits consistently in the 8–12% band, the system is working. Scale volume, not complexity.

---

## License

Use, modify, and adapt freely for personal workflows.
