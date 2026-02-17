import time
from src.engine.boat import Boat
from src.engine.constants import RATES
from src.interface.draw import clear_screen, draw_venue, draw_leaderboard, stroke_rate_name
from src.interface.interaction import interactive_selection

class GameView:
    @staticmethod
    def render_game_screen(boats, title = "Redline Regatta"):
        """Draw venue and leaderbord."""
        clear_screen()
        draw_venue(boats)
        draw_leaderboard(sorted(boats,key=lambda x: (x.round, -x.position, -x.stroke_rate)), title)
        time.sleep(5)

    @staticmethod
    def show_player_turn(boat: Boat):
        """Show next player playing."""
        title_msg = f"{boat.name}'s Turn (Pos: {boat.position * 20}m | Rate: {stroke_rate_name(boat.stroke_rate)})"
        interactive_selection(["Continue"], "vertical", title_msg, boat.color)

        # Show stats if not player is not a npc
        if not boat.is_npc:
            title_msg = f"{boat.name}'s (Pos: {boat.position * 20}m | Rate: {stroke_rate_name(boat.stroke_rate)} | Hand: {boat.hand} | Stamina: {len(boat.stamina_pile)})"
            interactive_selection(["Continue"], "vertical", title_msg, boat.color)

    @staticmethod
    def get_sroke_rate(boat: Boat):
        """Show stroke rates available."""
        options = RATES
        title_msg = f"Current Rate: {stroke_rate_name(boat.stroke_rate)}. Select target rate for this round."
        choice_idx = interactive_selection(stroke_rate_name(options), "vertical", title_msg, boat.color)
        return options[choice_idx]
    
    @staticmethod
    def get_card_to_play(boat: Boat, available_cards: list, cards_selected: list, cards_needed: int):
        """Show available cards and counter of how many were choosen."""
        title_msg = f"Select Card {len(cards_selected) + 1}/{cards_needed}:"
        choice_idx = interactive_selection(available_cards, "horizontal", title_msg, boat.color)
        return available_cards[choice_idx]
    
    @staticmethod
    def choose_to_discard_cards(boat: Boat):
        """Ask if user wants to discard cards."""
        options = ["Discard", "No discard"]
        choice_idx = interactive_selection(options, "vertical", "Discard any cards?", boat.color) 
        return options[choice_idx]
    
    @staticmethod
    def get_card_to_discard(boat: Boat, available_cards: list):
        """Show available cards and allow card discard."""
        options = available_cards + ["Done"]
        choice_idx = interactive_selection(options, "horizontal", "Select cards to discard:", boat.color)
        return options[choice_idx]

    @staticmethod
    def choose_motivation(current_boat, boat_ahead):
        """Ask if user wants to use Motivation bonus."""
        options = ["Activate Motivation (+2 Spaces, Cost 1 Stamina)", "Hold Position"]
        title_msg = f"MOTIVATION: {current_boat.name} is passing {boat_ahead.name}! Activate bonus {current_boat.name}?"
        choice_idx = interactive_selection(options, "vertical", title_msg, current_boat.color)
        return options[choice_idx]

    @staticmethod
    def show_event(boat: Boat, event):
        """Shows player clusterand hand notification, failed stroke rate jumps and attempts to pass pace limits."""
        messages = {
            "clustered": f"CLUSTERED HAND! {boat.name} can't find rhythm and loses the stroke this round.",
            "no stamina": f"NO STAMINA! {boat.name} is exhausted and the stroke rate drops.",
            "failed": f"LACK OF STAMINA! {boat.name} can't sustain the surge and falls back.",
            "passed": f"RHYTHM FOUND! {boat.name} mantains a steady pace. Position: {boat.position * 20}m",
            "tired": f"PUSHING TOO HARD! {boat.name} puts the hand on the fire. Position: {boat.position * 20}m",
            "crab": f"CRAB CAUGHT! {boat.name} loses control of the oar and loses momentum. Position: {boat.position * 20}m"
        }
        interactive_selection(["Continue"], "vertical", messages[event], boat.color)

    @staticmethod
    def show_bonus(boats, event):
        """Show end-of-round bonus notifications."""
        if event == "change_0":
            title_msg = "CHANGES OF TIDES: No boats eligible."
        elif event == "change_1":
            title_msg = f"CHANGES OF TIDES: A favorable current lifts {boats[0]} forward."
        elif event == "change_2":
            title_msg = f"CHANGES OF TIDES: A favorable current lifts {boats[0]} and {boats[1]} forward."
        elif event == "motivation":
            title_msg = f"MOTIVATION: {boats[0]} feeds off the chase and surges past {boats[1]}!"
        else:
            title_msg = "Unknown bonus event."
        interactive_selection(["Continue"], "vertical", title_msg)