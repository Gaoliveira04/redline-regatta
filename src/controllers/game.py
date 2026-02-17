from src.engine.constants import VENUE_LENGTH, SPLITS
from src.interface.view import GameView
from src.engine.race_logic import GameLogic
from src.engine.npc_logic import NPCLogic


class GameController:
    """Manages the main game flow and round mechanics."""
    def __init__(self, chosen_colors):
        """
        Create boats and start game
        """
        self.game_running = True
        self.boats = GameLogic.create_boat(chosen_colors)

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
                GameView.show_bonus(affected, "change_2")
            elif len(affected) == 1:
                GameView.show_bonus(affected, "change_1")
            else:
                GameView.show_bonus(affected, "change_0")

            for i in range(1, len(sorted_boats)):
                current_boat = sorted_boats[i]
                boat_ahead = sorted_boats[i-1]
                
                if boat_ahead.finished or current_boat.finished or current_boat.penalized or current_boat.caught_crab:
                    continue

                if GameLogic.can_use_motivation(current_boat, boat_ahead):
                    if not current_boat.is_npc:
                        option = GameView.choose_motivation(current_boat, boat_ahead)

                        if option == "Activate Motivation (+2 Spaces, Cost 1 Stamina)":
                            GameLogic.pay_stamina_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

                    else:
                        use_motivation = NPCLogic.choose_motivation(current_boat)
                        if use_motivation == "use":
                            GameLogic.pay_stamina_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

                            boats = [current_boat.name, boat_ahead.name]
                            GameView.show_bonus(boats, "motivation")

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
            GameView.render_game_screen(self.boats, "Podium")
    
    def run_game(self):
        """
        Control and start game rounds structure:
        1. Change or maintain Stroke Rate
        2. Play cards
        3. Advance boat
        4. Replenish hand
        """
        GameView.render_game_screen(self.boats)
        while self.game_running:
            # ------ INDIVIDUAL PHASE ------
            for b in self.boats:
                if b.finished:
                    continue
                
                b.caught_crab = False
                b.penalized = False
                GameLogic.draw_cards(b)
                GameView.show_player_turn(b)

                if GameLogic.check_clustered_hand(b):
                    GameView.show_event(b, "clustered")
                    GameLogic.replenish_hand(b)
                    continue

                # Stroke Rate Phase
                exhaustion_status = GameLogic.check_stamina(b)
                if exhaustion_status == "ok":
                    if not b.is_npc:
                        rate_choice = GameView.get_sroke_rate(b)
                        result = GameLogic.change_stroke_rate(b, rate_choice)
                    else:
                        rate_choice = NPCLogic.choose_stroke_rate(b)
                        result = GameLogic.change_stroke_rate(b, rate_choice)

                    if result == "failed":
                            GameView.show_event(b, "failed")
                else:
                    GameView.show_event(b, "no stamina")

                # Play cards
                cards_selected = []
                available_cards, cards_needed = GameLogic.get_playable_cards(b)

                if not b.is_npc:
                    while len(cards_selected) < cards_needed:
                        for _ in range(cards_needed):
                            card = GameView.get_card_to_play(b, available_cards, cards_selected, cards_needed)
                            available_cards.remove(card)
                            cards_selected.append(card)
                else:
                    cards = NPCLogic.choose_cards(b)
                    cards_selected = cards[:cards_needed]

                # Movement and Split Limtis
                movement= GameLogic.calculate_movement(b, cards_selected)
                status, inf = GameLogic.check_split_limit(b, movement, SPLITS)

                if status == "passed":
                    GameLogic.apply_movement(b, movement)
                elif status == "tired":
                    GameLogic.apply_movement(b, movement)
                    GameLogic.pay_stamina_cards(b, inf)
                else:
                    GameLogic.apply_crab(b, inf)

                # Optional cards discard
                cards_selected = []
                available_cards, _ = GameLogic.get_playable_cards(b)

                if not b.is_npc:
                    option = GameView.choose_to_discard_cards(b)

                    if option == "Discard":
                        while True:
                            if not available_cards:
                                break
                            
                            card = GameView.get_card_to_discard(b, available_cards)
                            if card == "Done":
                                break
                            
                            available_cards.remove(card)
                            cards_selected.append(card)

                if cards_selected:
                    GameLogic.discard_cards(b, cards_selected)
                
                # Replenish hand
                GameLogic.replenish_hand(b)

                b.round += 1

                # Display results
                GameView.show_event(b, status)
            
            # ------ END OF ROUND BONUSES ------
            self.apply_bonuses()
            GameView.render_game_screen(self.boats, "Leaderboard")
            self.check_finish_line()