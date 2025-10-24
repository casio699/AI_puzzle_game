"""
heuristics.py: Heuristic functions for Puzzle Challenge.
"""
import numpy as np

def find_position(tiles, value):
    """Helper function to find position of a value in the puzzle."""
    for i, row in enumerate(tiles):
        if value in row:
            return (i, row.index(value))
    return None

def misplaced_tiles(state, goal):
    """
    Heuristic: Count the number of tiles not in their goal position (excluding blank).
    Lower is better; 0 means solved.
    """
    # Convert numpy arrays to lists for compatibility
    if hasattr(state, 'tolist'):
        state = state.tolist()
    if hasattr(goal, 'tolist'):
        goal = goal.tolist()
    
    count = 0
    for i in range(len(state)):
        for j in range(len(state[0])):
            if state[i][j] != 0 and state[i][j] != goal[i][j]:
                count += 1
    return count

def manhattan_distance(state, goal):
    """
    Heuristic: Total Manhattan distance of all tiles from their goal positions (excluding blank).
    Lower is better; 0 means solved.
    """
    # Convert numpy arrays to lists for compatibility
    if hasattr(state, 'tolist'):
        state = state.tolist()
    if hasattr(goal, 'tolist'):
        goal = goal.tolist()
    
    distance = 0
    n = len(state)
    # Create a dictionary to store goal positions for quick lookup
    goal_pos = {}
    for i in range(n):
        for j in range(n):
            goal_pos[goal[i][j]] = (i, j)
    
    # Calculate Manhattan distance for each tile
    for i in range(n):
        for j in range(n):
            val = state[i][j]
            if val != 0:  # Skip the blank tile
                goal_i, goal_j = goal_pos[val]
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance

def custom_heuristic(state, goal):
    """
    Custom heuristic: Manhattan distance + 0.5 * misplaced tiles.
    Combines both heuristics for a potentially better estimate.
    """
    # Convert numpy arrays to lists for compatibility
    if hasattr(state, 'tolist'):
        state = state.tolist()
    if hasattr(goal, 'tolist'):
        goal = goal.tolist()
    
    return manhattan_distance(state, goal) + 0.5 * misplaced_tiles(state, goal)
