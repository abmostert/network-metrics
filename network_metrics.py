#!/usr/bin/env python3
"""
network_metrics.py — minimal networking metrics logger + reporter (standard library only)

Data model:
- people.json  : { "<person_id>": {"name": "...", "notes": "...", "created_at": "..."} , ... }
- events.jsonl : one JSON object per line (append-only)

Event types (recommended):
- connection_requested
- connection_accepted
- legibility_sent
- question_sent
- reply_received
- call_ask_sent
- call_agreed
- scheduling_sent
- call_scheduled
- call_completed

Usage examples:
  python network_metrics.py add-person --id samia --name "Samia A."
  python network_metrics.py log --id samia --event connection_requested
  python network_metrics.py log --id samia --event connection_accepted
  python network_metrics.py metrics
  python network_metrics.py metrics --since 2026-01-01 --until 2026-01-31
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, Any, Iterable, Optional, Tuple

ISO_DT_FMT = "%Y-%m-%dT%H:%M:%SZ"
ISO_D_FMT = "%Y-%m-%d"

DEFAULT_EVENTS = [
    "connection_requested",
    "connection_accepted",
    "legibility_sent",
    "question_sent",
    "reply_received",
    "call_ask_sent",
    "call_agreed",
    "scheduling_sent",
    "call_scheduled",
    "call_completed",
]


def utc_now_iso() -> str:
    return datetime.utcnow().strftime(ISO_DT_FMT)


def die(msg: str, code: int = 2) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_dir(path: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def load_people(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_people(path: str, people: Dict[str, Any]) -> None:
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(people, f, indent=2, ensure_ascii=False, sort_keys=True)


def append_event(path: str, event_obj: Dict[str, Any]) -> None:
    ensure_dir(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_obj, ensure_ascii=False) + "\n")


def iter_events(path: str) -> Iterable[Dict[str, Any]]:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # skip bad lines (should be rare); keep running
                continue


def parse_ymd(s: str) -> date:
    try:
        return datetime.strptime(s, ISO_D_FMT).date()
    except ValueError:
        die(f"Bad date '{s}'. Use YYYY-MM-DD.")


def in_date_range(ts_iso: str, since: Optional[date], until: Optional[date]) -> bool:
    # inclusive since, inclusive until (date-based)
    try:
        dt = datetime.strptime(ts_iso, ISO_DT_FMT)
    except ValueError:
        return False
    d = dt.date()
    if since and d < since:
        return False
    if until and d > until:
        return False
    return True


@dataclass
class FunnelCounts:
    # activity
    connection_requested: int = 0
    connection_accepted: int = 0
    legibility_sent: int = 0
    question_sent: int = 0
    reply_received: int = 0
    call_ask_sent: int = 0
    call_agreed: int = 0
    scheduling_sent: int = 0
    call_scheduled: int = 0
    call_completed: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {k: getattr(self, k) for k in self.__annotations__.keys()}


def safe_div(n: int, d: int) -> Optional[float]:
    if d == 0:
        return None
    return n / d


def fmt_pct(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return f"{x*100:.1f}%"


def compute_counts(events_path: str, since: Optional[date], until: Optional[date]) -> FunnelCounts:
    c = FunnelCounts()
    for e in iter_events(events_path):
        ts = e.get("ts")
        if not isinstance(ts, str):
            continue
        if not in_date_range(ts, since, until):
            continue
        ev = e.get("event")
        if ev in c.__annotations__:
            setattr(c, ev, getattr(c, ev) + 1)
    return c


def compute_ratios(c: FunnelCounts) -> Dict[str, Optional[float]]:
    return {
        "acceptance_rate": safe_div(c.connection_accepted, c.connection_requested),
        "reply_rate_legibility": safe_div(c.reply_received, c.legibility_sent),
        "reply_rate_questions": safe_div(c.reply_received, c.question_sent),
        "call_yes_rate": safe_div(c.call_agreed, c.call_ask_sent),
        "booking_rate": safe_div(c.call_scheduled, c.connection_accepted),
        # Primary KPI (your target 8–12%):
        "chat_rate": safe_div(c.call_completed, c.connection_accepted),
        "completion_rate": safe_div(c.call_completed, c.call_scheduled),
    }


def print_report(c: FunnelCounts, ratios: Dict[str, Optional[float]], since: Optional[date], until: Optional[date]) -> None:
    window = []
    if since:
        window.append(f"since {since.isoformat()}")
    if until:
        window.append(f"until {until.isoformat()}")
    window_txt = f" ({', '.join(window)})" if window else ""
    print(f"\nNetworking Metrics Report{window_txt}\n" + "-" * 32)

    # counts
    print("\nCounts")
    for k, v in c.as_dict().items():
        print(f"  {k:22s} {v}")

    # ratios
    print("\nRatios")
    print(f"  acceptance_rate          {fmt_pct(ratios['acceptance_rate'])}   (accepted / requested)")
    print(f"  reply_rate_legibility    {fmt_pct(ratios['reply_rate_legibility'])}   (replies / L1-L2)")
    print(f"  reply_rate_questions     {fmt_pct(ratios['reply_rate_questions'])}   (replies / Q sent)")
    print(f"  call_yes_rate            {fmt_pct(ratios['call_yes_rate'])}   (call agreed / C1 sent)")
    print(f"  booking_rate             {fmt_pct(ratios['booking_rate'])}   (calls scheduled / accepted)")
    print(f"  chat_rate                {fmt_pct(ratios['chat_rate'])}   (calls completed / accepted)  ← target 8–12%")
    print(f"  completion_rate          {fmt_pct(ratios['completion_rate'])}   (completed / scheduled)")

    # quick interpretation for chat_rate
    cr = ratios["chat_rate"]
    if cr is not None:
        if cr < 0.05:
            band = "<5% (diagnose: messaging/ask/timing)"
        elif cr < 0.08:
            band = "5–8% (working, improvable)"
        elif cr <= 0.12:
            band = "8–12% (target band)"
        else:
            band = ">12% (strong; scale volume)"
        print(f"\nChat-rate band: {band}")
    print("")


def cmd_add_person(args: argparse.Namespace) -> None:
    people = load_people(args.people)
    pid = args.id.strip()
    if not pid:
        die("Person id cannot be empty.")
    if pid in people and not args.force:
        die(f"Person id '{pid}' already exists. Use --force to overwrite.")
    people[pid] = {
        "name": args.name,
        "notes": args.notes or "",
        "created_at": utc_now_iso(),
    }
    save_people(args.people, people)
    print(f"Added person: {pid} ({args.name})")


def cmd_log(args: argparse.Namespace) -> None:
    # Validate event
    ev = args.event.strip()
    if ev not in DEFAULT_EVENTS:
        die(f"Unknown event '{ev}'. Allowed: {', '.join(DEFAULT_EVENTS)}")
    pid = args.id.strip()
    if not pid:
        die("Person id cannot be empty.")

    # If people file exists, warn (not fail) if unknown id
    if os.path.exists(args.people):
        people = load_people(args.people)
        if pid not in people and not args.allow_unknown_person:
            die(f"Unknown person id '{pid}'. Add them first or use --allow-unknown-person.")
    event_obj = {
        "ts": utc_now_iso(),
        "person_id": pid,
        "event": ev,
        "meta": {},
    }
    if args.meta:
        try:
            event_obj["meta"] = json.loads(args.meta)
            if not isinstance(event_obj["meta"], dict):
                die("--meta must be a JSON object, e.g. '{\"q\":\"Q3\"}'")
        except json.JSONDecodeError:
            die("--meta must be valid JSON, e.g. '{\"q\":\"Q3\"}'")

    append_event(args.events, event_obj)
    print(f"Logged: {ev} for {pid}")


def cmd_metrics(args: argparse.Namespace) -> None:
    since = parse_ymd(args.since) if args.since else None
    until = parse_ymd(args.until) if args.until else None
    if since and until and until < since:
        die("--until cannot be earlier than --since.")

    c = compute_counts(args.events, since, until)
    ratios = compute_ratios(c)
    print_report(c, ratios, since, until)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kondo_metrics.py", description="Minimal networking metrics logger + reporter.")
    p.add_argument("--people", default="people.json", help="Path to people.json (default: people.json)")
    p.add_argument("--events", default="events.jsonl", help="Path to events.jsonl (default: events.jsonl)")

    sub = p.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser("add-person", help="Add a person record (minimal).")
    ap.add_argument("--id", required=True, help="Person id (short slug, unique).")
    ap.add_argument("--name", required=True, help="Display name.")
    ap.add_argument("--notes", default="", help="Optional notes.")
    ap.add_argument("--force", action="store_true", help="Overwrite if id exists.")
    ap.set_defaults(func=cmd_add_person)

    lg = sub.add_parser("log", help="Append one event to events.jsonl.")
    lg.add_argument("--id", required=True, help="Person id.")
    lg.add_argument("--event", required=True, help=f"Event type. Allowed: {', '.join(DEFAULT_EVENTS)}")
    lg.add_argument("--meta", default="", help="Optional JSON object meta (e.g. '{\"q\":\"Q3\"}').")
    lg.add_argument("--allow-unknown-person", action="store_true", help="Allow logging for unknown person ids.")
    lg.set_defaults(func=cmd_log)

    mt = sub.add_parser("metrics", help="Show counts and ratios.")
    mt.add_argument("--since", default="", help="Start date YYYY-MM-DD (inclusive).")
    mt.add_argument("--until", default="", help="End date YYYY-MM-DD (inclusive).")
    mt.set_defaults(func=cmd_metrics)

    return p


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
