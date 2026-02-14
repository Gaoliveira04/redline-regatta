import random
from src.engine.constants import PACE_CARDS, INSTABILITY_CARDS, STAMINA_CARDS

class Boat:
    def __init__(self, name, color, lane, is_npc = False):
        self.name = name
        self.color = color
        self.lane = lane
        self.is_npc = is_npc

        # ------ MOVEMENT ------
        self.round = 0
        self.position = 0
        self.stroke_rate = 2
        self.caught_crab = False
        self.finished = False

        # ------ CARDS ------        
        self.draw_pile = (PACE_CARDS + INSTABILITY_CARDS).copy()
        random.shuffle(self.draw_pile)

        self.hand = []
        self.discard_pile = []
        self.stamina_pile = STAMINA_CARDS.copy()
