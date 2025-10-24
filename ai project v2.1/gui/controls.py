"""
controls.py: Button and control definitions for Puzzle Challenge.
"""
import pygame

class Button:
    """
    Simple UI Button for Puzzle Challenge.
    """
    def __init__(self, rect, text, onclick, font=None, color=(50,150,255), text_color=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick  # Function to call when clicked
        self.color = color
        self.text_color = text_color
        self.font = font or pygame.font.SysFont(None, 32)
        self.hovered = False

    def draw(self, surface):
        color = tuple(min(255, c+30) if self.hovered else c for c in self.color)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (80,80,80), self.rect, 2, border_radius=8)
        # Evaluate text if it's callable (for dynamic labels)
        txt_val = self.text() if callable(self.text) else self.text
        txt = self.font.render(txt_val, True, self.text_color)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Evaluate onclick if it's callable
                if callable(self.onclick):
                    self.onclick()
