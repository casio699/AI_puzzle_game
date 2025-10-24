# Puzzle Challenge: Detailed Walkthrough

## Introduction

This document provides a comprehensive, line-by-line walkthrough of the "Puzzle Challenge" program, a sliding puzzle solver implemented in Python. The program simulates a classic sliding puzzle (e.g., 15-puzzle) and integrates multiple AI search algorithms to automatically solve it. It features a graphical user interface (GUI) built with Pygame, allowing users to interact with the puzzle, select algorithms, and view statistics.

The program is designed for educational purposes, particularly for an Applied Artificial Intelligence class, to demonstrate concepts like uninformed and informed search, heuristics, and performance analysis. Key emphases include:
- **Auto-Solve Algorithms**: Implementations of Depth-First Search (DFS), Breadth-First Search (BFS), Uniform Cost Search (UCS), Greedy Best-First Search, and A* Search.
- **Heuristics**: Admissible and consistent heuristic functions (e.g., misplaced tiles, Manhattan distance) used in informed searches.
- **Statistics**: Tracking and analysis of algorithm performance metrics such as execution time, steps to solution, and nodes explored.

This walkthrough is structured for clarity, starting with an overview, then diving into code details, and ending with integration insights. It assumes familiarity with basic Python, NumPy, and AI concepts.

## Project Structure

The project is organized into several directories and files for modularity:

- **`main.py`**: Entry point. Initializes Pygame and launches the GUI.
- **`game/`**: Core game logic.
  - `board.py`: Manages the puzzle board state, including initialization, shuffling, moves, and solvability checks.
  - `solver.py`: Contains AI algorithms for solving the puzzle.
  - `heuristics.py`: Defines heuristic functions for informed searches.
  - `statistics.py`: Handles collection and aggregation of performance statistics.
- **`gui/`**: User interface components.
  - `game_window.py`: Main GUI window, handling rendering, user input, and solver integration.
  - `controls.py`: Likely manages UI controls (e.g., buttons, menus).
  - `themes.py`: Styling and themes for the GUI.
- **`utils/`**: Utility functions (e.g., error handling).
- **`test_auto_solve.py`**: Standalone tests for the auto-solve functionality without GUI.
- **`requirements.txt`**: Lists dependencies (e.g., NumPy, Pygame).
- **`README.md`**: Project description.

The program uses NumPy for efficient array operations and Pygame for the GUI. All core logic is in `game/`, making it easy to extend or test independently.

## Core Components

### 1. Main Entry Point (`main.py`)

This file is the program's starting point. It is simple and serves as a launcher.

**Key Code Lines:**
- **Lines 1-7 (Docstring and Imports)**:
  ```python
  """
  main.py: Entry point for Puzzle Challenge.
  Initializes config, loads GUI, and starts the game loop.
  """
  import pygame
  from gui.game_window import GameWindow
  ```
  - **Explanation**: Imports Pygame for graphics and the `GameWindow` class from the GUI module. The docstring describes its purpose: setting up the game environment.

- **Lines 8-12 (main Function)**:
  ```python
  def main():
      pygame.init()
      window = GameWindow()
      window.run()
      pygame.quit()
  ```
  - **Explanation**: 
    - `pygame.init()`: Initializes all Pygame modules.
    - `GameWindow()`: Creates an instance of the GUI window, which handles rendering and user interaction.
    - `window.run()`: Starts the main game loop in the GUI, processing events and updates.
    - `pygame.quit()`: Cleans up Pygame resources on exit.
  - **How it Works**: This function encapsulates the entire application lifecycle. The `GameWindow` class (in `gui/game_window.py`) is responsible for integrating the board, solvers, and GUI elements.

- **Lines 13-16 (Script Execution)**:
  ```python
  if __name__ == "__main__":
      main()
  ```
  - **Explanation**: Ensures `main()` runs only when the script is executed directly, following Python best practices.

**Overall Functionality**: `main.py` acts as a bootstrapper. It sets up the environment and delegates control to the GUI, where all interactive features (e.g., puzzle manipulation, auto-solve) occur.

### 2. Board Logic (`game/board.py`)

