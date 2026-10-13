"""Reproducible demonstration data, not undisclosed instructor datasets."""
from pathlib import Path


def write_set(filename, rows):
    Path(filename).write_text("# PID arrival burst priority\n" + "\n".join(
        " ".join(map(str, row)) for row in rows
    ) + "\n")


def main():
    # Priorities were not supplied for set1: explicitly chosen demo values.
    write_set("set1.txt", [("P1", 0, 8, 3), ("P2", 1, 4, 1),
                           ("P3", 2, 9, 4), ("P4", 3, 5, 2)])
    write_set("set2.txt", [(f"P{i+1}", i * 2, 20 + (i * 7) % 21, 1 + i % 5)
                           for i in range(20)])
    write_set("set3.txt", [("P1", 0, 80, 3)] + [
        (f"P{i+1}", i, 1 + i % 4, 1 + i % 5) for i in range(1, 20)
    ])
    # Stream of high-priority jobs: 2 CPU ticks of work arrive every tick.
    # A finite prefix cannot establish infinite starvation, but reveals the delay.
    write_set("starvation.txt", [("LOW", 0, 8, 10)] + [
        (f"H{i+1}", i, 2, 0) for i in range(800)
    ])
    print("Created: set1.txt, set2.txt, set3.txt, starvation.txt")


if __name__ == "__main__":
    main()
