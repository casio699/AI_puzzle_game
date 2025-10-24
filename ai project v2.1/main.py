"""
main.py: Entry point for Puzzle Challenge.
Initializes config, loads GUI, and starts the game loop.
"""
import pygame
from gui.game_window import GameWindow

def main():
    pygame.init()
    window = GameWindow()
    window.run()
    pygame.quit()

if __name__ == "__main__":
    main()
