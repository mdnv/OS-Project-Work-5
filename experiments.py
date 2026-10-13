"""Save tables and plots without a graphical desktop (works over SSH)."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sched import Process, calculate_metrics, read_processes, simulate


def save_csv(path, rows):
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    output = Path("results")
    output.mkdir(exist_ok=True)
    comparisons = []
    for name in ("set1", "set2", "set3"):
        processes = read_processes(name + ".txt")
        for algo in ("fcfs", "sjf", "srtf", "priority", "rr"):
            _, summary = calculate_metrics(processes, simulate(processes, algo, quantum=3))
            comparisons.append({"set": name, "algorithm": algo, **summary})
    save_csv(output / "comparison.csv", comparisons)

    processes = read_processes("set2.txt")
    rr = []
    print("Quantum   AvgWait   AvgResponse   Switches")
    for quantum in range(1, 11):
        _, summary = calculate_metrics(processes, simulate(processes, "rr", quantum=quantum))
        rr.append({"quantum": quantum, **summary})
        print(f"{quantum:>7} {summary['waiting']:>9.2f} {summary['response']:>13.2f} {summary['switches']:>10}")
    save_csv(output / "rr_quantum.csv", rr)
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    axes[0].plot([r['quantum'] for r in rr], [r['waiting'] for r in rr], "o-", color="#2962ff")
    axes[0].set_ylabel("Average waiting (ticks)")
    axes[0].set_title("Round Robin on set2: quantum trade-off")
    axes[1].plot([r['quantum'] for r in rr], [r['switches'] for r in rr], "o-", color="#cf5e10")
    axes[1].set_ylabel("Process switches")
    axes[1].set_xlabel("Quantum (ticks)")
    axes[1].set_xticks(range(1, 11))
    for ax in axes:
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output / "rr_quantum.png", dpi=160)
    plt.close(fig)

    # Show increasing finite prefixes, then compare aging on the full prefix.
    aging_rows = []
    print("\nHigh jobs   Aging   LOW start   LOW finish   LOW waiting")
    for count in (100, 400, 800):
        processes = [Process("LOW", 0, 8, 10)] + [
            Process(f"H{i+1}", i, 2, 0) for i in range(count)
        ]
        for aging in (0, 5):
            rows, _ = calculate_metrics(processes, simulate(processes, "priority", aging=aging))
            low = next(row for row in rows if row['pid'] == 'LOW')
            aging_rows.append({"high_jobs": count, "aging": aging, **low})
            print(f"{count:>9} {aging:>7} {low['start']:>11} {low['finish']:>12} {low['waiting']:>13}")
    save_csv(output / "aging.csv", aging_rows)
    fig, ax = plt.subplots(figsize=(8, 4))
    for aging, label in ((0, "Without aging"), (5, "Aging every 5 waiting ticks")):
        rows = [r for r in aging_rows if r['aging'] == aging]
        ax.plot([r['high_jobs'] for r in rows], [r['start'] for r in rows], "o-", label=label)
    ax.set(xlabel="Number of high-priority arrivals", ylabel="LOW first start (ticks)",
           title="Long waiting under a high-priority arrival stream")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "aging.png", dpi=160)
    plt.close(fig)
    print("\nSaved tables and plots in results/")


if __name__ == "__main__":
    main()
