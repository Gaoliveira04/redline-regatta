import time
import random
from src.interface.interaction import interactive_selection
from src.interface.draw import draw_venue, draw_leaderboard, stroke_rate_name
from src.engine.constants import VENUE_LENGTH, SPLITS, RATES
from src.engine.race_logic import GameLogic

class GameController:
    """Manages the main game flow and round mechanics."""
    def __init__(self, chosen_colors):
        """
        Create boats and start game
        """
        self.boats = GameLogic.create_boat(chosen_colors)
        self.game_running = True

    def apply_bonuses(self):
        """
        Apply change of tides and motivation bonus to respective players
        """
        sorted_boats = sorted(
            self.boats, 
            key=lambda x: (x.position, x.stroke_rate), 
            reverse=True
        )

        if len(sorted_boats) >= 2:
            # Change of Tides bonus
            affected = []
            for b in [sorted_boats[-1], sorted_boats[-2]]:
                if b.caught_crab or b.finished:
                    continue
                
                GameLogic.change_tides_bonus(b)
                affected.append(b.name)
            
            if len(affected) == 2:
                title_msg = f"CHANGES OF TIDES: Applied to {affected[0]} and {affected[1]}"
                interactive_selection(["Continue"], "vertical", title_msg) 
            elif len(affected) == 1:
                title_msg = f"CHANGES OF TIDES: Applied to {affected[0]}"
                interactive_selection(["Continue"], "vertical", title_msg)
            else:
                title_msg = "CHANGES OF TIDES: Not applied (Crabs Caughted)"
                interactive_selection(["Continue"], "vertical", title_msg)

            for i in range(1, len(sorted_boats)):
                current_boat = sorted_boats[i]
                boat_ahead = sorted_boats[i-1]
                
                if boat_ahead.finished or current_boat.finished or current_boat.caught_crab:
                    continue

                if GameLogic.can_use_motivation(current_boat, boat_ahead):
                    if not current_boat.is_npc:
                        options = ["Activate Motivation (+2 Spaces, Cost 1 Stamina)", "Hold Position"]
                        title_msg = f"MOTIVATION: {current_boat.name} is passing {boat_ahead.name}! Activate bonus {current_boat.name}?"
                        choice_idx = interactive_selection(options, "vertical", title_msg, current_boat.color)

                        if choice_idx == 0:
                            GameLogic.pay_stamina_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

                    else:
                        if len(current_boat.stamina_pile) > 0:
                            GameLogic.pay_stamina_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

                            title_msg = f"MOTIVATION: {current_boat.name} passes {boat_ahead.name}!"
                            interactive_selection(["Continue"], "vertical", title_msg, current_boat.color)

    def check_finish_line(self):
        """
        Detect if any boat has finished the race. 
        If all boats have finished the race end game.
        """
        for b in self.boats:
            if b.position >= VENUE_LENGTH:
                b.finished = True
        
        if all(b.finished for b in self.boats):
            self.game_running = False

            # Tiebreaker: Position/Pace and then Stroke Rate
            sorted_boats = sorted(
                self.boats,
                key=lambda x: (x.round, -x.position, -x.stroke_rate)
            )
            draw_leaderboard(sorted_boats, "RACE FINISHED!")
            time.sleep(5)
    
    def run_game(self):
        """
        Control and start game rounds structure:
        1. Change or maintain Stroke Rate
        2. Play cards
        3. Advance boat
        4. Replenish hand
        """
        draw_venue(self.boats)
        time.sleep(7)

        while self.game_running:
            # ------ INDIVIDUAL PHASE ------
            for b in self.boats:
                if b.finished:
                    continue

                b.caught_crab = False

                # Show next player
                title_msg = f"{b.name}'s Turn (Pos: {b.position * 20}m | Rate: {stroke_rate_name(b.stroke_rate)})"
                interactive_selection(["Continue"], "vertical", title_msg, b.color)

                GameLogic.draw_cards(b)

                # Show stats
                if not b.is_npc:
                    title_msg = f"{b.name}'s (Pos: {b.position * 20}m | Rate: {stroke_rate_name(b.stroke_rate)} | Hand: {b.hand} | Stamina: {len(b.stamina_pile)})"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)

                if GameLogic.check_clustered_hand(b):
                    title_msg = f"CLUSTERED HAND! Round skipped for {b.name}."
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                    GameLogic.replenish_hand(b)
                    continue

                # Stroke Rate Phase
                if not b.is_npc:
                    options = RATES
                    title_msg = f"Current Rate: {stroke_rate_name(b.stroke_rate)}. Select target rate."
                    choice_idx = interactive_selection(stroke_rate_name(options), "vertical", title_msg, b.color)
                    rate_choice = options[choice_idx]

                    result = GameLogic.change_stroke_rate(b, rate_choice)

                    if result == "failed":
                        title_msg = "LACK OF STAMINA: Jump failed!"
                        interactive_selection(["Continue"], "vertical", title_msg, b.color)
                else:
                    # Identify playbel cards
                    playable_cards = sorted(
                        [c for c in b.hand if c != 's'], 
                        key=lambda x: (x if isinstance(x, int) else 2),
                        reverse=True
                    )
                    # Determine best Stroke Rate for this round
                    best_rate = 0
                    rate_map = {2: 4, 1: 2, 0: 1}

                    for rate in [2,1,0]:
                        needed = rate_map[rate]

                        # Check if npc has enough playble cards for Stroke rate
                        if len(playable_cards) < needed:
                            continue
                        
                        # Calculate estimated speed for this round
                        cards_to_play = playable_cards[:needed]
                        est_speed = sum([(c if isinstance(c, int) else 2) for c in cards_to_play])

                        # Check Place Limits
                        next_pos = b.position + est_speed
                        next_limit_pace = None
                        next_limit_loc = None
                        for limit_loc, limit_pace in SPLITS.items():
                            if b.position < limit_loc <= next_pos:
                                next_limit_loc = limit_loc
                                next_limit_pace = limit_pace
                                break
                            
                        # If no split to be crossed or estimated speed inferior or equal to pace limit,
                        # pick best Stroke Rate and stop checking
                        if next_limit_pace is None or est_speed <= next_limit_pace:
                            best_rate = rate
                            break

                        #  Use random decision to decide if NPC exceeds pace limit
                        aggressive_prob = (next_limit_loc / 100) * 0.60
                        if random.random() < aggressive_prob:
                            exhaustion_cost = max(1, int(est_speed - next_limit_pace))

                            # See if stamina is sufficient
                            if len(b.stamina_pile) >= exhaustion_cost:
                                best_rate = rate
                                break
                            else:
                                gamble_prob = (next_limit_loc / 100) * 0.40
                                if random.random() < gamble_prob:
                                    best_rate = rate
                                    break


                    # If hand full with Stamina Cards, reduce Stroke Rate to 35 spm
                    if b.hand.count("s") >= 2:
                        best_rate = 0

                    GameLogic.change_stroke_rate(b, best_rate)

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
                    available_cards.sort(
                        key=lambda x: (x if isinstance(x, int) else 1.5),
                        reverse=True
                    )
                    cards_selected = available_cards[:cards_needed]

                # Movement and Split Limtis
                movement= GameLogic.calculate_movement(b, cards_selected)
                status = GameLogic.check_split_limit(b, movement, SPLITS)

                if status in ["Passed", "Tired"]:
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

                b.round += 1

                # Display results
                if status == "Passed":
                    title_msg = f"{b.name} moves {movement} spaces. New Position: {b.position * 20}m"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                elif status == "Tired":
                    title_msg = f"PUSHING TOO HARD! {b.name} overexerts himself and becomes exhausted. New Position: {b.position * 20}m"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
                elif status == "Crab":
                    title_msg = f"CRAB CAUGHT! {b.name} pushed too hard and lost momentum. New Position: {b.position * 20}m"
                    choice_idx = interactive_selection(["Continue"], "vertical", title_msg, b.color)
            
            # ------ END OF ROUND BONUSES ------
            self.apply_bonuses()
            draw_venue(self.boats)
            draw_leaderboard(sorted(self.boats, key=lambda x: (x.position, x.stroke_rate), reverse=True), "Leaderboard")
            time.sleep(5)
            self.check_finish_line()