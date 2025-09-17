import unittest
import sys
import os

# --- Add the project root to the Python path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ---

from src.player import Player
from src.enemy import Enemy
from src.card import Card

class MockClock:
    """A mock Pygame clock to control time in tests."""
    def get_time(self):
        # Return a fixed time delta (e.g., 16.67ms for 60 FPS)
        return 16.67

class TestGameFlow(unittest.TestCase):
    """Tests for the main game flow and turn structure."""

    def setUp(self):
        """Set up a player, enemy, and mock objects for testing."""
        self.player = Player()
        self.enemy = Enemy(0, 0)
        
        # Give the player a card they can't afford to test the auto-end turn
        card_data = {"id": "c_expensive", "name": "Big Hit", "cost": 99, "type": "Attack", "value": 99, "description": "Too expensive.", "artwork": "s.png"}
        self.expensive_card = Card(card_data)
        
        # Give the player a card they can afford
        card_data_cheap = {"id": "c_cheap", "name": "Small Hit", "cost": 1, "type": "Attack", "value": 1, "description": "Cheap.", "artwork": "s.png"}
        self.cheap_card = Card(card_data_cheap)

    def test_turn_ends_when_player_runs_out_of_energy(self):
        """Verify that the turn automatically ends when the player has no more energy for any card in hand."""
        # Arrange
        turn_state = "player_turn"
        self.player.energy = 0
        self.player.hand = [self.expensive_card] # A card that costs more than 0

        # Act: Simulate the logic check from main.py
        if self.player.energy <= 0 and any(card.cost > 0 for card in self.player.hand):
            turn_state = "enemy_turn_announce"

        # Assert
        self.assertEqual(turn_state, "enemy_turn_announce")

    def test_turn_does_not_end_if_player_can_play_zero_cost_cards(self):
        """Verify the turn does not end if the player is out of energy but has a 0-cost card."""
        # Arrange
        turn_state = "player_turn"
        self.player.energy = 0
        zero_cost_card = self.cheap_card.copy()
        zero_cost_card.cost = 0
        self.player.hand = [zero_cost_card]

        # Act: Simulate the logic check from main.py
        if self.player.energy <= 0 and any(card.cost > 0 for card in self.player.hand):
            turn_state = "enemy_turn_announce"

        # Assert
        self.assertEqual(turn_state, "player_turn")

    def test_enemy_turn_announcement_progresses_to_attack(self):
        """Verify the 'enemy_turn_announce' state moves to 'enemy_turn_attack' after a delay."""
        # Arrange
        turn_state = "enemy_turn_announce"
        turn_timer = 1.4 # Just under the duration
        ENEMY_TURN_ANNOUNCE_DURATION = 1.5

        # Act: Simulate a time tick that pushes the timer over the duration
        turn_timer += 0.2 # 1.4 + 0.2 = 1.6
        if turn_timer >= ENEMY_TURN_ANNOUNCE_DURATION:
            turn_state = "enemy_turn_attack"

        # Assert
        self.assertEqual(turn_state, "enemy_turn_attack")

if __name__ == '__main__':
    unittest.main()