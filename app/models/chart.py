from sqlalchemy.ext.hybrid import hybrid_property

from app import db

from . import Hash


class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    osu_set_id = db.Column(db.Integer)
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

    hash = db.Column(db.String(64))
    ranked = db.Column(db.Boolean, default=False)
    max_combo = db.Column(db.Integer)
    ssr = db.Column(db.Integer)
    set_id = db.Column(db.Integer, db.ForeignKey('set.id'))

    scores = db.relationship('Score', backref='chart', lazy='dynamic')

    def __repr__(self):
        return '<Chart {0.id}: {1} [{0.difficulty_name}] {0.mode} ({0.creator_name})>'.format(self, self.display_full_romanized())

    @hybrid_property
    def frozen(self):
        return self.hash is not None

    def update_fields(self, data):
        if self.hash:
            return
        if data.get('set_id'):
            self.osu_set_id = data['set_id']
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

    def display_short(self):
        title = self.name_romanized or self.name
        return '{} [{}]'.format(title, self.difficulty_name)

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
        def filter(x):
            return round(x, 2) if x else 0
        if name:
            return filter(getattr(self, name))
        details = {
            'sr': self.sr,
            'cs': self.cs,
            'hp': self.hp,
            'ar': self.ar,
        }
        return {key: filter(value) for key, value in details}

    def display_difficulty(self):
        if self.ssr:
            return self.ssr / 4
        return self.display_details('sr')

    def display_hash(self):
        if self.hash is None:
            return False
        return Hash(self.hash).display()

    def get_osu_link(self):
        return 'https://osu.ppy.sh/b/{}'.format(self.id)

    def get_osu_card_url(self):
        if not self.osu_set_id:
            return False
        return 'https://assets.ppy.sh/beatmaps/{}/covers/card.jpg'.format(self.osu_set_id)

    def get_osu_thumbnail_url(self):
        if not self.osu_set_id:
            return False
        return 'https://assets.ppy.sh/beatmaps/{}/covers/list.jpg'.format(self.osu_set_id)

    def get_osu_preview(self):
        if not self.osu_set_id:
            return False
        return 'https://b.ppy.sh/preview/{}.mp3'.format(self.osu_set_id)

    def get_osu_download(self):
        if not self.osu_set_id:
            return False
        return 'https://osu.ppy.sh/beatmapsets/{}/download'.format(self.osu_set_id)

    def __init__(self, data):
        self.id = data['chart_id']
        self.update_fields(data)
