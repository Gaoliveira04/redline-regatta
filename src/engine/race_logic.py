from src.engine.constants import EASY, STEADY, SPLITS

class RaceLogic:
    def check_split_limit(boat, speed_this_turn):
        """
        Check if a boat passed a split limit too fast.
        Split limits at 500, 1000, 1500 and 1800.
        """
        next_pos = boat.position + speed_this_turn

        # Find if boat just crossed a split, above the speed
        limit_broken = None
        for loc, limit in SPLITS.items():
            if boat.position < loc <= next_pos:
                if speed_this_turn > limit:
                    limit_broken = (loc, limit)
                    break

        # If boat crossed split limit, penalize Stamina
        if limit_broken:
            loc, limit = limit_broken
            excess = speed_this_turn - limit

            if len(boat.stamina_pile) >= excess:
                for _ in range(excess):
                    boat.stamina_pile.pop()
                    boat.discard_pile.append("e")
                return False
            else:
                boat.stamina_pile.clear()
                boat.position = loc - 1
                if boat.stroke_rate in [EASY,STEADY]:
                    boat.stroke_rate = EASY
                    boat.hand.append("s")
                else:
                    boat.stroke_rate = EASY
                    boat.hand.append("s") 
                    boat.hand.append("s")
                return True
        else:
            return False