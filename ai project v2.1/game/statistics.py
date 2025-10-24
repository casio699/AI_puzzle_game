"""
statistics.py: Statistics collection and display for Puzzle Challenge.
"""
from collections import defaultdict

class Statistics:
    """
    Tracks and stores AI/heuristic performance for the puzzle game.
    Stores results as a list of dicts for each (algorithm, heuristic) pair.
    """
    def __init__(self):
        self.data = defaultdict(list)  # (algo, heuristic) -> list of dicts

    def add_result(self, algo, heuristic, time_taken, steps, explored):
        """Add a result for a specific algorithm and heuristic."""
        self.data[(algo, heuristic)].append({
            'time': time_taken,
            'steps': steps,
            'explored': explored
        })

    def get_summary(self, algo, heuristic):
        """Return average stats for a given algorithm/heuristic."""
        results = self.data.get((algo, heuristic), [])
        if not results:
            return None
        avg_time = sum(r['time'] for r in results) / len(results)
        avg_steps = sum(r['steps'] for r in results) / len(results)
        avg_explored = sum(r['explored'] for r in results) / len(results)
        return {
            'avg_time': avg_time,
            'avg_steps': avg_steps,
            'avg_explored': avg_explored,
            'runs': len(results)
        }

    def get_all_stats(self):
        """Return a summary for all algorithm/heuristic pairs."""
        return { (algo, heur): self.get_summary(algo, heur) for (algo, heur) in self.data }
