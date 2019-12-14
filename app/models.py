from datetime import datetime
import math

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

DATETIME_BACK = '%Y-%m-%d %H:%M:%S'

from app import db

class SubmittableData:
    pass


class Player(db.Model, SubmittableData):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    osu_join_date = db.Column(db.DateTime)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='player', lazy='dynamic')
    avatar_url = db.Column(db.String(512))
    cover_url = db.Column(db.String(512))
    country = db.Column(db.String(128))
    country_code = db.Column(db.String(2))
    twitter = db.Column(db.String(32))
    discord = db.Column(db.String(32))
    website = db.Column(db.String(512))

    def update_fields(self, data):
        if data.get('name'):
            self.username = data['name']
        if data.get('join_date'):
            self.osu_join_date = datetime.strptime(
                data['join_date'].split('+')[0], '%Y-%m-%dT%H:%M:%S'
            )
        if data.get('avatar'):
            self.avatar_url = data['avatar']
        if data.get('cover'):
            self.cover_url = data['cover']
        if data.get('country'):
            self.country = data['country']
        if data.get('country_code'):
            self.country_code = data['country_code']
        if data.get('twitter'):
            self.twitter = data['twitter']
        if data.get('discord'):
            self.discord = data['discord']
        if data.get('website'):
            self.website = data['website']

    def __init__(self, data):
        self.id = data['id']
        self.update_fields(data)

    def get_ranks(self, rank, above=False):
        if above:
            ranks = self.get_all_ranks(just_names=True)
            target = ranks[ranks.index(rank):]
        else:
            target = [rank]
        return self.scores.filter(Score.rank.in_(rank)).count()

    def get_all_ranks(self, just_names=False):
        ranks = ['D', 'C', 'B', 'A', 'A+', 'S', 'S+', 'S++', 'SS']
        if just_names:
            return ranks
        return {x: self.get_ranks(x) for x in ranks}

    def get_osu_link(self):
        return 'https://osu.ppy.sh/users/{}'.format(self.id)


class Score(db.Model, SubmittableData):
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
    chart_id = db.Column(db.Integer, db.ForeignKey('chart.id'))
    mode = db.Column(db.String(128), default='osu')
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    version = db.Column(db.Integer)

    def get_max_notes(self):
        return self.perfect + self.great + self.good + self.ok + self.meh + self.miss

    @hybrid_property
    def points(self):
        return (self.perfect * 7 + self.great * 6 + self.good * 2 + self.ok + self.meh) / 3

    @points.expression
    def sortable_points(cls):
            return cls.perfect * 7 + cls.great * 6 + cls.good * 2 + cls.ok + cls.meh

    @hybrid_property
    def flairs(self):
        result = []
        if self.get_accuracy() == 1:
            result.append('perfect')
        elif self.miss == 0:
            result.append('full combo')
        return result


    def get_max_points(self):
        if self.mode == 'mania':
            return math.floor(self.get_max_notes() * 7 / 3)
        return self.get_max_notes() * 2

    def get_accuracy(self):
         return self.points / self.get_max_points()

    def is_supported(self, chart=None):
        return not self.is_convert(chart)

    def is_convert(self, chart=None):
        chart = chart or self.chart
        print('score mode:', self.mode)
        print('chart mode:', chart.mode)
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
        if self.accuracy == 1:
            return 'SS'
        if self.accuracy > 0.985:
            return 'S++'
        if self.accuracy > 0.9725:
            return 'S+'
        if self.accuracy > 0.95:
            return 'S'
        if self.accuracy > 0.925:
            return 'A+'
        if self.accuracy > 0.9:
            return 'A'
        if self.accuracy > 0.8:
            return 'B'
        if self.accuracy > 0.7:
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

class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer)
    mode = db.Column(db.String(128))
    duration = db.Column(db.Integer)
    bpm = db.Column(db.String(128))
    name = db.Column(db.String(128))
    name_romanized = db.Column(db.String(128))
    artist = db.Column(db.String(128))
    artist_romanized = db.Column(db.String(128))
    difficulty_name = db.Column(db.String(128))
    hp = db.Column(db.Float)
    cs = db.Column(db.Float)
    od = db.Column(db.Float)
    ar = db.Column(db.Float)
    sr = db.Column(db.Float)
    creator_name = db.Column(db.String(128))
    scores = db.relationship('Score', backref='chart', lazy='dynamic')

    def update_fields(self, data):
        if data.get('set_id'):
            self.set_id = data['set_id']
        if data.get('mode'):
            self.mode = data['mode']
        if data.get('duration'):
            self.duration = data['duration']
        if data.get('bpm'):
            self.bpm = data['bpm']
        if data.get('song_name'):
            self.name = data['song_name']
        if data.get('romanized_name'):
            self.name_romanized = data['romanized_name']
        if data.get('artist_name'):
            self.artist = data['artist_name']
        if data.get('romanized_artist'):
            self.artist_romanized = data['romanized_artist']
        if data.get('difficulty_name'):
            self.difficulty_name = data['difficulty_name']
        if data.get('hp'):
            self.hp = data['hp']
        if data.get('cs'):
            self.cs = data['cs']
        if data.get('od'):
            self.od = data['od']
        if data.get('ar'):
            self.ar = data['ar']
        if data.get('sr'):
            self.sr = data['sr']
        if data.get('set_creator_name'):
            self.creator_name = data['set_creator_name']

    def display_name(self):
        if self.name == self.name_romanized or self.name_romanized is None:
            return self.name
        if self.name is None:
            return self.name_romanized
        return '{0.name} ({0.name_romanized})'.format(self)

    def display_artist(self):
        if self.artist == self.artist_romanized or self.artist_romanized is None:
            return self.artist
        if self.artist is None:
            return self.artist_romanized
        return '{0.artist} ({0.artist_romanized})'.format(self)

    def display_full_name(self):
        return '{} - {}'.format(self.display_name(), self.display_artist())

    def display_full_original(self):
        return '{} - {}'.format(
            self.artist or self.artist_romanized,
            self.name or self.name_romanized
        )

    def display_full_romanized(self):
        return '{} - {}'.format(
            self.artist_romanized or self.artist,
            self.name_romanized or self.name
        )

    def display_details(self, name):
        filter = lambda x: round(x, 2) if x else 0
        if name:
            return filter(getattr(self, name))
        details = {
            'sr': self.sr,
            'cs': self.cs,
            'hp': self.hp,
            'ar': self.ar,
        }
        return {key: filter(value) for key, value in details}

    def get_osu_link(self):
        return 'https://osu.ppy.sh/b/{}'.format(self.id)

    def get_osu_card_url(self):
        if not self.set_id:
            return False
        return 'https://assets.ppy.sh/beatmaps/{}/covers/card.jpg'.format(self.set_id)

    def get_osu_preview(self):
        if not self.set_id:
            return False
        return 'https:////b.ppy.sh/preview/{}.mp3'.format(self.set_id)

    def __init__(self, data):
        self.id = data['chart_id']
        self.update_fields(data)
