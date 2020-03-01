DATETIME_BACK = '%Y-%m-%d %H:%M:%S'
DATETIME_FRONT = '%B %-d %Y at %H:%M:%S'


class Hash:
    def __init__(self, hash):
        self.hash = hash

    def display(self):
        return self.hash[8:]


from .chart import Chart
from .player import Player
from .score import Score
from .set import Set


__all__ = [Chart, Player, Score, Set, Hash, DATETIME_FRONT, DATETIME_BACK]
