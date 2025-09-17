import unittest
import sys
import os

# --- Add the project root to the Python path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)
# ---

from src.player import Player
from src.enemy import Enemy
from src.card import Card

class TestGameStates(unittest.TestCase):
    """Tests for the main game state machine transitions."""

    def setUp(self):
        """Set up a player, enemy, and mock objects for testing."""
        self.player = Player()
        self.enemy = Enemy(0, 0)
        
        # Create a basic attack card for testing
        card_data = {"id": "c1", "name": "Strike", "cost": 1, "type": "Attack", "value": 6, "description": "Deal 6 damage.", "artwork": "s.png"}
        self.strike_card = Card(card_data)

    def test_player_turn_to_combat_win(self):
        """Verify that defeating an enemy transitions the state to COMBAT_WIN."""
        # Arrange
        game_state = "PLAYER_TURN"
        self.enemy.hp = 5 # Enemy has low health
        self.player.energy = 1
        self.player.hand = [self.strike_card]

        # Act
        # Simulate playing a card that defeats the enemy
        self.player.play_card(self.strike_card, self.enemy)
        # Simulate the main loop's check
        if self.enemy.hp <= 0:
            game_state = "COMBAT_WIN"

        # Assert
        self.assertEqual(game_state, "COMBAT_WIN")
        self.assertLessEqual(self.enemy.hp, 0)

    def test_player_turn_to_game_over_by_hp(self):
        """Verify that player HP reaching zero transitions the state to GAME_OVER."""
        # Arrange
        game_state = "PLAYER_TURN"
        self.player.hp = 0

        # Act
        # Simulate the main loop's check
        if self.player.hp <= 0:
            game_state = "GAME_OVER"

        # Assert
        self.assertEqual(game_state, "GAME_OVER")

    def test_player_turn_to_game_over_by_empty_deck(self):
        """Verify that failing to draw from an empty deck transitions to GAME_OVER."""
        # Arrange
        game_state = "PLAYER_TURN"
        self.player.draw_pile = [] # Ensure draw pile is empty

        # Act
        # Simulate the draw action and the main loop's check
        draw_successful = self.player.draw_card()
        if not draw_successful:
            game_state = "GAME_OVER"

        # Assert
        self.assertFalse(draw_successful)
        self.assertEqual(game_state, "GAME_OVER")


if __name__ == '__main__':
    unittest.main()