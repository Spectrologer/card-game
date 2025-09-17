import pygame

class UILayout:
    """
    Manages the layout of the game screen using a grid-based system.
    This class calculates and provides Rects for different UI regions.
    """

    def __init__(self, width: int, height: int):
        """
        Initializes the layout with the given screen dimensions.

        Args:
            width (int): The width of the screen.
            height (int): The height of the screen.
        """
        self.width = width
        self.height = height

        # --- Define major UI regions ---

        # Top bar for buttons like 'Close'
        self.top_bar = pygame.Rect(0, 0, width, 50)
        
        # Bottom area for player hand and stats (now bottom half of the screen)
        self.bottom_bar = pygame.Rect(0, height // 2, width, height // 2)
        
        # Main combat area in the middle
        self.combat_area = pygame.Rect(0, self.top_bar.bottom, width, self.bottom_bar.top - self.top_bar.bottom)

        # Player avatar area, positioned above the hand
        self.player_avatar_area = pygame.Rect(0, self.bottom_bar.top - 170, 200, 160)
        self.player_avatar_area.centerx = width * 0.25 # Position it 25% from the left

        # Enemy info area on the right of the combat area
        self.enemy_area = self.combat_area.copy()
        self.enemy_area.width = width // 3
        self.enemy_area.right = width
        
        self.hand_area = pygame.Rect(0, self.bottom_bar.y + 100, width, self.bottom_bar.height - 100)
        self.player_stats_area = pygame.Rect(20, self.bottom_bar.top + 10, 300, 100)

        # A specific zone within the hand_area where cards are actually placed. 1/2 of screen width.
        self.card_zone_width = width / 2
        self.card_zone = pygame.Rect((width - self.card_zone_width) / 2, self.hand_area.y, self.card_zone_width, self.hand_area.height)

        self.deck_info_area = pygame.Rect(20, self.bottom_bar.top + 110, 300, 100)
        self.end_turn_area = pygame.Rect(width - 170, height - 70, 150, 50)
        self.draw_pile_area = pygame.Rect(width - 180, self.hand_area.y, 100, 150)
        self.discard_pile_area = pygame.Rect(width - 300, self.hand_area.y, 100, 150)