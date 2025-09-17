import pygame
from typing import Optional
import os
from ui import wrap_text # Import the new text wrapper

class Card:
    """Represents a single card in the game."""

    # Class-level set to track filenames that have already failed to load
    _failed_to_load_artwork = set()

    def __init__(self, data: dict):
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.cost: int = data["cost"]
        self.type: str = data["type"]
        self.value: int = data.get("value") # Use .get() for optional fields
        self.description: str = data["description"]
        self.artwork_filename: str = data["artwork"]
        # We will load the pygame.Surface in a separate method
        self.image: Optional[pygame.Surface] = None
        # Add a rect for positioning and collision detection
        self.rect: Optional[pygame.Rect] = None

    def copy(self) -> 'Card':
        """Creates a new Card instance with the same data."""
        # Re-create the original data structure that __init__ expects
        data = {
            "id": self.id,
            "name": self.name,
            "cost": self.cost,
            "type": self.type,
            "value": self.value,
            "description": self.description,
            "artwork": self.artwork_filename
        }
        new_card = Card(data)
        # If the original card's artwork failed to load, mark the new one as failed too
        # to prevent it from trying (and printing an error) again.
        if self.artwork_filename in Card._failed_to_load_artwork:
            Card._failed_to_load_artwork.add(new_card.artwork_filename)
        
        new_card.load_image() # Now, load the image (or placeholder)
        return new_card

    def load_image(self):
        """Loads the card's image from the artwork filename."""
        try:
            # --- Build a reliable, absolute path to the assets folder from the project root ---
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level from 'src' to the project root directory
            project_root = os.path.join(current_dir, '..')
            base_path = os.path.join(project_root, 'assets', 'images', 'cards')
            # Construct the full path to the image
            image_path = os.path.join(base_path, self.artwork_filename)
            self.image = pygame.image.load(image_path).convert_alpha()

            # --- Render text directly onto the loaded image ---
            try:
                font_small = pygame.font.Font(None, 20)
            except pygame.error: # Fallback if default font fails
                font_small = pygame.font.SysFont("sans", 20)

            font_large = pygame.font.Font(None, 24)

            # Render card name
            name_surf = font_large.render(self.name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(self.image.get_width() // 2, 20))
            self.image.blit(name_surf, name_rect)

            # Render card cost
            cost_surf = font_large.render(str(self.cost), True, (255, 255, 0)) # Yellow cost
            cost_rect = cost_surf.get_rect(topleft=(10, 10))
            self.image.blit(cost_surf, cost_rect)

            # Render description text
            desc_area_y = self.image.get_height() * 0.6 # Start description text 60% down the card
            desc_padding = 8
            desc_max_width = self.image.get_width() - (desc_padding * 2)
            wrap_text(self.image, self.description, (desc_padding, desc_area_y), font_small, desc_max_width, color=(230, 230, 230))


        except pygame.error as e:
            # Only print the error once per filename to avoid flooding the console
            if self.artwork_filename not in Card._failed_to_load_artwork:
                print(f"Error loading image for card '{self.name}' at {image_path}: {e}")
                Card._failed_to_load_artwork.add(self.artwork_filename)

            # Optional: Create a placeholder surface if image fails to load
            self.image = pygame.Surface((100, 150), pygame.SRCALPHA)
            self.image.fill((50, 50, 50)) # Dark grey background
            pygame.draw.rect(self.image, (100, 100, 100), self.image.get_rect(), 3) # Border

            # --- Render placeholder text ---
            font_small = pygame.font.Font(None, 20)
            font_large = pygame.font.Font(None, 24)

            # Render card name
            name_surf = font_large.render(self.name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(self.image.get_width() // 2, 20))
            self.image.blit(name_surf, name_rect)

            # Render card cost
            cost_surf = font_large.render(str(self.cost), True, (255, 255, 0)) # Yellow cost
            cost_rect = cost_surf.get_rect(topleft=(10, 10))
            self.image.blit(cost_surf, cost_rect)

            # Render description text on placeholder
            desc_area_y = self.image.get_height() * 0.6
            desc_padding = 8
            desc_max_width = self.image.get_width() - (desc_padding * 2)
            wrap_text(self.image, self.description, (desc_padding, desc_area_y), font_small, desc_max_width, color=(230, 230, 230))

    def draw(self, surface: pygame.Surface, is_hovered: bool = False):
        """Draws the card on the given surface."""
        if not self.image or not self.rect:
            return
        # Draw the card image itself first
        surface.blit(self.image, self.rect)

        # Draw a highlight rectangle if hovered
        if is_hovered:
            highlight_rect = self.rect.inflate(6, 6) # Make it slightly larger than the card
            pygame.draw.rect(
                surface,
                (255, 255, 0), # Yellow highlight
                highlight_rect,
                border_radius=12
            )

    def draw_tooltip(self, surface: pygame.Surface):
        """Draws the card's description tooltip, meant to be called for the hovered card."""
        if not self.rect:
            return
        # --- Draw description tooltip on hover ---
        # Create a semi-transparent background for the text
        tooltip_width = 200
        tooltip_height = 100
        tooltip_surf = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        tooltip_surf.fill((20, 20, 30, 220)) # Dark, semi-transparent background
        pygame.draw.rect(tooltip_surf, (150, 150, 150), tooltip_surf.get_rect(), 1, border_radius=5)

        # Render the description text (you might need a text wrapping function for longer descriptions)
        font = pygame.font.Font(None, 22)
        desc_surf = font.render(self.description, True, (230, 230, 230))
        desc_rect = desc_surf.get_rect(center=(tooltip_width // 2, tooltip_height // 2))
        tooltip_surf.blit(desc_surf, desc_rect)

        # Position the tooltip above the card
        tooltip_pos = (self.rect.centerx - tooltip_width // 2, self.rect.top - tooltip_height - 5)
        surface.blit(tooltip_surf, tooltip_pos)