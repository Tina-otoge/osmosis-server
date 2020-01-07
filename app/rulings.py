MODS_WHITELIST = [
    'NF',
    'SD',
    'DT',
    'HD',
    'FL',
    'AR',
]

RANKS = {
    'SS': 1,
    'S++': 0.985,
    'S+': 0.9725,
    'S': 0.95,
    'A+': 0.925,
    'A': 0.9,
    'B': 0.8,
    'C': 0.7,
    'D': 0
}

class Judge:
    PERFECT = 350
    GREAT = 300
    GOOD = 100
    OK = 50
    MEH = 50

MAX_JUDGE = {
    'osu': Judge.GREAT,
    'mania': Judge.PERFECT,
    'fruits': Judge.PERFECT,
    'taiko': Judge.GREAT,
}

def calculate_osmos(accuracy, difficulty, mods=[]):
    for mod in mods:
        if mod['acronym'] not in MODS_WHITELIST:
            return 0
    smooth_limit = 0.95
    if not difficulty:
        return 0
    if accuracy < smooth_limit:
        accuracy_weight = 10
    else:
        accuracy_weight = 10 - ((accuracy - smooth_limit) * 50)
    return int(
        (difficulty ** 2)
        * (accuracy ** accuracy_weight)
        * 10
    )


def get_rank(accuracy):
    for rank, min in RANKS.items():
        if accuracy >= min:
            return rank
