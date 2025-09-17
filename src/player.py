from __future__ import annotations
import pygame
import random
from typing import TYPE_CHECKING

# This block is only processed by type checkers, not at runtime
if TYPE_CHECKING:
    from card import Card
    from enemy import Enemy

class Player:
    """Represents the player in the game."""

    def __init__(self):
        """Initializes the player with starting attributes."""
        self.max_hp = 20
        self.hp = 20
        self.max_energy = 3
        self.energy = 3
        self.armor = 0
        self.cards_drawn_this_turn = 0
        
        # --- Card Management ---
        self.deck: list[Card] = []
        self.hand: list[Card] = []
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []

        # --- Visuals ---
        self.image = self._create_placeholder_image()
        self.rect = self.image.get_rect() # Position will be set in main.py

    def reset_stats(self):
        """Resets the player's core stats like HP and energy to their maximums."""
        self.hp = self.max_hp
        self.energy = self.max_energy
        self.armor = 0

    def set_deck(self, cards: list[Card]):
        """Sets the player's master deck for the run."""
        self.deck = cards

    def start_new_combat(self):
        """Resets piles and draws an initial hand for combat."""
        self.draw_pile = self.deck.copy()
        random.shuffle(self.draw_pile)
        self.hand = []
        self.discard_pile = []
        self.armor = 0 # Reset armor at the start of combat
        self.cards_drawn_this_turn = 0 # Reset draw count for new combat
        # Example: Draw 5 cards to start
        for _ in range(5):
            self._draw_card_no_count()

    def _draw_card_no_count(self) -> bool:
        """Internal method to draw a card without incrementing the turn's draw counter. Used for setup."""
        if not self.draw_pile:
            return False
        self.hand.append(self.draw_pile.pop())
        return True

    def draw_card(self) -> bool:
        """Draws a card from the draw pile into the hand, counting it against the turn limit. Returns True if successful, False otherwise."""
        if not self.draw_pile:
            print("Draw pile is empty!")
            return False

        self.hand.append(self.draw_pile.pop())
        self.cards_drawn_this_turn += 1
        return True

    def play_card(self, card: Card, target: Enemy):
        """
        Plays a card from the hand, applying its effect and moving it to the discard pile.
        """
        if self.energy < card.cost:
            print(f"Not enough energy to play {card.name}. Requires {card.cost}, has {self.energy}.")
            return # Not enough energy

        self.energy -= card.cost

        # Apply card effect based on its type
        if card.type == "Attack":
            # For now, we assume attacks always target the passed 'target'
            target.hp -= card.value
            print(f"Played {card.name}, dealing {card.value} damage to {type(target).__name__}. Enemy HP: {target.hp}")
        elif card.type == "Skill":
            if card.name == "Defend": # This could be more generic later
                self.armor += card.value
                print(f"Played {card.name}, gaining {card.value} armor. Player armor: {self.armor}")

        # Move the card from hand to discard pile
        self.hand.remove(card)
        self.discard_pile.append(card)

    def end_turn(self):
        """Handles end-of-turn logic for the player."""
        print("Player ends turn. Resetting energy.")
        self.energy = self.max_energy
        self.cards_drawn_this_turn = 0 # Reset draw count for the new turn
        # We will add discarding the hand here in a future step.

    def take_damage(self, amount: int):
        """
        Reduces the player's armor and then HP by the given amount.
        """
        # Armor absorbs damage first
        damage_to_armor = min(self.armor, amount)
        self.armor -= damage_to_armor
        
        remaining_damage = amount - damage_to_armor
        
        # Remaining damage is dealt to HP
        self.hp -= remaining_damage


    def _create_placeholder_image(self) -> pygame.Surface:
        """Creates a placeholder image for the player."""
        size = (120, 160)
        image = pygame.Surface(size, pygame.SRCALPHA)

        # Simple body shape (e.g., a blue-ish rectangle)
        body_rect = pygame.Rect(10, 20, size[0] - 20, size[1] - 20)
        pygame.draw.rect(image, (60, 120, 180), body_rect, border_radius=15)

        # Simple head shape (e.g., a circle)
        head_center = (size[0] // 2, 45)
        pygame.draw.circle(image, (220, 180, 160), head_center, 30) # Skin-tone circle

        return image

    def update(self):
        """
        Updates the player's state at the end of a frame.
        (Currently empty, but can be used for buffs/debuffs later)
        """
        pass

    def draw(self, surface: pygame.Surface):
        """Draws the player on the given surface."""
        if self.image and self.rect:
            surface.blit(self.image, self.rect)