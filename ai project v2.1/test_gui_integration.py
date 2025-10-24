#!/usr/bin/env python3
"""
Test script to isolate GUI integration issues with auto-solve
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
import numpy as np

def test_gui_initialization():
    """Test if the GUI components initialize properly"""
    print("Testing GUI initialization...")

    try:
        # Initialize pygame (required for GUI components)
        pygame.init()
        print("✓ Pygame initialized")

        # Test importing GUI components
        from gui.game_window import GameWindow
        from gui.controls import Button
        print("✓ GUI modules imported")

        # Create a minimal window (don't actually display)
        pygame.display.set_mode((1, 1))  # Minimal size to avoid display issues

        # Test creating GameWindow instance (but don't run the main loop)
        window = GameWindow()
        print("✓ GameWindow instance created")

        # Check if solver buttons were initialized
        if hasattr(window, 'solver_buttons') and len(window.solver_buttons) > 0:
            print(f"✓ Solver buttons initialized: {len(window.solver_buttons)} buttons")
            for i, btn in enumerate(window.solver_buttons):
                print(f"  Button {i}: {btn.text if callable(btn.text) else btn.text}")
        else:
            print("✗ Solver buttons not initialized")
            return False

        # Check solver state variables
        solver_attrs = ['solver_algos', 'selected_algo', 'selected_heuristic', 'solver_animating']
        for attr in solver_attrs:
            if hasattr(window, attr):
                value = getattr(window, attr)
                print(f"✓ {attr}: {value}")
            else:
                print(f"✗ Missing attribute: {attr}")
                return False

        pygame.quit()
        print("✓ GUI initialization test passed")
        return True

    except Exception as e:
        print(f"✗ GUI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        return False

def test_button_callbacks():
    """Test if the button callbacks work properly"""
    print("\nTesting button callbacks...")

    try:
        pygame.init()
        pygame.display.set_mode((1, 1))

        from gui.game_window import GameWindow
        window = GameWindow()

        # Test algorithm switching
        original_algo = window.selected_algo
        original_heur = window.selected_heuristic

        # Simulate clicking next algorithm button
        if len(window.solver_buttons) > 1:
            next_algo_btn = window.solver_buttons[1]  # Should be "next algo"
            if hasattr(next_algo_btn, 'action') and next_algo_btn.action:
                next_algo_btn.action()
                new_algo = window.selected_algo
                print(f"✓ Algorithm switched: {original_algo} -> {new_algo}")
            else:
                print("✗ Next algorithm button has no action")

        # Test heuristic switching
        if len(window.solver_buttons) > 4:
            next_heur_btn = window.solver_buttons[4]  # Should be "next heur"
            if hasattr(next_heur_btn, 'action') and next_heur_btn.action:
                next_heur_btn.action()
                new_heur = window.selected_heuristic
                print(f"✓ Heuristic switched: {original_heur} -> {new_heur}")
            else:
                print("✗ Next heuristic button has no action")

        pygame.quit()
        return True

    except Exception as e:
        print(f"✗ Button callback test failed: {e}")
        pygame.quit()
        return False

def test_solver_integration():
    """Test the full integration of solver with GUI state"""
    print("\nTesting solver integration...")

    try:
        pygame.init()
        pygame.display.set_mode((1, 1))

        from gui.game_window import GameWindow
        window = GameWindow()

        # Create a simple solvable state
        window.board.tiles = np.array([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        window.board.blank_pos = (2, 1)
        print(f"Set board to simple state: {window.board.tiles.flatten()}")

        # Reset solver state
        window.solver_animating = False
        window.solver_path = []

        # Test _run_solver method directly
        print("Calling _run_solver()...")
        window._run_solver()

        if window.solver_path:
            print(f"✓ Solver found path: {window.solver_path}")
            print(f"✓ Animation ready: {len(window.solver_path)} steps")
            return True
        else:
            print("✗ Solver found no path")
            return False

    except Exception as e:
        print(f"✗ Solver integration test failed: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        return False
    finally:
        pygame.quit()

def test_animation_system():
    """Test if the animation system works"""
    print("\nTesting animation system...")

    try:
        pygame.init()
        pygame.display.set_mode((1, 1))

        from gui.game_window import GameWindow
        window = GameWindow()

        # Set up a solved path manually
        window.solver_path = ['right', 'up']  # Simple 2-step path
        window.solver_anim_idx = 0
        window.solver_animating = True

        # Test animation step
        original_blank = window.board.blank_pos
        original_tiles = window.board.tiles.copy()

        # Simulate one animation step (what happens in the run loop)
        if window.solver_animating and window.solver_path:
            move = window.solver_path[window.solver_anim_idx]
            moved = window.board.move(move)
            window.solver_anim_idx += 1

            if window.solver_anim_idx >= len(window.solver_path):
                window.solver_animating = False

            print(f"✓ Animation step executed: move '{move}', board changed: {moved}")
            print(f"  Blank moved: {original_blank} -> {window.board.blank_pos}")
            return True
        else:
            print("✗ Animation system not ready")
            return False

    except Exception as e:
        print(f"✗ Animation test failed: {e}")
        pygame.quit()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    print("Puzzle Challenge GUI Integration Test")
    print("="*50)

    tests = [
        ("GUI Initialization", test_gui_initialization),
        ("Button Callbacks", test_button_callbacks),
        ("Solver Integration", test_solver_integration),
        ("Animation System", test_animation_system),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    print("\n" + "="*50)
    print("SUMMARY:")
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("✓ All GUI integration tests passed!")
        print("The auto-solve button should be working. Check user interaction or display issues.")
    else:
        print("✗ Some GUI integration tests failed. These need fixing:")
        for test_name, result in results:
            if not result:
                print(f"  - {test_name}")