The `Board` class represents the sliding puzzle grid. It handles state management, ensuring the puzzle is solvable, and processes moves.

**Key Code Lines (Line-by-Line Breakdown):**
- **Lines 1-6 (Docstring and Imports)**:
  ```python
  """
  board.py: Board logic and tile movement for Puzzle Challenge.
  """
  import numpy as np
  import random
  ```
  - **Explanation**: Uses NumPy for 2D array operations (e.g., tile grid) and `random` for shuffling.

- **Lines 7-18 (Board Class and __init__)**:
  ```python
  class Board:
      """
      Board class for the sliding puzzle.
      Handles grid state, shuffling, tile movement, and provides helpers for rendering and logic.
      """
      def __init__(self, size=3):
          # Ensure the board size is valid (3x3 to 6x6)
          assert 3 <= size <= 6, "Grid size must be between 3 and 6."
          self.size = size
          self.tiles = self._create_solved_board()  # 2D numpy array
          self.blank_pos = (size - 1, size - 1)     # Position of the blank (0)
          self.shuffle()                            # Shuffle to a solvable state
  ```
  - **Explanation**:
    - `assert`: Validates board size for performance (larger grids are computationally intensive).
    - `self.tiles`: A NumPy array representing the grid (e.g., for 3x3: numbers 1-8 and 0 for blank).
    - `self.blank_pos`: Tracks the blank tile's position for efficient move checks.
    - `self.shuffle()`: Generates a random, solvable puzzle (detailed below).
  - **How it Works**: Initialization creates a solved board and shuffles it, ensuring solvability via inversion counts (a key AI concept for sliding puzzles).

- **Lines 20-28 (_create_solved_board)**:
  ```python
  def _create_solved_board(self):
      """
      Return a solved board as a 2D numpy array.
      The blank (0) is in the last position.
      """
      n = self.size
      arr = np.arange(1, n*n)
      arr = np.append(arr, 0)  # 0 is the blank
      return arr.reshape((n, n))
  ```
  - **Explanation**: Creates a solved state (tiles 1 to N^2-1, blank at bottom-right). Used as the goal in solvers.

- **Lines 30-41 (is_solved)**:
  ```python
  def is_solved(self):
      """
      Check if the board is in a solved state (tiles in order, blank at end).
      """
      n = self.size
      solved = np.arange(1, n*n)
      solved = np.append(solved, 0)
      return np.array_equal(self.tiles.flatten(), solved)
  ```
  - **Explanation**: Flattens the grid and compares to a solved array. Used in GUI to detect win conditions.

- **Lines 43-57 (shuffle)**:
  ```python
  def shuffle(self):
      """
      Shuffle the board to a random, solvable state.
      Uses the number of inversions to ensure solvability.
      """
      n = self.size
      arr = np.arange(1, n*n)
      arr = np.append(arr, 0)
      while True:
          np.random.shuffle(arr)
          board = arr.reshape((n, n))
          if self._is_solvable(board) and not self._is_solved_flat(arr):
              self.tiles = board
              self.blank_pos = tuple(map(int, np.argwhere(board == 0)[0]))
              break
  ```
  - **Explanation**: Shuffles tiles and checks solvability using inversion parity (odd grids: even inversions; even grids: adjusted by blank row). Ensures only solvable puzzles are generated, preventing unsolvable states.

- **Lines 66-82 (_is_solvable)**:
  ```python
  def _is_solvable(self, board):
      """
      Check if a board is solvable (based on inversion count).
      Odd grid: even inversions. Even grid: depends on blank row.
      """
      flat = board.flatten()
      n = self.size
      inv = 0
      for i in range(len(flat)):
          for j in range(i+1, len(flat)):
              if flat[i] and flat[j] and flat[i] > flat[j]:
                  inv += 1
      if n % 2 == 1:
          return inv % 2 == 0
      else:
          row_blank = np.where(board == 0)[0][0]
          return (inv + n - row_blank) % 2 == 0
  ```
  - **Explanation**: Counts tile inversions (pairs out of order). Solvability rules are based on parity theory for sliding puzzles.

