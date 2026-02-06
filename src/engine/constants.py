VENUE_LENGTH = 100
# ------------ BOAT CONSTANTS ------------
COLORS = {
    "Black": "\033[0;30m",
    "Red": "\033[0;31m",
    "Green": "\033[0;32m",
    "Brown": "\033[0;33m",
    "Blue": "\033[0;34m",
    "Purple": "\033[0;35m",
    "Cyan": "\033[0;36m",
    "Yellow": "\033[1;33m"
}

LANES = [1,2,3,4,5,6]

# ------------ CARDS CONSTANTS ------------
PACE_CARDS = [1,1,1,1,1,1,2,2,2,2,3,3]
SUFFERING_CARDS = ["s","s","s"]
EXHAUSTION_CARDS = ["e","e","e","e","e","e"]
HAND_LIMIT = 7

# ------------ STROKE RATE CONSTANTS ------------

EASY = 0      # 36 spm
STEADY = 1    # 39 spm
RACE = 2      # 42 spm
SPRINT = 3    # 45 spm

MIN_RATE = EASY
MAX_RATE = SPRINT

# ------------ SPLIT LIMITS ------------
SPLITS = {
    25: 4, 
    50: 5, 
    75: 6,
    85: 8
}
