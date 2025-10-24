#!/usr/bin/env python3
"""
Test script to simulate auto-solve functionality without GUI
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from game.board import Board

def test_auto_solve_simulation():
    """Test the auto-solve logic by simulating what happens in GameWindow._run_solver"""

    print("Testing auto-solve functionality...")

    # Create a board
    board = Board(3)
    print(f"Initial board state:")
    print(board.tiles)
    print(f"Blank position: {board.blank_pos}")

    # Import solver functions
    try:
        from game.solver import dfs_solver, bfs_solver, ucs_solver, greedy_solver, astar_solver
        from game.heuristics import misplaced_tiles, manhattan_distance, custom_heuristic
        print("✓ Successfully imported solver functions")
    except Exception as e:
        print(f"✗ Failed to import solver functions: {e}")
        return False

    # Set up the test parameters (simulating GUI state)
    algo = 'UCS'  # Start with UCS
    heur = 'manhattan'  # Use manhattan heuristic

    start_state = (board.tiles.copy(), board.blank_pos)
    n = board.size

    # Create goal state (same as in _run_solver)
    goal = np.arange(1, n*n)
    goal = np.append(goal, 0).reshape((n, n))
    goal_state = (goal, tuple(map(int, (n-1, n-1))))

    print(f"Goal state:")
    print(goal)

    # Test the solver mapping (same as in _run_solver)
    solver_map = {
        'DFS': dfs_solver,
        'BFS': bfs_solver,
        'UCS': ucs_solver,
        'Greedy': lambda s, g: greedy_solver(s, g, {'misplaced': misplaced_tiles, 'manhattan': manhattan_distance, 'custom': custom_heuristic}[heur]),
        'A*': lambda s, g: astar_solver(s, g, {'misplaced': misplaced_tiles, 'manhattan': manhattan_distance, 'custom': custom_heuristic}[heur]),
    }

    print(f"\nTesting {algo} solver...")

    try:
        import time
        t0 = time.time()

        if algo in ['Greedy', 'A*']:
            path, steps, info = solver_map[algo](start_state, goal_state)
        else:
            path, steps, info = solver_map[algo](start_state, goal_state)

        t1 = time.time()

        if path is not None:
            print("✓ Solution found!")
            print(f"  Path: {path}")
            print(f"  Steps: {steps}")
            print(f"  Explored nodes: {info.get('explored', 'N/A')}")
            print(f"  Time: {t1-t0:.3f}s")
            return True
        else:
            print("✗ No solution found")
            return False

    except Exception as e:
        print(f"✗ Solver error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_case():
    """Test with a very simple case that's almost solved"""
    print("\n" + "="*50)
    print("Testing with a simple case...")

    # Create a board that's almost solved
    tiles = np.array([[1, 2, 3], [4, 5, 6], [7, 0, 8]])  # Just one move needed
    blank_pos = (2, 1)  # blank at position (2,1)

    start_state = (tiles, blank_pos)
    goal = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    goal_state = (goal, (2, 2))

    print("Start state:")
    print(tiles)
    print("Goal state:")
    print(goal)

    try:
        from game.solver import bfs_solver
        path, steps, info = bfs_solver(start_state, goal_state)

        if path is not None:
            print("✓ Simple case solved!")
            print(f"  Path: {path}")
            print(f"  Steps: {steps}")
            return True
        else:
            print("✗ Even simple case failed")
            return False
    except Exception as e:
        print(f"✗ Error in simple case: {e}")
        return False

if __name__ == "__main__":
    print("Puzzle Challenge Auto-Solve Test")
    print("="*50)

    # Test simple case first
    simple_success = test_simple_case()

    # Test complex case
    complex_success = test_auto_solve_simulation()

    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Simple case: {'PASS' if simple_success else 'FAIL'}")
    print(f"Complex case: {'PASS' if complex_success else 'FAIL'}")

    if simple_success and complex_success:
        print("✓ All tests passed - auto-solve appears to be working")
    elif simple_success and not complex_success:
        print("⚠ Simple cases work, but complex cases may be slow")
    else:
        print("✗ Auto-solve has issues that need fixing")
