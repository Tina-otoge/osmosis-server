from datetime import datetime
import math

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

    def osu_link(self):
        return 'https://osu.ppy.sh/users/{}'.format(self.id)


class Score(db.Model, SubmittableData):
    id = db.Column(db.Integer, primary_key=True)
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
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    version = db.Column(db.Integer)

    def points(self):
        return math.floor(
            ((self.great * 6 + self.good * 2 + self.meh * 1) / 3)
        )

    def display_accuracy(self):
        if self.accuracy == 1:
            return '100%'
        return '%.2f%%' % (self.accuracy * 100)

    def display_mods(self):
        return self.mods.split(':')[:-1]

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
            self.mods = data['mods']
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
    mode = db.Column(db.String(128))
    duration = db.Column(db.Integer)
    bpm = db.Column(db.String(128))
    name = db.Column(db.String(128))
    name_romanized = db.Column(db.String(128))
    artist = db.Column(db.String(128))
    artist_romanized = db.Column(db.String(128))
    difficulty_name = db.Column(db.String(128))
    creator_name = db.Column(db.String(128))
    scores = db.relationship('Score', backref='chart', lazy='dynamic')

    def update_fields(self, data):
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

    def osu_link(self):
        return 'https://osu.ppy.sh/b/{}'.format(self.id)

    def __init__(self, data):
        self.id = data['chart_id']
        self.update_fields(data)
