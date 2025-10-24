"""
themes.py: Theme management for Puzzle Challenge.
"""

# Example themes
THEMES = {
    'Classic': {
        'background': (30, 30, 30),
        'tile': (200, 200, 200),
        'tile_text': (20, 20, 20),
        'empty_tile': (60, 60, 60),
        'button': (50, 150, 255),
        'button_text': (255, 255, 255),
        'stats_bg': (40, 40, 60),
    },
    'Ocean': {
        'background': (10, 40, 70),
        'tile': (90, 180, 255),
        'tile_text': (0, 40, 80),
        'empty_tile': (30, 70, 110),
        'button': (0, 180, 180),
        'button_text': (255, 255, 255),
        'stats_bg': (20, 60, 100),
    }
}

THEME_NAMES = list(THEMES.keys())

_current_theme_idx = 0

def get_current_theme():
    return THEMES[THEME_NAMES[_current_theme_idx]]

def next_theme():
    global _current_theme_idx
    _current_theme_idx = (_current_theme_idx + 1) % len(THEME_NAMES)
    return get_current_theme()
