from __future__ import annotations
import pygame
import math
from typing import TYPE_CHECKING

# This block is only processed by type checkers, not at runtime
if TYPE_CHECKING:
    from player import Player


class Enemy:
    """Represents an enemy in the game."""

    def __init__(self, x: int, y: int, hp: int = 10):
        """
        Initializes the enemy.

        Args:
            x (int): The initial center x-coordinate.
            y (int): The initial center y-coordinate.
            hp (int): The starting health of the enemy.
        """
        # --- Attributes ---
        self.max_hp = hp
        self.hp = hp
        self.armor = 0
        self.magic_defense = 0
        self.attack_damage = 10 # The damage this enemy will deal

        # --- Animation ---
        self.image = self._create_placeholder_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.base_x = x  # The central x position around which the enemy sways
        self.sway_angle = 0.0
        self.sway_speed = 0.02  # How fast the enemy sways
        self.sway_amplitude = 40  # How far the enemy sways from the center
        
        self.animation_state = "idle" # Can be "idle", "attacking", "returning"
        self.attack_target_pos = None
        self.attack_speed = 25 # Pixels per frame during attack

    def _create_placeholder_image(self) -> pygame.Surface:
        """Creates a placeholder image for the enemy."""
        size = (150, 180)
        image = pygame.Surface(size, pygame.SRCALPHA)
        
        # Main body
        body_rect = pygame.Rect(0, 0, size[0], size[1] - 30)
        pygame.draw.ellipse(image, (180, 50, 50), body_rect)
        
        # Eyes
        eye_y = 70
        eye_radius = 12
        pygame.draw.circle(image, (255, 255, 255), (size[0] // 2 - 30, eye_y), eye_radius)
        pygame.draw.circle(image, (255, 255, 255), (size[0] // 2 + 30, eye_y), eye_radius)
        pygame.draw.circle(image, (0, 0, 0), (size[0] // 2 - 30, eye_y), eye_radius - 5)
        pygame.draw.circle(image, (0, 0, 0), (size[0] // 2 + 30, eye_y), eye_radius - 5)

        return image

    def update(self) -> bool:
        """
        Updates the enemy's state, including its animation.
        Returns True if the attack animation hits its target, False otherwise.
        """
        attack_hit = False
        if self.animation_state == "idle":
            self.sway_angle += self.sway_speed
            # Use math.sin to create a smooth back-and-forth motion
            offset_x = math.sin(self.sway_angle) * self.sway_amplitude
            self.rect.centerx = self.base_x + int(offset_x)
        
        elif self.animation_state == "attacking":
            # Move towards the target position
            if self.rect.centerx > self.attack_target_pos[0]:
                self.rect.centerx -= self.attack_speed
            else: # Reached target, switch to returning
                self.animation_state = "returning"
                attack_hit = True

        elif self.animation_state == "returning":
            # Move back to base position
            if self.rect.centerx < self.base_x:
                self.rect.centerx += self.attack_speed
            else: # Returned to base, switch to idle
                self.rect.centerx = self.base_x
                self.animation_state = "idle"
        return attack_hit

    def draw(self, surface: pygame.Surface):
        """Draws the enemy on the given surface."""
        surface.blit(self.image, self.rect)

    def perform_attack(self, target: Player):
        """
        Performs an attack on a target (the player).
        Damage is applied to armor first, then HP.
        """
        damage_to_deal = self.attack_damage
        target.take_damage(damage_to_deal)
        print(f"Enemy attacks for {damage_to_deal}. Player HP: {target.hp}, Armor: {target.armor}")

        # In the future, this could return information about the attack
        # for visual effects or other logic.

    def start_attack_animation(self, target_rect: pygame.Rect):
        """Begins the visual attack sequence."""
        if self.animation_state == "idle":
            self.attack_target_pos = target_rect.midright # Target the right side of the player avatar
            self.animation_state = "attacking"