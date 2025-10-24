"""
error_handling.py: Error handling and notifications for Puzzle Challenge.
"""
import pygame

def show_error(screen, message, width, height):
    """Display an error message overlay on the given screen."""
    font = pygame.font.SysFont(None, 36)
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    text = font.render(message, True, (255, 80, 80))
    rect = text.get_rect(center=(width//2, height//2))
    overlay.blit(text, rect)
    screen.blit(overlay, (0, 0))
    pygame.display.flip()
    pygame.time.wait(1500)
