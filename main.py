import pygame
import sys
import json
import os
import asyncio # Import asyncio for the web game loop

# Add the 'src' directory to the Python path
# This is not needed for PyScript as it uses a virtual filesystem.
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.card import Card 
from src.ui import Button, draw_text
from src.enemy import Enemy
from src.player import Player
from src.layout import UILayout
# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WINDOW_TITLE = "Deckbuilder Card Battler"

def load_cards():
    """Loads all card definitions from the JSON file."""
    try:
        # In PyScript, the path is relative to the root where files are fetched.
        json_path = 'src/data/cards.json'
        with open(json_path, "r") as f:
            all_card_data = json.load(f)
            # Create a dictionary of Card objects, keyed by their ID
            return {data["id"]: Card(data) for data in all_card_data}
    except FileNotFoundError:
        print("Error: cards.json not found!")
        return {}
    except json.JSONDecodeError:
        print("Error: Could not decode cards.json!")
        return {}

def reset_game(player: Player, all_cards: dict, width: int, height: int, combat_count: int) -> Enemy:
    """Resets the game to its initial state and returns a new Enemy instance."""
    print("--- Resetting Game ---")
    # Create a new starting deck with fresh card copies
    strike_template = all_cards.get("card_001")
    defend_template = all_cards.get("card_002")
    starting_deck = []
    if strike_template and defend_template:
        for _ in range(5): # Let's reduce the starting deck size for better testing/gameplay
            starting_deck.append(strike_template.copy())
        for _ in range(5):
            starting_deck.append(defend_template.copy())

    # player.reset_stats() is now called from main() on first run
    player.set_deck(starting_deck)
    player.start_new_combat()

    # Create and return a new enemy for the new game
    # Scale enemy HP based on combat count. 25% increase per combat.
    base_hp = 10 # The HP of the first enemy
    new_hp = int(base_hp * (1 + 0.25 * combat_count))
    new_enemy = Enemy(width // 2, height // 2 - 100, hp=new_hp)
    return new_enemy

async def main():
    """Main game function."""

    # --- PyScript/Web Specific Setup ---
    # This tells pygame to render to the div specified in the <py-script> tag's "target"
    os.environ["PYGAME_BLEND_ALPHA_SDL2"] = "1"

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # --- Game Variables ---
    combat_count = 0

    all_cards = load_cards()
    print(f"Loaded {len(all_cards)} cards!")
    # Load card images
    for card in all_cards.values():
        card.load_image() # No longer needs a path argument

    # --- Player ---
    player = Player()
    # Create a starting deck. It's crucial that each card is a unique object.
    # We'll use the loaded cards as templates.
    strike_template = all_cards.get("card_001")
    defend_template = all_cards.get("card_002")
    enemy = reset_game(player, all_cards, SCREEN_WIDTH, SCREEN_HEIGHT, combat_count)

    # --- Game State Machine ---
    # The game can only be in one of these states at a time.
    # - PLAYER_TURN: Waiting for player input (playing cards, ending turn).
    # - ENEMY_ANNOUNCE: Brief pause to show "Enemy's Turn".
    # - ENEMY_ATTACK: The enemy performs its attack animation and logic.
    # - ENEMY_END: The enemy turn ends, player's turn begins.
    # - GAME_OVER: The player has lost, showing restart/quit options.
    # - COMBAT_WIN: The player has won the combat, showing next/quit options.
    game_state = "PLAYER_TURN"

    turn_timer = 0
    game_over_reason = "" # To store why the game ended
    ENEMY_TURN_ANNOUNCE_DURATION = 1.5 # seconds

    # --- UI Layout ---
    layout = UILayout(SCREEN_WIDTH, SCREEN_HEIGHT)

    # --- Enemy ---
    # enemy is now initialized by reset_game

    # --- Dynamic UI positioning ---
    # We need a function to reposition elements when the screen resizes
    def position_ui_elements(width, height):
        close_button.rect.topright = (width - 10, 10)
        end_turn_button.rect = layout.end_turn_area

        # Position cards in hand
        num_cards = len(player.hand)
        if num_cards == 0:
            return

        card_width = 100 # Assuming card image width is 100
        card_spacing = card_width + 10 # Ideal spacing

        # Calculate total width required with ideal spacing
        total_hand_width = (num_cards - 1) * card_spacing + card_width

        # If the hand is too wide for the zone, calculate the necessary overlap
        if total_hand_width > layout.card_zone.width and num_cards > 1:
            card_spacing = (layout.card_zone.width - card_width) / (num_cards - 1)

        card_x_start = layout.card_zone.left
        card_y = layout.card_zone.y
        for i, card in enumerate(player.hand): # Use player.hand now
            card.rect = card.image.get_rect(topleft=(card_x_start + i * card_spacing, card_y))

        # Reposition enemy
        if enemy:
            enemy.rect.center = layout.enemy_area.center
            enemy.base_x = layout.enemy_area.centerx

        # Reposition player
        player.rect.center = layout.player_avatar_area.center

    # --- UI Elements ---
    close_button = Button(0, 0, 100, 40, "Close")
    end_turn_button = Button(0, 0, 150, 50, "End Turn")
    restart_button = Button(0, 0, 200, 60, "Restart")
    position_ui_elements(layout.width, layout.height) # Set initial position

    running = True
    while running:
        for event in pygame.event.get(): # Regular event loop
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                layout = UILayout(event.w, event.h) # Re-create layout with new dimensions
                position_ui_elements(event.w, event.h) # Reposition all elements

            # --- Event Handling based on Game State ---
            if game_state == "PLAYER_TURN":
                if close_button.is_clicked(event):
                    running = False
                if end_turn_button.is_clicked(event):
                    game_state = "ENEMY_ANNOUNCE"
                
                # Check for card clicks (iterate backwards to safely remove items)
                for card in reversed(player.hand):
                    if card.rect and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if card.rect.collidepoint(event.pos):
                            # Check if there is an enemy to target
                            if not enemy:
                                print("No enemy to target!")
                                continue
                            player.play_card(card, enemy) # This can fail if not enough energy
                            position_ui_elements(screen.get_width(), screen.get_height()) # Reposition hand
                            # --- Immediate check for enemy defeat after a card is played ---
                            if enemy.hp <= 0:
                                game_state = "COMBAT_WIN"
                            break # Stop after playing one card to avoid multiple plays on one click
            elif game_state == "GAME_OVER":
                if restart_button.is_clicked(event):
                    combat_count = 0 # Reset combat count on game over
                    player.reset_stats() # Fully reset player HP for a new run
                    enemy = reset_game(player, all_cards, screen.get_width(), screen.get_height(), combat_count) # This resets player.hp
                    restart_button.rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 50)
                    position_ui_elements(screen.get_width(), screen.get_height())
                    game_state = "PLAYER_TURN"
                    game_over_reason = "" # Clear the reason so the overlay doesn't re-appear immediately
                if close_button.is_clicked(event):
                    running = False
            elif game_state == "COMBAT_WIN":
                if restart_button.is_clicked(event): # We'll reuse the restart button for "Next Combat"
                    combat_count += 1
                    # Player stats like HP carry over to the next combat
                    enemy = reset_game(player, all_cards, screen.get_width(), screen.get_height(), combat_count)
                    position_ui_elements(screen.get_width(), screen.get_height())
                    game_state = "PLAYER_TURN"
                if close_button.is_clicked(event):
                    running = False

        # --- Game Logic / Updates based on Game State --- (Use elif to prevent state re-evaluation in the same frame)
        if game_state == "PLAYER_TURN":
            player.update()
            if enemy:
                enemy.update() # Update for idle animations
                if enemy.hp <= 0:
                    game_state = "COMBAT_WIN"
            
            # --- Check for state transitions ---
            if player.hp <= 0:
                game_over_reason = "You have been defeated!"
                game_state = "GAME_OVER"
            # Auto-end turn if player has no energy for any cards
            elif (player.energy <= 0 and any(card.cost > 0 for card in player.hand)) or not player.hand:
                game_state = "ENEMY_ANNOUNCE"

        elif game_state == "ENEMY_ANNOUNCE":
            turn_timer += clock.get_time() / 1000 # Add elapsed time in seconds
            if turn_timer >= ENEMY_TURN_ANNOUNCE_DURATION:
                turn_timer = 0
                game_state = "ENEMY_ATTACK"
                if enemy:
                    enemy.start_attack_animation(player.rect)

        elif game_state == "ENEMY_ATTACK":
            if enemy:
                attack_landed = enemy.update()
                if attack_landed:
                    enemy.perform_attack(player)
                    game_state = "ENEMY_END"
            else: # Enemy was defeated before it could attack
                game_state = "ENEMY_END"

        elif game_state == "ENEMY_END":
            # Wait for enemy return animation to finish
            if enemy:
                enemy.update()
            
            if not enemy or enemy.animation_state == "idle":
                player.end_turn() # Reset player energy and draw count
                # --- Auto-draw a card at the start of the turn ---
                if not player.draw_card():
                    game_over_reason = "Draw pile is empty!"
                    game_state = "GAME_OVER"
                else:
                    position_ui_elements(screen.get_width(), screen.get_height())
                game_state = "PLAYER_TURN"

        elif game_state == "GAME_OVER":
            restart_button.rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 50)
        
        elif game_state == "COMBAT_WIN":
            restart_button.rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 50)

        # --- Drawing ---
        screen.fill((20, 20, 30)) # Fill screen with a dark blue color

        # --- Drawing based on Game State ---
        if game_state not in ["GAME_OVER", "COMBAT_WIN"]:
            # --- Draw Combat Number ---
            combat_text = f"Combat {combat_count + 1}"
            draw_text(screen, combat_text, screen.get_width() // 2 - 50, 15, font_size=32, color=(220, 220, 220))

            # --- Draw normal game UI ---
            player.draw(screen)
            if enemy:
                enemy.draw(screen)
                stats_text = f"HP: {enemy.hp} | Armor: {enemy.armor} | Attack: {enemy.attack_damage}"
                stats_rect = pygame.Rect(0, 0, 300, 30)
                stats_rect.midtop = enemy.rect.midbottom
                draw_text(screen, stats_text, stats_rect.x, stats_rect.y, font_size=28, color=(220, 220, 220))
            
            # --- Deck Composition Display ---
            # This should reflect all cards currently in play for the combat (draw + discard + hand)
            deck_composition = {}
            # Let's count from the master deck list for consistency
            for card in player.deck:
                deck_composition[card.name] = deck_composition.get(card.name, 0) + 1
            
            # Draw from the bottom up for scalability
            deck_info_pos = layout.draw_pile_area.topleft
            line_height = 22
            # Start drawing just above the draw pile area and move upwards
            start_y = layout.draw_pile_area.top - line_height
            for i, (name, count) in enumerate(deck_composition.items()):
                text = f"{name}: {count}"
                draw_text(screen, text, deck_info_pos[0], start_y - (i * line_height), font_size=24, color=(200, 200, 200))

            # Discard Pile Info
            # This is now drawn as part of the pile itself

            # Draw/Discard Pile visuals
            pygame.draw.rect(screen, (50, 50, 80), layout.draw_pile_area, border_radius=10)
            draw_text(screen, "Deck", layout.draw_pile_area.centerx - 25, layout.draw_pile_area.centery - 30)
            draw_text(screen, str(len(player.draw_pile)), layout.draw_pile_area.centerx - 10, layout.draw_pile_area.centery, font_size=36)
            
            # Player Stats
            stats_pos = layout.player_stats_area.topleft
            player_hp_text = f"HP: {player.hp} / {player.max_hp}"
            player_armor_text = f"Armor: {player.armor}"
            player_energy_text = f"Energy: {player.energy} / {player.max_energy}"
            draw_text(screen, player_hp_text, stats_pos[0], stats_pos[1], font_size=32, color=(200, 220, 200))
            draw_text(screen, player_armor_text, stats_pos[0], stats_pos[1] + 30, font_size=32, color=(180, 180, 255))
            draw_text(screen, player_energy_text, stats_pos[0], stats_pos[1] + 60, font_size=32, color=(200, 200, 255))
            
            pygame.draw.rect(screen, (80, 50, 50), layout.discard_pile_area, border_radius=10)
            draw_text(screen, "Discard", layout.discard_pile_area.centerx - 40, layout.discard_pile_area.centery - 15)
            draw_text(screen, str(len(player.discard_pile)), layout.discard_pile_area.centerx - 10, layout.discard_pile_area.centery + 5, font_size=36)

            # Draw cards in hand
            hovered_card = None
            for card in player.hand:
                if card.rect.collidepoint(pygame.mouse.get_pos()):
                    hovered_card = card
            
            for card in player.hand:
                is_hovered = (card == hovered_card)
                card.draw(screen, is_hovered)

            # Only show the end turn button during the player's turn
            if game_state == "PLAYER_TURN":
                end_turn_button.draw(screen)
            elif game_state == "ENEMY_ANNOUNCE":
                draw_text(screen, "Enemy's Turn", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, font_size=72, color=(200, 50, 50))

            if hovered_card:
                hovered_card.draw_tooltip(screen)

        elif game_state == "GAME_OVER":
            # Draw elements common to both playing and game over (the background scene)
            player.draw(screen)

            # Draw the game over overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Black, semi-transparent
            screen.blit(overlay, (0, 0))

            # Draw "Game Over" text
            draw_text(screen, "Game Over", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, font_size=72, color=(200, 50, 50))
            draw_text(screen, game_over_reason, SCREEN_WIDTH // 2 - (len(game_over_reason) * 9), SCREEN_HEIGHT // 2 - 30, font_size=36, color=(220, 220, 220))

            # Draw the restart button
            restart_button.draw(screen)

        elif game_state == "COMBAT_WIN":
            # Draw the background scene

            # Draw the victory overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Black, semi-transparent
            screen.blit(overlay, (0, 0))

            # Draw "You Win!" text
            draw_text(screen, "You Win!", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 100, font_size=72, color=(255, 215, 0))

            # Draw the "Next Combat" button (reusing the restart button)
            restart_button.text = "Next Combat"
            restart_button.draw(screen)

        # The close button should be visible in all states
        close_button.draw(screen)

        pygame.display.flip() # Update the full display Surface to the screen
        clock.tick(60) # Limit frame rate to 60 FPS
        await asyncio.sleep(0) # Yield control to the browser

    pygame.quit()
    # sys.exit() is not needed in the browser and can cause issues.

if __name__ == "__main__":
    # PyScript runs the top-level code. We use asyncio.run to start our async main function.
    # This makes the game loop compatible with the browser's event model.
    asyncio.run(main())
