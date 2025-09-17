import unittest
import sys
import os

# --- Add the project root to the Python path ---
# This allows us to import from the 'src' directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ---

from src.player import Player
from src.card import Card

class TestPlayer(unittest.TestCase):
    """Tests for the Player class."""

    def setUp(self):
        """Set up a new Player and some mock cards before each test."""
        self.player = Player()
        
        # Create mock card data. We don't need real images for this test.
        strike_data = {"id": "c1", "name": "Strike", "cost": 1, "type": "Attack", "value": 6, "description": "Deal 6 damage.", "artwork": "s.png"}
        defend_data = {"id": "c2", "name": "Defend", "cost": 1, "type": "Skill", "value": 5, "description": "Gain 5 Block.", "artwork": "d.png"}
        
        # Create unique card objects for the deck
        self.mock_deck = [Card(strike_data) for _ in range(5)] + [Card(defend_data) for _ in range(5)]
        
        self.player.set_deck(self.mock_deck)
        # Manually set up the draw pile to have a predictable state for testing
        self.player.draw_pile = self.player.deck.copy()
        self.player.hand = []
        self.player.discard_pile = []

    def test_draw_card_moves_card_to_hand(self):
        """Verify that drawing a card moves it from the draw pile to the hand."""
        initial_draw_pile_size = len(self.player.draw_pile)
        initial_hand_size = len(self.player.hand)
        
        # Get the top card of the draw pile to check against later
        top_card = self.player.draw_pile[-1]

        # Action: Draw a card
        self.player.draw_card()

        # Assert: Check the state changes
        self.assertEqual(len(self.player.draw_pile), initial_draw_pile_size - 1)
        self.assertEqual(len(self.player.hand), initial_hand_size + 1)
        self.assertIn(top_card, self.player.hand)
        self.assertNotIn(top_card, self.player.draw_pile)

if __name__ == '__main__':
    unittest.main()