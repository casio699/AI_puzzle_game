"""
solver.py: AI algorithms for Puzzle Challenge (DFS, BFS, UCS, Greedy, A*).

Each solver returns:
    path: list of moves (e.g. ['up', 'left', ...])
    steps: number of moves in solution
    info: statistics (e.g. explored nodes, cost)
"""
import numpy as np
import heapq
from collections import deque

# State: (tiles, blank_pos)

def get_neighbors(state):
    """
    Given a puzzle state, return all valid neighbor states (after sliding a tile into the blank).
    Each neighbor is a tuple: (new_state, action).
    """
    tiles, blank = state
    n = tiles.shape[0]
    x, y = blank
    moves = []
    for dx, dy, action in [(-1,0,'up'),(1,0,'down'),(0,-1,'left'),(0,1,'right')]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < n and 0 <= ny < n:
            new_tiles = tiles.copy()
            new_tiles[x,y], new_tiles[nx,ny] = new_tiles[nx,ny], new_tiles[x,y]
            moves.append(((new_tiles, (nx,ny)), action))
    return moves

def serialize(tiles):
    """Convert tiles to a tuple for hashing."""
    return tuple(tiles.flatten())

def reconstruct_path(came_from, state):
    path = []
    while state in came_from:
        state, action = came_from[state]
        path.append(action)
    return path[::-1]

def dfs_solver(start, goal):
    """Depth-First Search (DFS) solver."""
    stack = [(start, [])]
    visited = set()
    while stack:
        state, path = stack.pop()
        if np.array_equal(state[0], goal[0]):
            return path, len(path), {'explored': len(visited)}
        key = (serialize(state[0]), state[1])
        if key in visited:
            continue
        visited.add(key)
        for neighbor, action in get_neighbors(state):
            stack.append((neighbor, path + [action]))
    return None, 0, {'explored': len(visited)}

def bfs_solver(start, goal):
    """
    Breadth-First Search (BFS) solver.
    
    Args:
        start: Initial state as (tiles, blank_pos)
        goal: Goal state as (tiles, blank_pos)
        
    Returns:
        tuple: (path, steps, info) where:
            - path: list of moves (e.g., ['up', 'left', ...])
            - steps: number of moves in solution
            - info: dictionary with statistics
    """
    queue = deque([(start, [])])
    visited = set()
    
    # Convert goal tiles to a tuple for comparison
    goal_tiles_tuple = tuple(map(tuple, goal[0]))
    
    while queue:
        state, path = queue.popleft()
        current_tiles, current_blank = state
        
        # Convert current tiles to a tuple for comparison
        current_tiles_tuple = tuple(map(tuple, current_tiles))
        
        # Check if current state matches the goal state
        if current_tiles_tuple == goal_tiles_tuple:
            return path, len(path), {'explored': len(visited)}
            
        # Use serialized state for visited check
        state_key = (current_tiles_tuple, current_blank)
        if state_key in visited:
            continue
            
        visited.add(state_key)
        
        # Explore neighbors
        for neighbor, action in get_neighbors(state):
            queue.append((neighbor, path + [action]))
            
    return None, 0, {'explored': len(visited)}

def ucs_solver(start, goal):
    """
    Uniform Cost Search (UCS) solver.
    
    Args:
        start: Initial state as (tiles, blank_pos)
        goal: Goal state as (tiles, blank_pos)
        
    Returns:
        tuple: (path, steps, info) where:
            - path: list of moves (e.g., ['up', 'left', ...])
            - steps: number of moves in solution
            - info: dictionary with statistics including cost
    """
    import itertools
    counter = itertools.count()
    heap = [(0, next(counter), start, [])]
    visited = set()
    goal_tiles_tuple = tuple(map(tuple, goal[0]))
    
    while heap:
        cost, _, state, path = heapq.heappop(heap)
        current_tiles, current_blank = state
        current_tiles_tuple = tuple(map(tuple, current_tiles))
        
        if current_tiles_tuple == goal_tiles_tuple:
            return path, len(path), {'explored': len(visited), 'cost': cost}
            
        state_key = (current_tiles_tuple, current_blank)
        if state_key in visited:
            continue
            
        visited.add(state_key)
        
        for neighbor, action in get_neighbors(state):
            heapq.heappush(heap, (cost + 1, next(counter), neighbor, path + [action]))
            
    return None, 0, {'explored': len(visited)}

def greedy_solver(start, goal, heuristic):
    """
    Greedy Best-First Search solver.
    
    Args:
        start: Initial state as (tiles, blank_pos)
        goal: Goal state as (tiles, blank_pos)
        heuristic: Heuristic function h(n) that estimates cost to goal
        
    Returns:
        tuple: (path, steps, info) where:
            - path: list of moves (e.g., ['up', 'left', ...])
            - steps: number of moves in solution
            - info: dictionary with statistics
    """
    import itertools
    counter = itertools.count()
    heap = [(heuristic(start[0], goal[0]), next(counter), start, [])]
    visited = set()
    goal_tiles_tuple = tuple(map(tuple, goal[0]))
    
    while heap:
        h, _, state, path = heapq.heappop(heap)
        current_tiles, current_blank = state
        current_tiles_tuple = tuple(map(tuple, current_tiles))
        
        if current_tiles_tuple == goal_tiles_tuple:
            return path, len(path), {'explored': len(visited)}
            
        state_key = (current_tiles_tuple, current_blank)
        if state_key in visited:
            continue
            
        visited.add(state_key)
        
        for neighbor, action in get_neighbors(state):
            heapq.heappush(heap, (
                heuristic(neighbor[0], goal[0]), 
                next(counter),
                neighbor, 
                path + [action]
            ))
            
    return None, 0, {'explored': len(visited)}

def astar_solver(start, goal, heuristic):
    """
    A* Search solver.
    
    Args:
        start: Initial state as (tiles, blank_pos)
        goal: Goal state as (tiles, blank_pos)
        heuristic: Heuristic function h(n) that estimates cost to goal
        
    Returns:
        tuple: (path, steps, info) where:
            - path: list of moves (e.g., ['up', 'left', ...])
            - steps: number of moves in solution
            - info: dictionary with statistics including cost
    """
    import itertools
    counter = itertools.count()
    heap = [(heuristic(start[0], goal[0]), 0, next(counter), start, [])]
    visited = set()
    goal_tiles_tuple = tuple(map(tuple, goal[0]))
    
    while heap:
        f, cost, _, state, path = heapq.heappop(heap)
        current_tiles, current_blank = state
        current_tiles_tuple = tuple(map(tuple, current_tiles))
        
        if current_tiles_tuple == goal_tiles_tuple:
            return path, len(path), {'explored': len(visited), 'cost': cost}
            
        state_key = (current_tiles_tuple, current_blank)
        if state_key in visited:
            continue
            
        visited.add(state_key)
        
        for neighbor, action in get_neighbors(state):
            g = cost + 1
            h = heuristic(neighbor[0], goal[0])
            heapq.heappush(heap, (g + h, g, next(counter), neighbor, path + [action]))
            
    return None, 0, {'explored': len(visited)}