- **Lines 84-103 (move)**:
  ```python
  def move(self, direction):
      """
      Move a tile in the given direction ('up', 'down', 'left', 'right') if possible.
      Returns True if moved, False otherwise.
      """
      x, y = self.blank_pos
      dx, dy = 0, 0
      if direction == 'up': dx, dy = -1, 0
      elif direction == 'down': dx, dy = 1, 0
      elif direction == 'left': dx, dy = 0, -1
      elif direction == 'right': dx, dy = 0, 1
      else: return False
      nx, ny = x + dx, y + dy
      if 0 <= nx < self.size and 0 <= ny < self.size:
          self.tiles[x, y], self.tiles[nx, ny] = self.tiles[nx, ny], self.tiles[x, y]
          self.blank_pos = (nx, ny)
          return True
      return False
  ```
  - **Explanation**: Swaps the blank with an adjacent tile if valid. Updates `blank_pos` for efficiency.

**Overall Functionality**: `Board` manages the puzzle state, ensuring valid and solvable configurations. Moves are atomic and reversible, supporting the search algorithms.

### 3. Auto-Solve Algorithms (`game/solver.py`)

This module implements the core AI for solving the puzzle using various search strategies. Each solver returns a path of moves, step count, and statistics.

**Key Code Lines (Line-by-Line Breakdown):**
- **Lines 1-14 (Docstring and Imports)**:
  ```python
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
  ```
  - **Explanation**: Uses `heapq` for priority queues (UCS, Greedy, A*) and `deque` for BFS. States are tuples: (tiles, blank_pos).

- **Lines 15-30 (get_neighbors)**:
  ```python
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
  ```
  - **Explanation**: Generates possible moves by swapping the blank with adjacent tiles. Returns new states and actions.

- **Lines 43-57 (dfs_solver)**:
  ```python
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
  ```
  - **Explanation**: Uses a stack for LIFO (depth-first). Explores deeply first; may find solutions quickly but not optimally. Tracks visited states to avoid cycles.

- **Lines 59-101 (bfs_solver)**:
  ```python
  def bfs_solver(start, goal):
      """
      Breadth-First Search (BFS) solver.
      """
      queue = deque([(start, [])])
      visited = set()
      goal_tiles_tuple = tuple(map(tuple, goal[0]))
      while queue:
          state, path = queue.popleft()
          current_tiles, current_blank = state
          current_tiles_tuple = tuple(map(tuple, current_tiles))
          if current_tiles_tuple == goal_tiles_tuple:
              return path, len(path), {'explored': len(visited)}
          state_key = (current_tiles_tuple, current_blank)
          if state_key in visited:
              continue
          visited.add(state_key)
          for neighbor, action in get_neighbors(state):
              queue.append((neighbor, path + [action]))
      return None, 0, {'explored': len(visited)}
  ```
  - **Explanation**: Uses a queue for FIFO (breadth-first). Guarantees shortest path in unweighted graph (optimal moves). Converts to tuples for hashing.

- **Lines 103-140 (ucs_solver)**:
  ```python
  def ucs_solver(start, goal):
      """
      Uniform Cost Search (UCS) solver.
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
  ```
  - **Explanation**: Uses a priority queue with cost (uniform 1 per move). Similar to BFS but for weighted graphs; here, it's equivalent since costs are uniform.

- **Lines 142-185 (greedy_solver)**:
  ```python
  def greedy_solver(start, goal, heuristic):
      """
      Greedy Best-First Search solver.
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
              heapq.heappush(heap, (heuristic(neighbor[0], goal[0]), next(counter), neighbor, path + [action]))
      return None, 0, {'explored': len(visited)}
  ```
  - **Explanation**: Prioritizes nodes with lowest heuristic value (e.g., Manhattan distance). Fast but not optimal.

- **Lines 187-227 (astar_solver)**:
  ```python
  def astar_solver(start, goal, heuristic):
      """
      A* Search solver.
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
  ```
  - **Explanation**: Combines cost (g) and heuristic (h) for f = g + h. Guarantees optimal path if heuristic is admissible.

