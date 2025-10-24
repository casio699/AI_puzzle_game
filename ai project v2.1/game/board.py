"""
board.py: Board logic and tile movement for Puzzle Challenge.
"""
import numpy as np
import random

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

    def _create_solved_board(self):
        """
        Return a solved board as a 2D numpy array.
        The blank (0) is in the last position.
        """
        n = self.size
        arr = np.arange(1, n*n)
        arr = np.append(arr, 0)  # 0 is the blank
        return arr.reshape((n, n))

    def _flatten(self):
        """Return the board as a flat list (for hashing/comparison)."""
        return self.tiles.flatten().tolist()

    def is_solved(self):
        """
        Check if the board is in a solved state (tiles in order, blank at end).
        """
        n = self.size
        solved = np.arange(1, n*n)
        solved = np.append(solved, 0)
        return np.array_equal(self.tiles.flatten(), solved)

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

    def _is_solved_flat(self, flat):
        """Check if a flat array is in solved order."""
        n = self.size
        solved = np.arange(1, n*n)
        solved = np.append(solved, 0)
        return np.array_equal(flat, solved)

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

    def move(self, direction):
        """
        Move a tile in the given direction ('up', 'down', 'left', 'right') if possible.
        Returns True if moved, False otherwise.
        """
        x, y = self.blank_pos
        dx, dy = 0, 0
        # Determine movement delta
        if direction == 'up': dx, dy = -1, 0
        elif direction == 'down': dx, dy = 1, 0
        elif direction == 'left': dx, dy = 0, -1
        elif direction == 'right': dx, dy = 0, 1
        else: return False
        nx, ny = x + dx, y + dy
        # Check bounds and swap with blank if valid
        if 0 <= nx < self.size and 0 <= ny < self.size:
            self.tiles[x, y], self.tiles[nx, ny] = self.tiles[nx, ny], self.tiles[x, y]
            self.blank_pos = (nx, ny)
            return True
        return False

    def get_tile(self, row, col):
        """
        Return the value of the tile at (row, col). 0 is blank.
        """
        return self.tiles[row, col]

    def set_size(self, size):
        """
        Set a new board size and reshuffle to a new solvable puzzle.
        """
        self.size = size
        self.tiles = self._create_solved_board()
        self.blank_pos = (size - 1, size - 1)
        self.shuffle()
