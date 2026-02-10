import time
import random
from src.interface.interaction import interactive_selection
from src.interface.draw import draw_venue, draw_leaderboard
from src.engine.constants import VENUE_LENGTH, SPLITS
from src.engine.race_logic import GameLogic

class GameController:
    """Manages the main game flow and turn mechanics."""
    def __init__(self, chosen_colors):
        """
        """
        self.boats = GameLogic.create_boat(chosen_colors)
        self.game_running = True

    def apply_bonuses(self):
        """
        """
        sorted_boats = sorted(self.boats, key=lambda x: (x.position, x.stroke_rate), reverse=True)
        if len(sorted_boats) >= 2:
            GameLogic.change_tides_bonus(sorted_boats[-1])
            GameLogic.change_tides_bonus(sorted_boats[-2])
            
            title_msg = f"CHANGES OF TIDES: Applied to {sorted_boats[-1].name} and {sorted_boats[-2].name}"
            choice_idx = interactive_selection(["Continue"], "vertical", title_msg)

            for i in range(1, len(sorted_boats)):
                current_boat = sorted_boats[i]
                boat_ahead = sorted_boats[i-1]

                can_use = GameLogic.can_use_motivation(current_boat, boat_ahead)
                if not current_boat.is_npc:
                    if can_use:
                        options = ["Activate Motivation (+2 Spaces, Cost 1 Stamina)", "Hold Position"]
                        title_msg = f"MOTIVATION: {current_boat.name} is passing {boat_ahead.name}! Activate bonus {current_boat.name}?"
                        choice_idx = interactive_selection(options, "vertical", title_msg, current_boat.color)

                        if choice_idx == 0:
                            GameLogic.pay_exhaustion_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

                else:
                    if can_use:
                        GameLogic.pay_exhaustion_cards(current_boat, 1)
                        GameLogic.motivation_bonus(current_boat)

                        title_msg = f"MOTIVATION: {current_boat.name} passes {boat_ahead.name}!"
                        choice_idx = interactive_selection(["Continue"], "vertical", title_msg, current_boat.color)

    def check_finish_line(self):
        """
        """
        for b in self.boats:
            if b.position >= VENUE_LENGTH:
                b.finished = True
        
        if all(b.finished for b in self.boats):
            draw_leaderboard(sorted(self.boats, key=lambda x: (x.turn, x.position, x.stroke_rate)), "RACE FINISHED!")
            self.game_running = False
            time.sleep(3)
    
    def run_game(self):
        """
        """
        draw_venue(self.boats)
        time.sleep(5)

        while self.game_running:
            # ------ INDIVIDUAL PHASE ------
            for b in self.boats:
                if b.finished:
                    continue

                b.turn += 1

                # Show next player
                title_msg = f"{b.name}'s Turn (Pos: {b.position * 20}m | Rate: {b.stroke_rate})"
                interactive_selection(["Continue"], "vertical", title_msg, b.color)

                GameLogic.draw_cards(b)

                # Show stats
                if not b.is_npc:
                    title_msg = f"{b.name}'s (Pos: {b.position * 20}m | Rate: {b.stroke_rate} | Hand: {b.hand} | Stamina: {len(b.stamina_pile)})"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)

                if GameLogic.check_clustered_hand(b):
                    title_msg = f"CLUSTERED HAND! Turn skipped for {b.name}."
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                    GameLogic.replenish_hand(b)
                    continue

                # Stroke rate change
                rate_choice = "maintain"
                jump_choice = False

                # Detect if it's a player
                if not b.is_npc:
                    options = ["maintain", "up", "down"]
                    title_msg = f"Current Rate: {b.stroke_rate}. Change?"
                    choice_idx = interactive_selection(options, "vertical", title_msg, b.color)
                    rate_choice = options[choice_idx]

                    if rate_choice != "maintain" and len(b.stamina_pile) > 0:
                        options = ["Normal Shift", "Boost (Cost 1 Stamina)"]
                        choice_idx = interactive_selection(options, "vertical", "Do you want to boost?", b.color)
                        jump_choice = (choice_idx == 1)
                else:
                    potential_cards = sorted([c for c in b.hand if isinstance(c, int) or c == 's'], 
                                            key=lambda x: (x if isinstance(x, int) else 1.5), reverse=True)
                    est_cards_needed = b.stroke_rate + 1
                    est_speed = sum([(c if isinstance(c, int) else 1.5) for c in potential_cards[:est_cards_needed]])
                    next_pos = b.position + est_speed

                    upcoming_limit = None
                    for split_loc, split_limit in SPLITS.items():
                        if b.position < split_loc <= next_pos:
                            upcoming_limit = split_limit

                    if upcoming_limit:
                        if est_speed > upcoming_limit:
                            rate_choice = "down"
                        elif est_speed < upcoming_limit - 3:
                            rate_choice = "up"
                            jump_choice = True
                        elif est_speed < split_limit - 1:
                            rate_choice = "up"
                    else:
                        if len(b.stamina_pile) > 3:
                            rate_choice = "up"
                            jump_choice = True
                        elif len(b.stamina_pile) < 2:
                            rate_choice = "down"
                        else:
                            rate_choice = "up"

                GameLogic.change_stroke_rate(b, rate_choice, jump_choice)

                # Play cards
                cards_selected = []
                available_cards, cards_needed = GameLogic.get_playable_cards(b)

                if not b.is_npc:
                    while len(cards_selected) < cards_needed:
                        for _ in range(cards_needed):
                            title_msg = f"Select Card {len(cards_selected) + 1}/{cards_needed}:"
                            choice_idx = interactive_selection(available_cards, "horizontal", title_msg, b.color)
                            card_value = available_cards.pop(choice_idx)
                            cards_selected.append(card_value)
                else:
                    available_cards.sort(key=lambda x: (x if isinstance(x, int) else 1.5), reverse=True)
                    cards_selected = available_cards[:cards_needed]

                # Movement
                movement= GameLogic.calculate_movement(b, cards_selected)
                status = GameLogic.check_split_limit(b, movement)

                if status == "Passed":
                        GameLogic.apply_movement(b, movement)

                # Optional cards discard
                cards_selected = []
                available_cards, _ = GameLogic.get_playable_cards(b)

                if not b.is_npc:
                    options = ["Discard", "No discard"]
                    choice_idx = interactive_selection(options, "vertical", "Discard any cards?", b.color) 
                    
                    if options[choice_idx] == "Discard":
                        while True:
                            if not available_cards:
                                break

                            options = available_cards + ["Done"]
                            choice_idx = interactive_selection(options, "horizontal", "Select cards to discard:", b.color)
                            selection = options.pop(choice_idx)
                            if selection == "Done":
                                break
                            
                            card_value = available_cards.pop(choice_idx)
                            cards_selected.append(card_value)

                if cards_selected:
                    GameLogic.discard_cards(b, cards_selected)
                
                # Replenish hand
                GameLogic.replenish_hand(b)

                # Display results
                if status == "Passed":
                    title_msg = f"{b.name} moves {movement} spaces. New Position: {b.position * 20}m"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                elif status == "Penalized":
                    title_msg = f"CRAB CAUGHT! {b.name} pushed too hard and lost momentum. New Position: {b.position * 20}m"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                else:
                    title_msg = f"CRAB CAUGHT! {b.name} pushed too hard and become exhausted. New Position: {b.position * 20}m"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
            
            # ------ END OF ROUND BONUSES ------
            self.apply_bonuses()
            self.check_finish_line()
            draw_venue(self.boats)
            draw_leaderboard(sorted(self.boats, key=lambda x: (x.position, x.stroke_rate), reverse=True), "Leaderboard")
            time.sleep(5)