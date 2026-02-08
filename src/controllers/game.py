import time
import random
from src.interface.interaction import interactive_selection
from src.interface.draw import draw_venue, draw_leaderboard
from src.engine.constants import VENUE_LENGTH
from src.engine.race_logic import GameLogic

class GameController:
    def __init__(self, chosen_colors):
        self.boats = GameLogic.create_boat(chosen_colors)
        self.game_running = True

    def apply_bonuses(self):
        sorted_boats = sorted(self.boats, key=lambda x: (x.position, x.stroke_rate), reverse=True)
        if len(sorted_boats) >= 2:
            GameLogic.change_tides_bonus(sorted_boats[-1])
            GameLogic.change_tides_bonus(sorted_boats[-2])
            
            title_msg = f"Change of Tides applies to {sorted_boats[-1].name} and {sorted_boats[-2].name}"
            choice_idx = interactive_selection(["Continue"], "vertical", title_msg)

            for i in range(1, len(sorted_boats)):
                current_boat = sorted_boats[i]
                boat_ahead = sorted_boats[i-1]

                can_use = GameLogic.can_use_motivation(current_boat, boat_ahead)
                if not current_boat.is_npc:
                    if can_use:
                        options = ["Activate Motivation (+2 Spaces, Cost 1 Stamina)", "Hold Position"]
                        title_msg = f"MOTIVATION: {current_boat.name} is drafting {boat_ahead.name}! Activate bonus {current_boat.name}?"
                        choice_idx = interactive_selection(options, "vertical", title_msg, current_boat.color)

                        if choice_idx == 0:
                            GameLogic.pay_exhaustion_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

                else:
                    if can_use:
                        GameLogic.pay_exhaustion_cards(current_boat, 1)
                        GameLogic.motivation_bonus(current_boat)

                        title_msg = f"{current_boat.name} (NPC) uses Motivation!"
                        choice_idx = interactive_selection(["Continue"], "vertical", title_msg, current_boat.color)

    def check_finish_line(self):
        for b in self.boats:
            if b.position >= VENUE_LENGTH:
                b.finished = True
        
        if all(b.finished for b in self.boats):
            draw_leaderboard(sorted(self.boats, key=lambda x: x.position, reverse=True))
            self.game_running = False
    
    def run_game(self):
        draw_venue(self.boats)
        time.sleep(5)

        while self.game_running:
            # ------ INDIVIDUAL PHASE ------
            for b in self.boats:
                if b.finished:
                    continue

                # Show next player
                title_msg = f"{b.name}'s Turn (Pos: {b.position * 20}m | Rate: {b.stroke_rate})"
                interactive_selection(["Continue"], "vertical", title_msg, b.color)

                GameLogic.draw_cards(b)

                # Show stats
                if not b.is_npc:
                    title_msg = f"{b.name}'s (Pos: {b.position * 20}m | Rate: {b.stroke_rate} | Hand: {b.hand} | Stamina: {len(b.stamina_pile)})"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)

                if GameLogic.check_clustered_hand(b):
                    title_msg = f"CLUTTERED HAND! Turn skipped for {b.name}."
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
                    if random.random() > 0.5:
                        rate_choice = "up"
                    if random.random() > 0.8 and len(b.stamina_pile) > 3:
                        jump_choice = True

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
                    title_msg = f"{b.name} moves {movement} spaces. New Position: {b.position}"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                elif status == "Penalized":
                    title_msg = f"CRAB CAUGHT! {b.name} pushed too hard and lost momentum."
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                else:
                    title_msg = f"CRAB CAUGHT! {b.name} pushed too hard and become exhausted."
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
            
            # ------ END OF ROUND BONUSES ------
            self.apply_bonuses()
            self.check_finish_line()
            draw_venue(self.boats)
            time.sleep(3)