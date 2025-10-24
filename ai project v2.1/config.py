"""
config.py: Global settings and constants for Puzzle Challenge.
"""

# Window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
FPS = 60

# Colors (themes can override)
DEFAULT_THEME = {
    'background': (30, 30, 30),
    'tile': (200, 200, 200),
    'tile_text': (20, 20, 20),
    'empty_tile': (60, 60, 60),
    'button': (50, 150, 255),
    'button_text': (255, 255, 255),
    'stats_bg': (40, 40, 60),
}

# Grid
MIN_GRID_SIZE = 3
MAX_GRID_SIZE = 6

# Asset paths
ASSET_PATH = 'assets/'
SOUND_PATH = ASSET_PATH + 'sounds/'
MUSIC_PATH = ASSET_PATH + 'music/'
IMAGE_PATH = ASSET_PATH + 'images/'
