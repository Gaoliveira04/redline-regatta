import random
from src.engine.constants import EASY, MIN_RATE, MAX_RATE, HAND_LIMIT

class CardLogic:
    """
    Handles everything related to Cards, Decks, and Stroke Rates.
    """

    # ------ DECK MANAGEMENT ------ 
    def draw_cards(boat):
        """
        Draw top cards from draw deck to the hand until it has 7 cards.
        Handles deck reshuffling if draw pile is empty.
        """
        while len(boat.hand) < HAND_LIMIT:
            # Detect if draw deck and discard pile are empty
            if not boat.draw_pile:
                if not boat.discard_pile:
                    # If both decks are empty, give failsafe cared
                    boat.draw_pile = [1]
                else:
                    boat.draw_pile.extend(boat.discard_pile)
                    boat.discard_pile.clear()
                    random.shuffle(boat.draw_pile)  
            
            card = boat.draw_pile.pop(0)
            boat.hand.append(card)
        
        # Sort hand: pace cards, suffering cards and exhaustion cards
        boat.hand.sort(key=lambda x: (x == "e", x == "s", x))

    def calculate_movement(boat, played_cards: list):
        """
        """
        spaces_moved = 0

        for card in played_cards:
            if isinstance(card, int):
                spaces_moved += card
            elif card == "s":
                if not boat.draw_pile:
                    if boat.discard_pile:
                        boat.draw_pile = boat.discard_pile[:]
                        boat.discard_pile = []
                        random.shuffle(boat.draw_pile)
                    else:
                        spaces_moved += 0

                flipped = boat.draw_pile.pop(0)
                boat.discard_pile.append(flipped)
                if isinstance(flipped, int):
                    spaces_moved += flipped
                else:
                    spaces_moved += random.randint(1,2)

        boat.discard_pile.extend(played_cards)
        return spaces_moved
    
    def check_clustered_hand(boat):
        """
        Detect if hand of player is a Cluttered Hand
        """
        cards_required = boat.stroke_rate + 1

        # Detect playable cards
        playable_cards = []
        for c in boat.hand:
            if c != "e":
                playable_cards.append(c)

        if len(playable_cards) < cards_required:
            boat.discard_pile.extend(playable_cards)
            for c in playable_cards:
                boat.hand.remove(c)
            boat.stroke_rate = EASY
            return True
        return False

    # ------ STROKE RATE MANAGEMENT ------ 
    def change_stroke_rate(boat, choice: str, use_jump: bool):
        """
        Applies a change in stroke rate.
        Detects if user can do jumps in stroke rate and permission.
        """
        if choice == "maintain":
            return False

        # Detect if user wants and can jump stroke rate
        if use_jump and len(boat.stamina_pile) > 0:
            step = 2 
        else:
            step = 1

        # Change stroke rate
        new_stroke_rate = boat.stroke_rate
        if choice == "up":
            new_stroke_rate += step
        elif choice == "down":
            new_stroke_rate -= step

        # Apply stroke rate bounds
        new_stroke_rate = max(MIN_RATE, min(MAX_RATE, new_stroke_rate))

        # Pay exhaustion cost if jump succeeded
        if abs(new_stroke_rate - boat.stroke_rate) == 2:
            boat.stamina_pile.pop()
            boat.discard_pile.append("e")

        boat.stroke_rate = new_stroke_rate
    
    def easy_rate_cooldown(boat):
        """
        Easy rate bonus: 
        Move up to 2 Exhaustion cards from hand back to the stamina pile
        """
        # Only appens in the Easy stroke rate
        if boat.stroke_rate != EASY:
            return
    
        recovery_count = 0
        for card in boat.hand[:]:
            if card == "e" and recovery_count < 2:
                boat.hand.remove("e")
                boat.stamina_pile.append("e")
                recovery_count += 1

    # ------ STAMINA PILE MANAGEMENT ------     
    def pay_exhaustion_cards(boat, amount: int):
        """
        Jump pace: 1 card
        Motivation: 1 card
        Split limit: Pace - Pace limit
        """
        if len(boat.stamina_pile) < amount:
            boat.stamina_pile.clear()
            return False

        for _ in range(amount):
            boat.stamina_pile.pop()
            boat.discard_pile.append("e")
        return True

    # ------------ END OF TURN ------------
    def finish_turn(boat):
        """
        Apply rules of finishing turn.
        """
        CardLogic.easy_rate_cooldown(boat)
        CardLogic.draw_cards(boat)