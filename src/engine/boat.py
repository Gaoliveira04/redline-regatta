import random
from src.engine.constants import EASY, PACE_CARDS, SUFFERING_CARDS, EXHAUSTION_CARDS

class Boat:
    def __init__(self, name, color, lane, is_npc = False):
        self.name = name
        self.color = color
        self.lane = lane
        self.is_npc = is_npc

        # ------ MOVEMENT ------
        self.position = 0
        self.stroke_rate = EASY
        self.finished = False

        # ------ CARDS ------        
        self.draw_pile = (PACE_CARDS + SUFFERING_CARDS).copy()
        random.shuffle(self.draw_pile)

        self.hand = []
        self.discard_pile = []
        self.stamina_pile = EXHAUSTION_CARDS.copy()
