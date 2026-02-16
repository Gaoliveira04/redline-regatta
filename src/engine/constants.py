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
INSTABILITY_CARDS = ["i","i","i"]
STAMINA_CARDS = ["s","s","s","s","s","s","s"]
HAND_LIMIT = 7

# ------------ STROKE RATE CONSTANTS ------------
RATES =[0,1,2]

# ------------ SPLIT LIMITS ------------
SPLITS = {
    25: 7, 
    50: 7, 
    75: 6,
    87: 5
}

METERS = {
    25: "500m",
    50: "1000m",
    75: "1500m",
    87: "1750m"
}

AGGRESSION_PROFILES = {
    25: 0.10, 
    50: 0.20,
    75: 0.40,
    85: 0.85
}
