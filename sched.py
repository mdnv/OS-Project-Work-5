#!/usr/bin/env python3
"""CPU scheduling simulator; all times are integer simulation ticks."""
import argparse
from collections import deque
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int


ALGORITHMS = ("fcfs", "sjf", "srtf", "priority", "rr")


def validate(processes):
    if not processes:
        raise ValueError("Process list is empty")
    seen = set()
    for p in processes:
        if not p.pid or p.pid == "IDLE" or p.pid in seen:
            raise ValueError("PID must be unique; IDLE is reserved")
        seen.add(p.pid)
        if any(type(v) is not int for v in (p.arrival, p.burst, p.priority)):
            raise ValueError("arrival, burst and priority must be integers")
        if p.arrival < 0 or p.burst <= 0:
            raise ValueError("arrival >= 0 and burst > 0 are required")


def read_processes(filename):
    processes = []
    for line_no, line in enumerate(Path(filename).read_text().splitlines(), 1):
        fields = line.split("#", 1)[0].split()
        if not fields:
            continue
        if len(fields) != 4:
            raise ValueError(f"Line {line_no}: expected PID arrival burst priority")
        try:
            arrival, burst, priority = map(int, fields[1:])
        except ValueError as exc:
            raise ValueError(f"Line {line_no}: times and priority must be integers") from exc
        processes.append(Process(fields[0], arrival, burst, priority))
    validate(processes)
    return processes


def append_interval(timeline, start, end, pid):
    """Merge adjacent intervals of the same process; use IDLE for inactivity."""
    if timeline and timeline[-1][2] == pid and timeline[-1][1] == start:
        timeline[-1] = (timeline[-1][0], end, pid)
    else:
        timeline.append((start, end, pid))


def simulate(processes, algorithm, **params):
    """Return [(start, end, PID), ...], where intervals are [start, end).

    Smaller priority means higher importance. Equal primary keys prefer the
    current process, then arrival time, then input order. Aging uses accumulated
    ready-queue waiting: effective_priority = priority - waiting // aging.
    Context-switch cost is zero; there is no I/O in this model.
    """
    processes = list(processes)
    validate(processes)
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    quantum = params.get("quantum", 3)
    aging = params.get("aging", 0)
    if type(quantum) is not int or quantum <= 0:
        raise ValueError("quantum must be a positive integer")
    if type(aging) is not int or aging < 0:
        raise ValueError("aging must be a nonnegative integer (0 disables aging)")
    if aging and algorithm != "priority":
        raise ValueError("aging is supported only for priority")
    remaining = [p.burst for p in processes]
    timeline = []
    t = 0

    if algorithm == "rr":
        arrivals = sorted(range(len(processes)), key=lambda i: (processes[i].arrival, i))
        queue = deque()
        pos = 0

        def admit(now):
            nonlocal pos
            while pos < len(arrivals) and processes[arrivals[pos]].arrival <= now:
                queue.append(arrivals[pos])
                pos += 1

        admit(t)
        while queue or pos < len(arrivals):
            if not queue:
                next_t = processes[arrivals[pos]].arrival
                append_interval(timeline, t, next_t, "IDLE")
                t = next_t
                admit(t)
            i = queue.popleft()
            end = t + min(quantum, remaining[i])
            append_interval(timeline, t, end, processes[i].pid)
            remaining[i] -= end - t
            t = end
            # Include arrivals exactly at t BEFORE re-queuing the old process.
            admit(t)
            if remaining[i]:
                queue.append(i)
        return timeline

    current = None
    unfinished = len(processes)
    while unfinished:
        ready = [i for i, p in enumerate(processes) if p.arrival <= t and remaining[i]]
        if not ready:
            next_t = min(p.arrival for i, p in enumerate(processes) if remaining[i])
            append_interval(timeline, t, next_t, "IDLE")
            t = next_t
            current = None
            continue
        if algorithm in ("fcfs", "sjf"):
            if current is None:
                if algorithm == "fcfs":
                    current = min(ready, key=lambda i: (processes[i].arrival, i))
                else:
                    current = min(ready, key=lambda i: (processes[i].burst, processes[i].arrival, i))
        elif algorithm == "srtf":
            current = min(ready, key=lambda i: (
                remaining[i], i != current, processes[i].arrival, i
            ))
        else:
            def priority_key(i):
                p = processes[i]
                executed = p.burst - remaining[i]
                waiting = t - p.arrival - executed
                effective = p.priority - (waiting // aging if aging else 0)
                return effective, i != current, p.arrival, i
            current = min(ready, key=priority_key)
        # Preemptive algorithms reconsider all ready processes on every tick.
        append_interval(timeline, t, t + 1, processes[current].pid)
        remaining[current] -= 1
        t += 1
        if remaining[current] == 0:
            unfinished -= 1
            current = None
    return timeline


def calculate_metrics(processes, timeline):
    first = {}
    completion = {}
    busy = 0
    for start, end, pid in timeline:
        if pid != "IDLE":
            first.setdefault(pid, start)
            completion[pid] = end
            busy += end - start
    rows = []
    for p in processes:
        turnaround = completion[p.pid] - p.arrival
        rows.append({
            "pid": p.pid, "arrival": p.arrival, "burst": p.burst,
            "start": first[p.pid], "finish": completion[p.pid],
            "waiting": turnaround - p.burst,
            "turnaround": turnaround,
            "response": first[p.pid] - p.arrival,
        })
    # Count only adjacent transitions between distinct PIDs; exclude IDLE.
    switches = sum(a[2] != "IDLE" and b[2] != "IDLE" and a[2] != b[2]
                   for a, b in zip(timeline, timeline[1:]))
    summary = {
        key: sum(row[key] for row in rows) / len(rows)
        for key in ("waiting", "turnaround", "response")
    }
    summary.update(cpu=100 * busy / timeline[-1][1], switches=switches)
    return rows, summary


def print_summary(label, summary):
    print(f"{label:<19} {summary['waiting']:>9.2f} {summary['turnaround']:>9.2f} "
          f"{summary['response']:>9.2f} {summary['cpu']:>8.2f} {summary['switches']:>9}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Input: PID arrival burst priority")
    parser.add_argument("--algo", choices=(*ALGORITHMS, "all"), default="all")
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("--aging", type=int, default=0, help="Waiting ticks per priority boost; 0=off")
    parser.add_argument("--timeline", action="store_true")
    parser.add_argument("--per-process", action="store_true")
    args = parser.parse_args()
    if args.aging and args.algo not in ("priority", "all"):
        parser.error("--aging requires --algo priority or all")
    try:
        processes = read_processes(args.file)
        print(f"{'Algorithm':<19} {'AvgWait':>9} {'AvgTurn':>9} {'AvgResp':>9} {'CPU%':>8} {'Switches':>9}")
        for algo in (ALGORITHMS if args.algo == "all" else (args.algo,)):
            aging = args.aging if algo == "priority" else 0
            intervals = simulate(processes, algo, quantum=args.quantum, aging=aging)
            rows, summary = calculate_metrics(processes, intervals)
            label = algo.upper()
            if algo == "rr":
                label += f" q={args.quantum}"
            if aging:
                label += f" aging={aging}"
            print_summary(label, summary)
            if args.timeline:
                print("Timeline: " + " | ".join(f"{a}-{b}:{pid}" for a, b, pid in intervals))
            if args.per_process:
                print("PID       Arrival Burst Start Finish Wait Turn Response")
                for row in rows:
                    print(f"{row['pid']:<9} " + " ".join(f"{row[k]:>5}" for k in (
                        "arrival", "burst", "start", "finish", "waiting", "turnaround", "response"
                    )))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