**Overall Functionality**: These algorithms model the puzzle as a graph search problem. DFS and BFS are uninformed; UCS, Greedy, and A* are informed, using heuristics for efficiency.

### 4. Heuristics (`game/heuristics.py`)

Heuristics estimate the distance to the goal, guiding informed searches.

**Key Code Lines:**
- **Lines 13-29 (misplaced_tiles)**:
  ```python
  def misplaced_tiles(state, goal):
      """
      Heuristic: Count the number of tiles not in their goal position (excluding blank).
      Lower is better; 0 means solved.
      """
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
  ```
  - **Explanation**: Simple count of misplaced tiles. Admissible but not consistent.

- **Lines 31-57 (manhattan_distance)**:
  ```python
  def manhattan_distance(state, goal):
      """
      Heuristic: Total Manhattan distance of all tiles from their goal positions (excluding blank).
      Lower is better; 0 means solved.
      """
      if hasattr(state, 'tolist'):
          state = state.tolist()
      if hasattr(goal, 'tolist'):
          goal = goal.tolist()
      distance = 0
      n = len(state)
      goal_pos = {}
      for i in range(n):
          for j in range(n):
              goal_pos[goal[i][j]] = (i, j)
      for i in range(n):
          for j in range(n):
              val = state[i][j]
              if val != 0:
                  goal_i, goal_j = goal_pos[val]
                  distance += abs(i - goal_i) + abs(j - goal_j)
      return distance
  ```
  - **Explanation**: Sums |dx| + |dy| for each tile to its goal. Admissible and consistent, often optimal with A*.

- **Lines 59-70 (custom_heuristic)**:
  ```python
  def custom_heuristic(state, goal):
      """
      Custom heuristic: Manhattan distance + 0.5 * misplaced tiles.
      Combines both heuristics for a potentially better estimate.
      """
      if hasattr(state, 'tolist'):
          state = state.tolist()
      if hasattr(goal, 'tolist'):
          goal = goal.tolist()
      return manhattan_distance(state, goal) + 0.5 * misplaced_tiles(state, goal)
  ```
  - **Explanation**: Hybrid to leverage strengths of both.

**Overall Functionality**: Heuristics make informed searches efficient. Manhattan is preferred for A* due to consistency.

### 5. Statistics (`game/statistics.py`)

Tracks performance for analysis and comparison.

**Key Code Lines:**
- **Lines 6-12 (Statistics Class)**:
  ```python
  class Statistics:
      """
      Tracks and stores AI/heuristic performance for the puzzle game.
      Stores results as a list of dicts for each (algorithm, heuristic) pair.
      """
      def __init__(self):
          self.data = defaultdict(list)  # (algo, heuristic) -> list of dicts
  ```
  - **Explanation**: Uses a dict of lists to store metrics per (algorithm, heuristic) combo.

- **Lines 14-20 (add_result)**:
  ```python
  def add_result(self, algo, heuristic, time_taken, steps, explored):
      """Add a result for a specific algorithm and heuristic."""
      self.data[(algo, heuristic)].append({
          'time': time_taken,
          'steps': steps,
          'explored': explored
      })
  ```
  - **Explanation**: Records metrics for each run.

- **Lines 22-35 (get_summary)**:
  ```python
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
  ```
  - **Explanation**: Computes averages for comparison.

**Overall Functionality**: Enables empirical evaluation of algorithms, useful for demonstrating AI performance trade-offs.

## Integration and Usage

- **GUI Integration**: In `gui/game_window.py`, users select algorithms and heuristics via UI. The solver runs in the background, applying moves sequentially.
- **Tests**: `test_auto_solve.py` simulates runs without GUI, verifying solvers and providing output for validation.
- **How It All Works**: The board provides state; solvers use heuristics to find paths; statistics track efficiency. For example, A* with Manhattan often solves fastest for optimal paths.

## Conclusion

This program exemplifies AI in practice: modeling problems as graphs, applying search algorithms, and using heuristics for efficiency. For your presentation, demonstrate a puzzle, run auto-solve (e.g., A*), and discuss statistics. Total implementation is clean, modular, and educational. If needed, extend with more algorithms or visualizations!
