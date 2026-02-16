import random
from src.engine.constants import SPLITS, AGGRESSION_PROFILES
from src.engine.boat import Boat

class NPCLogic:
    def choose_cards(boat: Boat):
        """
        Picks the best cards to play from the hand.
        """
        playable = [c for c in boat.hand if c != 's']
        playable.sort(
            key=lambda x: (x if isinstance(x, int) else 2),
            reverse=True
        )
        return playable
    
    def calculate_speed_for_rate(boat: Boat, rate):
        """
        Estimates total movement value of a card selection.
        """
        rate_map = {2: 4, 1: 2, 0: 1}
        needed = rate_map[rate]
        playable_cards = NPCLogic.choose_cards(boat)

        if len(playable_cards) < needed:
            return 0
        
        cards_to_play = playable_cards[:needed]
        return sum([(c if isinstance(c, int) else 2) for c in cards_to_play])
    
    def detect_pace_limits(boat: Boat, est_speed, limit = SPLITS):
        """
        Checks if the estimated speed will cross a split line.
        """
        # Check Place Limits
        next_pos = boat.position + est_speed
        next_limit_pace = None
        next_limit_loc = None
        for limit_loc, limit_pace in limit.items():
            if boat.position < limit_loc <= next_pos:
                next_limit_loc = limit_loc
                next_limit_pace = limit_pace
                break
        return next_limit_loc, next_limit_pace

    def choose_stroke_rate(boat: Boat, limit = SPLITS):
        """
        Decides the target stroke rate based on stamina, hand state, and course position.
        """
        # Low Stamina Checks
        stamina_count = len(boat.stamina_pile)
        if stamina_count == 0:
            return 0
        
        if boat.hand.count("s") >= 1 and stamina_count < 3:
            return 0
        
        # Determine opotions
        best_safe_rate = 0
        best_risky_rate = 0
        risky_limit_loc = None
        risky_cost = 0

        for rate in [2,1,0]:
            est_speed = NPCLogic.calculate_speed_for_rate(boat, rate)
            if est_speed == 0 and rate > 0: 
                continue
            
            # Risk assesment
            next_limit_loc, next_limit_pace = NPCLogic.detect_pace_limits(boat, est_speed, limit)
            if next_limit_pace is None or est_speed <= next_limit_pace:
                if rate > best_safe_rate:
                    best_safe_rate = rate
            else:
                cost = max(1, int(est_speed - next_limit_pace))
                safety_buffer = 2 if boat.position < 80 else 0
                if (stamina_count - cost) < safety_buffer:
                    continue

                if rate > best_risky_rate:
                    best_risky_rate = rate
                    risky_limit_loc = next_limit_loc
                    risky_cost = cost
            
        # Make decision
        if best_risky_rate <= best_safe_rate:
            return best_safe_rate
        
        # Get the aggression probability for this specific limit
        base_prob = AGGRESSION_PROFILES.get(risky_limit_loc, 0.40)

        # Be more careful if stamina is getting low
        stamina_factor = 1.0 if stamina_count >= 4 else 0.6
        final_prob = base_prob * stamina_factor

        # Roll the dice ONCE
        if random.random() < final_prob:
            return best_risky_rate

        return best_safe_rate
    
    def choose_motivation(boat: Boat):
        """
        Choose to use Motivation bonus if near the end of the race or have plenty of energy.
        """
        threshold = 1 if boat.position > 80 else 4
        if len(boat.stamina_pile) >= threshold:
            if random.random() < 0.50:
                return "use"
        return "no"
