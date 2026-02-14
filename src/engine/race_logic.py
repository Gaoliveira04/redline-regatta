import random
from src.engine.constants import VENUE_LENGTH, COLORS, HAND_LIMIT
from src.engine.boat import Boat

class GameLogic:
    def create_boat(chosen_colors: list):
        """
        Creates players boats and npc boats based on chosen color.
        """
        lanes = [1,2,3,4,5,6]
        available_colors = list(COLORS.keys())
        boats = []

        # Players boat
        for color_name in chosen_colors:
            if color_name == "No more players":
                continue

            lane = random.choice(lanes)
            lanes.remove(lane)
            available_colors.remove(color_name)
            boats.append(Boat(name= color_name, color= COLORS[color_name], lane= lane, is_npc= False))

        # Npc boat
        for lane in lanes:
            npc_color = available_colors.pop(0)
            boats.append(Boat(name= npc_color, color= COLORS[npc_color], lane= lane, is_npc= True))
        
        return sorted(boats, key=lambda x: x.lane) 

    # ------ DECKS MANAGEMENT ------ 
    def draw_cards(boat: Boat):
        """
        Draw top cards from draw deck to the hand until it has 7 cards.
        Handles deck reshuffling if draw pile is empty.
        """
        while len(boat.hand) < HAND_LIMIT:
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
        
        # Sort hand: pace cards, instability cards and stamina cards
        boat.hand.sort(key=lambda x: (x == "s", x == "i", x))

    def check_clustered_hand(boat):
        """
        Detect if hand of player is a Cluttered Hand
        """
        if boat.stroke_rate == 0 or boat.stroke_rate == 1:
            cards_required = boat.stroke_rate + 1
        else:
            cards_required = boat.stroke_rate + 2

        # Detect playable cards
        playable_cards = []
        for c in boat.hand:
            if c != "s":
                playable_cards.append(c)

        if len(playable_cards) < cards_required:
            boat.discard_pile.extend(playable_cards)
            for c in playable_cards:
                boat.hand.remove(c)
            boat.stroke_rate = 0
            return True
        return False
    
    def pay_stamina_cards(boat, amount: int):
        """
        Move an amount of Stamina Cards from the Stamina Pile into the Discard Pile
        """
        if len(boat.stamina_pile) < amount:
            while len(boat.stamina_pile) > 0:
                boat.stamina_pile.pop()
                boat.discard_pile.append("s")
            return False

        for _ in range(amount):
            boat.stamina_pile.pop()
            boat.discard_pile.append("s")
        return True

    # ------ STROKE RATE MANAGEMENT ------ 
    def change_stroke_rate(boat, choice: int):
        """
        Applies a change in stroke rate.
        Detects if user wants to jump in stroke rate and if can pay.
        """
        if choice not in [0,1,2]:
            return "failed"
        
        new_rate = choice
        if new_rate == boat.stroke_rate:
            return "maintain"

        # Pay stamina cost if jump succeeded
        if abs(new_rate - boat.stroke_rate) == 2:
            paid = GameLogic.pay_stamina_cards(boat, 1)
            if paid:
                boat.stroke_rate = new_rate
                return "changed"
            else:
                return "failed"

        boat.stroke_rate = new_rate
        return "changed"

    def min_rate_effect(boat):
        """
        Stroke Rate Effect: 35 spm:
        Move up to 2 Stamina cards from hand back to the stamina pile
        """
        # Only appens in the Easy stroke rate
        if boat.stroke_rate != 0:
            return
    
        recovery_count = 0
        for card in boat.hand[:]:
            if card == "s" and recovery_count < 2:
                boat.hand.remove("s")
                boat.stamina_pile.append("s")
                recovery_count += 1
    
    def max_rate_effect(boat):
        """
        Stroke Rate Effect: 45 spm:
        Move 1 Stamina Card from Stamina Pile to Discard Pile
        """
        # Only appens in the 45 spm
        if boat.stroke_rate != 2 or boat.round == 0:
            return
        
        if len(boat.stamina_pile) > 0:
            GameLogic.pay_stamina_cards(boat, 1)
        else:
            GameLogic.change_stroke_rate(boat, "35 spm")

    # ------ PLAY/DISCARD CARDS ------ 
    def get_playable_cards(boat: Boat):
        """
        Returns playable cards and number allowed this turn.
        """
        if boat.stroke_rate == 0 or boat.stroke_rate == 1:
            number_cards = boat.stroke_rate + 1
        else:
            number_cards = boat.stroke_rate + 2
        playable_cards = [c for c in boat.hand if c != "s"]
        return playable_cards, number_cards

    def discard_cards(boat: Boat, selected_cards: list):
        """
        Remove selected cards from hand and sends them to dicard
        """
        for card in selected_cards:
            if card in [1,2,3]:
                boat.discard_pile.append(card)
                boat.hand.remove(card)
    
    # ------ MOVEMENT ------ 
    def calculate_movement(boat, played_cards: list):
        """
        Calculate movement of boat based on played cards
        """
        spaces_moved = 0

        for card in played_cards:
            if isinstance(card, int):
                spaces_moved += card
            elif card == "i":
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

        GameLogic.discard_cards(boat, played_cards)
        return spaces_moved

    def check_split_limit(boat: Boat, speed_this_turn: int, limits: dict):
        """
        Check if a boat passed a split limit too fast.
        Applies split penalities if exceeded.
        """
        next_pos = boat.position + speed_this_turn

        # Find if boat just crossed a split, above the speed
        for split_loc, split_limit in limits.items():
            if boat.position < split_loc <= next_pos:
                if speed_this_turn > split_limit:
                    excess = speed_this_turn - split_limit

                    if len(boat.stamina_pile) > excess:
                        GameLogic.pay_stamina_cards(boat, excess)
                        return "Tired"
                    else:
                        boat.position = split_loc - 1
                        boat.caught_crab = True

                        penalty_amount = 0
                        if boat.stroke_rate == 0:
                            penalty_amount = 1
                        elif boat.stroke_rate == 1:
                            penalty_amount = 2
                        elif boat.stroke_rate == 2:
                            penalty_amount = 3
                    
                        GameLogic.pay_stamina_cards(boat, penalty_amount)
                                
                        boat.stroke_rate = 0
                        return "Crab"
        return "Passed"
    
    def apply_movement(boat: Boat, movement: int):
        """
        Applies movement to the boat.
        """
        boat.position = min(boat.position + movement, VENUE_LENGTH)

    # ------ REPLENISH HAND ------
    def replenish_hand(boat: Boat):
        """
        Finish the turn by refilling hand.
        """
        GameLogic.min_rate_effect(boat)
        GameLogic.max_rate_effect(boat)
        GameLogic.draw_cards(boat)
    
    # ------ BONUS PHASE ------
    def can_use_motivation(current_boat: Boat, boat_ahead: Boat):
        """
        Checks if motivation bonus is allowed.
        """
        distance = boat_ahead.position - current_boat.position
        if distance == 0 or distance == 1:
            if len(current_boat.stamina_pile) >= 1:
                return True
        else:
            return False

    def motivation_bonus(current_boat: Boat):
        """
        Applies motivation bonus.
        """
        current_boat.position += 2

    def change_tides_bonus(boat: Boat):
        """
        Applies change of tide bonus.
        """
        boat.position += 1