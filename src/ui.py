import pygame

class Button:
    """A simple clickable button with text."""

    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (70, 80, 90) # Dark grey
        self.hover_color = (90, 100, 110) # Lighter grey
        self.text_color = (255, 255, 255) # White
        self.font = pygame.font.Font(None, 32) # Default font, size 32

    def draw(self, surface: pygame.Surface):
        """Draws the button on the given surface."""
        # Check for mouse hover
        is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        draw_color = self.hover_color if is_hovered else self.color

        pygame.draw.rect(surface, draw_color, self.rect, border_radius=8)

        # Draw text
        if self.text != '':
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """
        Checks if the button was clicked.
        Returns True if a MOUSEBUTTONUP event happens on this button.
        """
        if (
            event.type == pygame.MOUSEBUTTONUP and
            event.button == 1 and # Left mouse button
            self.rect.collidepoint(event.pos)
        ):
            return True
        return False

def draw_text(surface: pygame.Surface, text: str, x: int, y: int, font_size=24, color=(255, 255, 255)):
    """A helper function to draw text on a surface."""
    font = pygame.font.Font(None, font_size)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surf, text_rect)

def wrap_text(surface, text, pos, font, max_width, color=(255, 255, 255)):
    """
    Renders text by wrapping it within a specified width.
    Each line is drawn starting from the given position.
    """
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    x, y = pos
    word_height = 0 # To handle vertical spacing
    for line in words:
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= pos[0] + max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new line.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        if word_height > 0: # Avoid incrementing y if line was empty
             y += word_height  # Start on new line.