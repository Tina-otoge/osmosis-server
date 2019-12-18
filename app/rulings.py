MODS_WHITELIST = [
    'NF',
    'SD',
    'DT',
    'HD',
    'FL',
    'AR',
]

class Judge:
    PERFECT = 350
    GREAT = 300
    GOOD = 100
    OK = 50
    MEH = 50

def calculate_osmos(accuracy, difficulty):
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
