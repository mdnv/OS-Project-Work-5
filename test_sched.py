import unittest
from sched import Process, calculate_metrics, simulate


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.processes = [Process("P1", 0, 8, 3), Process("P2", 1, 4, 1),
                          Process("P3", 2, 9, 4), Process("P4", 3, 5, 2)]

    def test_reference_metrics(self):
        # The assignment's FCFS reference (9.25, 15.75) is arithmetically wrong.
        for algo, waiting, turnaround in (("fcfs", 8.75, 15.25),
                                          ("srtf", 6.5, 13.0), ("rr", 13.5, 20.0)):
            with self.subTest(algo=algo):
                _, result = calculate_metrics(self.processes, simulate(self.processes, algo, quantum=3))
                self.assertAlmostEqual(result['waiting'], waiting)
                self.assertAlmostEqual(result['turnaround'], turnaround)

    def test_rr_arrival_at_quantum_boundary(self):
        processes = [Process("A", 0, 6, 0), Process("B", 3, 1, 0)]
        self.assertEqual(simulate(processes, "rr", quantum=3),
                         [(0, 3, 'A'), (3, 4, 'B'), (4, 7, 'A')])

    def test_srtf_preemption(self):
        self.assertEqual(simulate(self.processes, "srtf"),
                         [(0, 1, 'P1'), (1, 5, 'P2'), (5, 10, 'P4'),
                          (10, 17, 'P1'), (17, 26, 'P3')])

    def test_sjf_is_nonpreemptive(self):
        self.assertEqual(simulate(self.processes, 'sjf'),
                         [(0, 8, 'P1'), (8, 12, 'P2'), (12, 17, 'P4'), (17, 26, 'P3')])

    def test_priority_preemption(self):
        self.assertEqual(simulate([Process('A', 0, 4, 5), Process('B', 1, 1, 0)], 'priority'),
                         [(0, 1, 'A'), (1, 2, 'B'), (2, 5, 'A')])

    def test_idle_and_utilization(self):
        processes = [Process('A', 5, 2, 0), Process('B', 10, 1, 0)]
        for algo in ('fcfs', 'sjf', 'srtf', 'priority', 'rr'):
            with self.subTest(algo=algo):
                intervals = simulate(processes, algo)
                self.assertEqual(intervals, [(0, 5, 'IDLE'), (5, 7, 'A'),
                                            (7, 10, 'IDLE'), (10, 11, 'B')])
                _, result = calculate_metrics(processes, intervals)
                self.assertAlmostEqual(result['cpu'], 100 * 3 / 11)
                self.assertEqual(result['switches'], 0)

    def test_large_quantum_equals_fcfs(self):
        self.assertEqual(simulate(self.processes, 'rr', quantum=100),
                         simulate(self.processes, 'fcfs'))

    def test_validation(self):
        for args in (([], 'fcfs', {}), (self.processes, 'rr', {'quantum': 0}),
                     ([Process('A', -1, 2, 0)], 'fcfs', {}),
                     ([Process('A', 0, 0, 0)], 'fcfs', {}),
                     ([Process('A', 0, 1, 0)] * 2, 'fcfs', {})):
            with self.subTest(args=args), self.assertRaises(ValueError):
                simulate(args[0], args[1], **args[2])

    def test_aging_helps_low_priority(self):
        processes = [Process('LOW', 0, 8, 10)] + [Process(f'H{i}', i, 2, 0) for i in range(100)]
        starts = []
        for aging in (0, 5):
            rows, _ = calculate_metrics(processes, simulate(processes, 'priority', aging=aging))
            starts.append(rows[0]['start'])
        self.assertEqual(starts, [200, 96])

    def test_conservation_and_repeatability(self):
        for algo in ('fcfs', 'sjf', 'srtf', 'priority', 'rr'):
            with self.subTest(algo=algo):
                timeline = simulate(self.processes, algo)
                self.assertEqual(timeline, simulate(self.processes, algo))
                for p in self.processes:
                    self.assertEqual(sum(b - a for a, b, pid in timeline if pid == p.pid), p.burst)
                self.assertTrue(all(a[1] == b[0] for a, b in zip(timeline, timeline[1:])))


if __name__ == '__main__':
    unittest.main()
