"""
game_window.py: Main game window and layout for Puzzle Challenge.
"""
import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, DEFAULT_THEME

class GameWindow:
    """
    Main game window class for Puzzle Challenge.
    Handles all rendering, event processing, game logic, AI, statistics, and UI integration.
    Designed for clarity, modularity, and easy in-class editing.
    """
    def __init__(self):
        # Import dependencies and initialize window
        from game.board import Board
        from gui.controls import Button
        from game.statistics import Statistics
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Puzzle Challenge")
        self.clock = pygame.time.Clock()
        self.running = True
        # Theme and board
        self.theme = DEFAULT_THEME
        self.board = Board(size=3)  # Default to 3x3 grid
        self.tile_size = min(WINDOW_WIDTH, WINDOW_HEIGHT-100) // self.board.size
        self.margin = 30
        # Store the initial state for reset (for true "reset" functionality)
        self.initial_tiles = self.board.tiles.copy()
        self.initial_blank = self.board.blank_pos
        # Puzzle solved state
        self.puzzle_solved = False
        # Timer and step counter
        self.timer_started = False
        self.start_ticks = 0
        self.elapsed_time = 0
        self.steps = 0
        self.initial_steps = 0
        self.initial_time = 0
        # Music and sound toggles
        self.music_on = True
        self.sound_on = True
        # UI control/button lists
        self.buttons = []           # Main game controls (reset, new, etc)
        self.sound_buttons = []     # Sound/music/theme controls
        # AI/solver controls
        self.solver_algos = ['DFS', 'BFS', 'UCS', 'Greedy', 'A*']
        self.heuristics = ['misplaced', 'manhattan', 'custom']
        self.selected_algo = 0
        self.selected_heuristic = 0
        self.solver_buttons = []    # Buttons for solver controls
        self.solver_animating = False
        self.solver_path = []
        self.solver_anim_idx = 0
        self.solver_anim_delay = 300  # ms between auto-solve animation steps
        self.solver_last_anim = 0
        # Statistics tracker for AI/heuristics
        self.statistics = Statistics()
        # Initialize all UI and system components
        self._init_buttons()
        self._init_sound()
        self._init_theme()
        self._init_solver_buttons()

    def _init_buttons(self):
        from gui.controls import Button
        font = pygame.font.SysFont(None, 28)
        btn_w, btn_h = 120, 40
        gap = 20
        y = WINDOW_HEIGHT - btn_h - 15
        x = (WINDOW_WIDTH - (btn_w*4 + gap*3)) // 2
        def reset_board():
            import numpy as np
            self.board.tiles = self.initial_tiles.copy()
            self.board.blank_pos = self.initial_blank
            self.steps = self.initial_steps
            self.elapsed_time = self.initial_time
            self.timer_started = False
            self.solver_animating = False
        def new_board():
            self.board.set_size(self.board.size)
            self.initial_tiles = self.board.tiles.copy()
            self.initial_blank = self.board.blank_pos
            self.steps = 0
            self.elapsed_time = 0
            self.timer_started = False
            self.initial_steps = 0
            self.initial_time = 0
            self.solver_animating = False
        def quit_game(): self.running = False
        def next_size():
            s = self.board.size + 1 if self.board.size < 6 else 3
            self.board.set_size(s)
            self.initial_tiles = self.board.tiles.copy()
            self.initial_blank = self.board.blank_pos
            self.steps = 0
            self.elapsed_time = 0
            self.timer_started = False
            self.initial_steps = 0
            self.initial_time = 0
            self.solver_animating = False
        self.buttons = [
            Button((x, y, btn_w, btn_h), "Reset", reset_board, font=font),
            Button((x+btn_w+gap, y, btn_w, btn_h), "New", new_board, font=font),
            Button((x+2*(btn_w+gap), y, btn_w, btn_h), f"Size: {self.board.size}x{self.board.size}", next_size, font=font),
            Button((x+3*(btn_w+gap), y, btn_w, btn_h), "Quit", quit_game, font=font)
        ]
        # Top-right music/sound/theme buttons
        music_x = WINDOW_WIDTH - 390
        music_y = 60
        def toggle_music():
            self.music_on = not self.music_on
            if self.music_on:
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.stop()
        def toggle_sound():
            self.sound_on = not self.sound_on
        def next_theme():
            from gui.themes import next_theme as theme_next, get_current_theme
            self.theme = theme_next()
        self.sound_buttons = [
            Button((music_x, music_y, 110, 36), lambda: f"Music {'On' if self.music_on else 'Off'}", toggle_music, font=font),
            Button((music_x+120, music_y, 110, 36), lambda: f"Sound {'On' if self.sound_on else 'Off'}", toggle_sound, font=font),
            Button((music_x+240, music_y, 110, 36), "Theme", next_theme, font=font)
        ]

    def _update_size_button(self):
        # Update the label of the size button
        self.buttons[2].text = f"Size: {self.board.size}x{self.board.size}"

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            # Animate solver if active
            if self.solver_animating and self.solver_path:
                now = pygame.time.get_ticks()
                if now - self.solver_last_anim > self.solver_anim_delay:
                    move = self.solver_path[self.solver_anim_idx]
                    self.board.move(move)
                    self.solver_anim_idx += 1
                    self.solver_last_anim = now
                    if self.solver_anim_idx >= len(self.solver_path):
                        self.solver_animating = False
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Prevent moves if solved, but allow button presses
            if self.puzzle_solved:
                for btn in self.buttons:
                    btn.handle_event(event)
                for btn in self.sound_buttons:
                    btn.handle_event(event)
                for btn in self.solver_buttons:
                    btn.handle_event(event)
                continue
            elif event.type == pygame.KEYDOWN:
                # Arrow key controls for tile movement
                if event.key == pygame.K_UP:
                    moved = self.board.move('up')
                elif event.key == pygame.K_DOWN:
                    moved = self.board.move('down')
                elif event.key == pygame.K_LEFT:
                    moved = self.board.move('left')
                elif event.key == pygame.K_RIGHT:
                    moved = self.board.move('right')
            # Pass events to buttons
            for btn in self.buttons:
                btn.handle_event(event)
            for btn in self.sound_buttons:
                btn.handle_event(event)
            for btn in self.solver_buttons:
                btn.handle_event(event)
            # Mouse click: move tile if adjacent to blank
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                n = self.board.size
                # Use updated grid offset for mouse detection
                top_offset = 60 + 32 + 10 + (22 * 4) + 20
                self.tile_size = min(WINDOW_WIDTH, WINDOW_HEIGHT-top_offset-100) // n
                offset_x = (WINDOW_WIDTH - n*self.tile_size) // 2
                offset_y = top_offset
                col = (mx - offset_x) // self.tile_size
                row = (my - offset_y) // self.tile_size
                if 0 <= row < n and 0 <= col < n:
                    blank_x, blank_y = self.board.blank_pos
                    # Check if clicked tile is adjacent to blank
                    if abs(blank_x - row) + abs(blank_y - col) == 1:
                        # Move blank in the direction of the clicked tile
                        if row == blank_x:
                            if col < blank_y:
                                moved = self.board.move('left')
                            else:
                                moved = self.board.move('right')
                        elif col == blank_y:
                            if row < blank_x:
                                moved = self.board.move('up')
                            else:
                                moved = self.board.move('down')
                self._update_size_button()
        # Play sound effect on move
        if moved and self.sound_on:
            if hasattr(self, 'move_sound') and self.move_sound:
                self.move_sound.play()
        # Start timer on first move
        if moved and not self.timer_started:
            self.timer_started = True
            self.start_ticks = pygame.time.get_ticks()
        # Increment steps on every valid move
        if moved:
            self.steps += 1

    def draw(self):
        # Fill with theme background or default
        bg_color = self.theme.get('background', (40, 44, 52))
        self.screen.fill(bg_color)
        
        # Draw a subtle gradient background
        gradient = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            # Create a subtle gradient from top to bottom
            intensity = 1.0 - (y / WINDOW_HEIGHT * 0.1)  # 10% darker at bottom
            r = min(255, int(bg_color[0] * intensity))
            g = min(255, int(bg_color[1] * intensity))
            b = min(255, int(bg_color[2] * intensity))
            pygame.draw.line(gradient, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        self.screen.blit(gradient, (0, 0))
        
        # Draw UI components in order (back to front)
        self._draw_grid()  # Grid first (background)
        self._draw_top_bar()  # Top bar with title and timer
        self._draw_sound_buttons()  # Sound and theme controls
        self._draw_buttons()  # Main game buttons (reset, new, etc.)
        
        # Draw puzzle solved message if applicable
        if self.board.is_solved():
            self.puzzle_solved = True
            self._draw_solved_message()
            # Pause timer
            if self.timer_started:
                self.elapsed_time += (pygame.time.get_ticks() - self.start_ticks) / 1000
                self.timer_started = False
        else:
            self.puzzle_solved = False
            # Update timer
            if self.timer_started:
                self.current_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
            else:
                self.current_time = 0
        # TODO: Draw statistics, etc.

    def _draw_top_bar(self):
        """
        Draw the timer and step counter at the top of the window.
        """
        # Draw a semi-transparent background for the top bar
        top_bar = pygame.Surface((WINDOW_WIDTH, 50), pygame.SRCALPHA)
        top_bar.fill((40, 44, 52, 200))  # Semi-transparent dark background
        self.screen.blit(top_bar, (0, 0))
        
        # Draw title in the center
        title_font = pygame.font.SysFont('Arial', 28, bold=True)
        title = title_font.render("Puzzle Challenge", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 25))
        self.screen.blit(title, title_rect)
        
        # Timer and steps with improved styling
        font = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Timer value
        if self.timer_started:
            time_val = self.elapsed_time + (pygame.time.get_ticks() - self.start_ticks) / 1000
        else:
            time_val = self.elapsed_time
            
        time_str = f"Time: {time_val:05.1f}s"
        steps_str = f"Steps: {self.steps}"
        
        # Draw timer and steps at bottom of top bar
        time_surf = font.render(time_str, True, (255, 255, 255))
        steps_surf = font.render(steps_str, True, (255, 255, 255))
        
        # Position at bottom of top bar with padding
        self.screen.blit(time_surf, (20, 30))
        self.screen.blit(steps_surf, (WINDOW_WIDTH - steps_surf.get_width() - 20, 30))

    def _draw_sound_buttons(self):
        # Draw a subtle background for the control panel
        panel_height = 50
        panel = pygame.Surface((WINDOW_WIDTH, panel_height), pygame.SRCALPHA)
        #panel.fill((50, 54, 60, 180))  # Semi-transparent dark background
        self.screen.blit(panel, (0, 50))  # Position below top bar (50px from top)
        
        # Position sound buttons in the control panel
        x_pos = 20
        y_pos = 50  # Below the top bar
        
        for btn in self.sound_buttons:
            # Update button position and size
            btn.rect.x = x_pos
            btn.rect.y = y_pos
            btn.rect.width = 100  # Fixed width for consistency
            
            # Update button label dynamically
            if callable(btn.text):
                btn.text = btn.text()
                
            # Adjust font size for better fit
            btn.font = pygame.font.SysFont('Arial', 16)
            btn.draw(self.screen)
            
            # Update position for next button
            x_pos += btn.rect.width + 10
        
        # Draw solver controls below the sound buttons
        self._draw_solver_controls()

    def _draw_solved_message(self):
        font = pygame.font.SysFont(None, 60)
        msg = font.render("Puzzle Solved!", True, (0, 200, 0))
        rect = msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        pygame.draw.rect(self.screen, (255,255,255), rect.inflate(40,40), border_radius=15)
        self.screen.blit(msg, rect)

    def _draw_buttons(self):
        for btn in self.buttons:
            btn.draw(self.screen)

    def _init_sound(self):
        import pygame
        import os
        # Load background music and sound effect (placeholder files)
        music_path = os.path.join('assets', 'music', 'bgm.ogg')
        sound_path = os.path.join('assets', 'sounds', 'move.wav')
        pygame.mixer.init()
        self.move_sound = None
        # Background music (robust to missing/invalid file)
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                if self.music_on:
                    pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"[Warning] Could not load music: {e}")
        # Move sound effect
        if os.path.exists(sound_path):
            try:
                self.move_sound = pygame.mixer.Sound(sound_path)
            except Exception as e:
                print(f"[Warning] Could not load move sound: {e}")

    def _init_theme(self):
        from gui.themes import get_current_theme
        self.theme = get_current_theme()

    def _draw_grid(self):
        """Draw the puzzle grid and tiles."""
        n = self.board.size
        
        # Calculate UI elements height
        top_bar_height = 50  # Top bar
        sound_controls_height = 40  # Sound controls
        solver_controls_height = 50  # Solver controls
        stats_panel_height = 100  # Statistics panel
        
        # Total height of all UI elements above the grid
        total_ui_height = top_bar_height + sound_controls_height + solver_controls_height + stats_panel_height
        
        # Calculate available height for the grid with some padding
        available_height = WINDOW_HEIGHT - total_ui_height - 40  # 40px bottom margin
        
        # Calculate maximum possible tile size that fits in the available space
        max_tile_width = (WINDOW_WIDTH - 80) // n  # Max width with 40px padding on each side
        max_tile_height = (available_height - 40) // n  # Max height with 20px padding
        tile_size = min(max_tile_width, max_tile_height)
        
        # Calculate total grid size
        grid_size = tile_size * n
        
        # Calculate grid position (centered horizontally, below UI elements)
        grid_x = (WINDOW_WIDTH - grid_size) // 2
        grid_y = total_ui_height + 20  # 20px margin below UI elements
        
        # Store the grid rectangle for click handling
        self.grid_rect = pygame.Rect(grid_x, grid_y, grid_size, grid_size)
        
        # Draw grid background
        pygame.draw.rect(self.screen, (60, 63, 65), self.grid_rect)  # Dark gray background
        
        # Calculate tile padding
        tile_padding = 2
        tile_size_with_padding = tile_size - (2 * tile_padding)
        
        # Draw each tile
        font = pygame.font.SysFont('Arial', max(12, tile_size_with_padding // 2), bold=True)
        
        for row in range(n):
            for col in range(n):
                val = self.board.get_tile(row, col)
                
                # Calculate tile position with padding
                x = grid_x + col * tile_size + tile_padding
                y = grid_y + row * tile_size + tile_padding
                
                rect = pygame.Rect(
                    x,
                    y,
                    tile_size_with_padding,
                    tile_size_with_padding
                )
                
                # Draw tile background
                if val == 0:  # Empty tile
                    pygame.draw.rect(self.screen, self.theme.get('empty_tile', (80, 80, 80)), rect, border_radius=4)
                else:  # Numbered tile
                    # Draw tile with gradient or solid color
                    pygame.draw.rect(self.screen, self.theme.get('tile', (100, 149, 237)), rect, border_radius=4)
                    
                    # Draw highlight on top edge for 3D effect
                    highlight = pygame.Surface((tile_size_with_padding, 2), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 50))
                    self.screen.blit(highlight, (x, y))
                    
                    # Draw number
                    txt = font.render(str(val), True, self.theme.get('tile_text', (255, 255, 255)))
                    txt_rect = txt.get_rect(center=rect.center)
                    self.screen.blit(txt, txt_rect)
                
                # Draw border
                pygame.draw.rect(self.screen, (120, 120, 120, 100), rect, 1, border_radius=4)
                
        # Update the tile size for click handling
        self.tile_size = tile_size

    def _init_solver_buttons(self):
        from gui.controls import Button
        
        # Define layout constants
        panel_padding = 20
        button_height = 36
        button_spacing = 15
        section_spacing = 30
        
        # Calculate positions
        y_pos = 110  # Start below the top controls
        
        # Only create new buttons if they don't exist yet
        if not hasattr(self, 'solver_buttons') or not self.solver_buttons:
            # Define button callbacks
            def prev_algo():
                self.selected_algo = (self.selected_algo - 1) % len(self.solver_algos)
                self._update_solver_button_labels()
                
            def next_algo():
                self.selected_algo = (self.selected_algo + 1) % len(self.solver_algos)
                self._update_solver_button_labels()
                
            def prev_heur():
                self.selected_heuristic = (self.selected_heuristic - 1) % len(self.heuristics)
                self._update_solver_button_labels()
                
            def next_heur():
                self.selected_heuristic = (self.selected_heuristic + 1) % len(self.heuristics)
                self._update_solver_button_labels()
                
            def auto_solve():
                self._run_solver()
            
            # Create a list to hold all buttons
            self.solver_buttons = []
            
            # Algorithm selection section
            algo_x = panel_padding
            algo_btn_w = 100
            
            # Previous algorithm button
            self.solver_buttons.append(Button(
                (algo_x, y_pos, 40, button_height), 
                '◀', 
                prev_algo, 
                font=pygame.font.SysFont('Arial', 16, bold=True)
            ))
            
            # Algorithm display (readonly)
            self.solver_buttons.append(Button(
                (algo_x + 45, y_pos, 110, button_height), 
                '', 
                None, 
                font=pygame.font.SysFont('Arial', 14, bold=True),
                color=(70, 70, 80),  # Dark gray background
                text_color=(200, 200, 200)  # Light gray text
            ))
            
            # Next algorithm button
            self.solver_buttons.append(Button(
                (algo_x + 160, y_pos, 40, button_height), 
                '▶', 
                next_algo, 
                font=pygame.font.SysFont('Arial', 16, bold=True)
            ))
            
            # Heuristic selection section (to the right of algorithm section)
            heur_x = algo_x + 220
            
            # Previous heuristic button
            self.solver_buttons.append(Button(
                (heur_x, y_pos, 40, button_height), 
                '◀', 
                prev_heur, 
                font=pygame.font.SysFont('Arial', 16, bold=True)
            ))
            
            # Heuristic display (readonly)
            self.solver_buttons.append(Button(
                (heur_x + 45, y_pos, 120, button_height), 
                '', 
                None, 
                font=pygame.font.SysFont('Arial', 14, bold=True),
                color=(70, 70, 80),  # Dark gray background
                text_color=(200, 200, 200)  # Light gray text
            ))
            
            # Next heuristic button
            self.solver_buttons.append(Button(
                (heur_x + 170, y_pos, 40, button_height), 
                '▶', 
                next_heur, 
                font=pygame.font.SysFont('Arial', 16, bold=True)
            ))
            
            # Auto Solve button (on the right side)
            solve_btn_w = 120
            solve_btn_x = WINDOW_WIDTH - solve_btn_w - panel_padding
            
            self.solver_buttons.append(Button(
                (solve_btn_x, y_pos, solve_btn_w, button_height), 
                'Auto Solve', 
                auto_solve, 
                font=pygame.font.SysFont('Arial', 15, bold=True),
                color=(65, 105, 225),  # Royal blue
                text_color=(255, 255, 255)  # White text
            ))
        
        # Always update the button labels
        self._update_solver_button_labels()
    
    def _update_solver_button_labels(self):
        """Update the text of the solver buttons without recreating them."""
        if hasattr(self, 'solver_buttons') and len(self.solver_buttons) >= 6:
            # Update algorithm display button
            self.solver_buttons[1].text = self.solver_algos[self.selected_algo]
            # Update heuristic display button
            self.solver_buttons[4].text = self.heuristics[self.selected_heuristic]
            # Force a redraw
            self.draw()
            pygame.display.flip()

    def _draw_solver_controls(self):
        # Draw a panel background for solver controls
        panel_height = 50
        panel = pygame.Surface((WINDOW_WIDTH, panel_height), pygame.SRCALPHA)
        #panel.fill((40, 44, 52, 180))  # Semi-transparent dark background
        self.screen.blit(panel, (0, 95))  # Position below sound controls (90px from top)
        
        # Draw solver buttons
        for btn in self.solver_buttons:
            if callable(btn.text):
                btn.text = btn.text()
            btn.draw(self.screen)
        
        # Draw current selection as labels above the buttons
        font = pygame.font.SysFont('Arial', 14, bold=True)
        algo = self.solver_algos[self.selected_algo]
        heur = self.heuristics[self.selected_heuristic]
        
        # Draw algorithm and heuristic labels
        algo_label = font.render("Algorithm:", True, (200, 200, 200))
        heur_label = font.render("Heuristic:", True, (200, 200, 200))
        
        self.screen.blit(algo_label, (30, 90))
        self.screen.blit(heur_label, (250, 90))
        
        # Draw statistics panel below the controls
        self._draw_statistics_panel()
    
    def _draw_statistics_panel(self):
        """Draw the statistics panel below the solver controls."""
        # Panel position and size
        panel_x = 20
        panel_y = 150  # Below the solver controls (90px + 60px)
        panel_width = WINDOW_WIDTH - 40
        panel_height = 100  # Reduced height to prevent overlap
        
        # Draw panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((50, 54, 60, 180))  # Semi-transparent dark background
        pygame.draw.rect(panel, (80, 85, 95, 200), panel.get_rect(), 1)  # Border
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 16, bold=True)
        title = title_font.render("Solver Statistics", True, (220, 220, 255))
        self.screen.blit(title, (panel_x + 10, panel_y + 8))
        
        # Get current algorithm and heuristic
        algo = self.solver_algos[self.selected_algo]
        heur = self.heuristics[self.selected_heuristic]
        stats = self.statistics.get_summary(algo, heur)
        
        # Prepare statistics text
        font = pygame.font.SysFont('Arial', 14)
        
        if stats:
            # Format statistics
            time_text = f"Time: {stats['avg_time']:.2f}s"
            steps_text = f"Steps: {stats['avg_steps']:.1f}"
            nodes_text = f"Nodes: {stats['avg_explored']:.0f}"
            runs_text = f"Runs: {stats['runs']}"
            
            # Render statistics
            time_surf = font.render(time_text, True, (220, 220, 220))
            steps_surf = font.render(steps_text, True, (220, 220, 220))
            nodes_surf = font.render(nodes_text, True, (220, 220, 220))
            runs_surf = font.render(runs_text, True, (220, 220, 220))
            
            # Position statistics in two columns
            col1_x = panel_x + 20
            col2_x = panel_x + panel_width // 2 + 10
            row_height = 28
            start_y = panel_y + 40
            
            self.screen.blit(time_surf, (col1_x, start_y))
            self.screen.blit(steps_surf, (col1_x, start_y + row_height))
            self.screen.blit(nodes_surf, (col2_x, start_y))
            self.screen.blit(runs_surf, (col2_x, start_y + row_height))
        else:
            # No statistics available
            no_stats = font.render("No statistics available yet. Run the solver to see metrics.", 
                                 True, (180, 180, 180))
            self.screen.blit(no_stats, (panel_x + 20, panel_y + 40))

    def _run_solver(self):
        import time
        import numpy as np
        from game.solver import dfs_solver, bfs_solver, ucs_solver, greedy_solver, astar_solver
        from game.heuristics import misplaced_tiles, manhattan_distance, custom_heuristic
        from utils.error_handling import show_error
        algo = self.solver_algos[self.selected_algo]
        heur = self.heuristics[self.selected_heuristic]
        start_state = (self.board.tiles.copy(), self.board.blank_pos)
        n = self.board.size
        # Create goal tiles as a numpy array
        goal_tiles = np.arange(1, n*n + 1)  # Create numbers from 1 to n²
        goal_tiles[-1] = 0  # Set last element to 0 (empty space)
        goal_tiles = goal_tiles.reshape((n, n))  # Now reshape to n×n
        # Find the position of 0 (empty space)
        zero_pos = np.argwhere(goal_tiles == 0)[0]
        goal_blank = tuple(zero_pos)
        goal_state = (goal_tiles, goal_blank)
        solver_map = {
            'DFS': dfs_solver,
            'BFS': bfs_solver,
            'UCS': ucs_solver,
            'Greedy': lambda s, g: greedy_solver(s, g, {'misplaced': misplaced_tiles, 'manhattan': manhattan_distance, 'custom': custom_heuristic}[heur]),
            'A*': lambda s, g: astar_solver(s, g, {'misplaced': misplaced_tiles, 'manhattan': manhattan_distance, 'custom': custom_heuristic}[heur]),
        }
        t0 = time.time()
        try:
            if algo in ['Greedy', 'A*']:
                path, steps, info = solver_map[algo](start_state, goal_state)
            else:
                path, steps, info = solver_map[algo](start_state, goal_state)
        except Exception as e:
            show_error(self.screen, f"Solver error: {str(e)}", WINDOW_WIDTH, WINDOW_HEIGHT)
            self.solver_path = []
            self.solver_animating = False
            return
        t1 = time.time()
        if path is not None:
            self.solver_path = path
            self.solver_anim_idx = 0
            self.solver_animating = True
            self.solver_last_anim = pygame.time.get_ticks()
            # Add to stats
            self.statistics.add_result(algo, heur, t1-t0, steps, info.get('explored', 0))
        else:
            # No solution found
            show_error(self.screen, "No solution found!", WINDOW_WIDTH, WINDOW_HEIGHT)
            self.solver_path = []
            self.solver_animating = False
