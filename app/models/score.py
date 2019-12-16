from datetime import datetime
import math

from sqlalchemy.ext.hybrid import hybrid_property

from app import db

from . import DATETIME_BACK

class Judge:
    PERFECT = 350
    GREAT = 300
    GOOD = 200
    OK = 50
    MEH = 50

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    perfect = db.Column(db.Integer, default=0)
    ok = db.Column(db.Integer, default=0)
    great = db.Column(db.Integer, default=0)
    good = db.Column(db.Integer, default=0)
    meh = db.Column(db.Integer, default=0)
    miss = db.Column(db.Integer, default=0)
    rank = db.Column(db.String(2))
    accuracy = db.Column(db.Float)
    max_combo = db.Column(db.Integer)
    mods = db.Column(db.String(128))
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.Column(db.String(128))
    mode = db.Column(db.String(128), default='osu')

    chart_id = db.Column(db.Integer, db.ForeignKey('chart.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    version = db.Column(db.Integer)

    def get_max_notes(self):
        return self.perfect + self.great + self.good + self.ok + self.meh + self.miss

    def get_ratio(self):
        if self.mode == 'mania':
            return 0.5 * Judge.PERFECT
        return 0.5 * Judge.GREAT

    @hybrid_property
    def points(self):
        return (
            self.perfect * Judge.PERFECT +
            self.great * Judge.GREAT +
            self.good * Judge.GOOD +
            self.ok * Judge.OK +
            self.meh * Judge.MEH
        ) / self.get_ratio()

    @points.expression
    def sortable_points(cls):
            return (
                self.perfect * Judge.PERFECT +
                self.great * Judge.GREAT +
                self.good * Judge.GOOD +
                self.ok * Judge.OK +
                self.meh * Judge.MEH
            )

    @hybrid_property
    def flairs(self):
        result = []
        if self.get_accuracy() == 1:
            result.append('perfect')
        elif self.miss == 0:
            result.append('full combo')
        return result


    def get_max_points(self):
        return self.get_max_notes() * 2

    def get_accuracy(self):
         return self.points / self.get_max_points()

    def is_supported(self, chart=None):
        if not self.chart_id:
            return False
        if self.is_convert(chart):
            return False
        return True

    def is_convert(self, chart=None):
        chart = chart or self.chart
        return self.mode != chart.mode

    def display_accuracy(self):
        accuracy = self.get_accuracy()
        if accuracy == 1:
            return '100%'
        return '%.2f%%' % (accuracy * 100)

    def display_judges(self):
        modes_judges = {
            'osu'   : [self.great, self.good, self.meh, self.miss],
            'taiko' : [self.great, self.good, self.miss],
            'fruits': [self.perfect, self.miss],
            'mania' : [self.perfect, self.great, self.good, self.ok, self.meh, self.miss]
        }
        return ' | '.join(map(str, modes_judges[self.mode]))

    def display_mod(self, mod):
        infos = []
        for key, value in mod.items():
            if key != 'acronym':
                infos.append('{}: {}'.format(key, value))
        return '<span data-toggle="tooltip" data-html="true" title="{}">{}</span>'.format(
            '<br>'.join(infos), mod['acronym']
        )

    def get_mods(self):
        if self.version == 1:
            mods = self.mods.split(':')[:-1]
            if not ''.join(mods):
                return []
            return [{'acronym': mod} for mod in mods]
        if not self.mods:
            return []
        mods = self.mods.split('\n')
        if ''.join(mods):
            return [{
                pair.split('=')[0]: pair.split('=')[1]
                    for pair in mod.split(' ')
                }
                for mod in mods
            ]
        return []

    def display_rank(self):
        accuracy = self.get_accuracy()
        if accuracy == 1:
            return 'SS'
        if accuracy > 0.985:
            return 'S++'
        if accuracy > 0.9725:
            return 'S+'
        if accuracy > 0.95:
            return 'S'
        if accuracy > 0.925:
            return 'A+'
        if accuracy > 0.9:
            return 'A'
        if accuracy > 0.8:
            return 'B'
        if accuracy > 0.7:
            return 'C'
        return 'D'

    def update_fields(self, data):
        if data.get('great'):
            self.great = data['great']
        if data.get('good'):
            self.good = data['good']
        if data.get('meh'):
            self.meh = data['meh']
        if data.get('miss'):
            self.miss = data['miss']
        if data.get('perfect'):
            self.perfect = data['perfect']
        if data.get('ok'):
            self.ok = data['ok']
        if data.get('accuracy'):
            self.accuracy = data['accuracy']
        if data.get('rank'):
            self.rank = data['rank']
        if data.get('max_combo'):
            self.max_combo = data['max_combo']
        if data.get('mods'):
            if isinstance(data['mods'], str) and ':' in data['mods']:
                self.mods = '\n'.join([
                    'acronym={}'.format(x) for x in data['mods'][:-1].split(':')
                ])
            else:
                self.mods = '\n'.join([' '.join(['{}={}'.format(key, value)
                    for key, value in mod.items()])
                          for mod in data['mods']])
        if data.get('mode'):
            self.mode = data['mode']
        if data.get('achieved_at'):
            self.achieved_at = datetime.strptime(
                data['achieved_at'].split(',')[0], DATETIME_BACK
            )
        if data.get('client'):
            self.client = data['client']

    def __init__(self, data):
        self.update_fields(data)

