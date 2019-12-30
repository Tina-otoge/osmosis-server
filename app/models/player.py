from datetime import datetime

from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    osu_join_date = db.Column(db.DateTime)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_url = db.Column(db.String(512))
    cover_url = db.Column(db.String(512))
    country = db.Column(db.String(128))
    country_code = db.Column(db.String(2))
    twitter = db.Column(db.String(32))
    discord = db.Column(db.String(32))
    website = db.Column(db.String(512))

    osmos = db.Column(db.Integer, default=0)
    playcount = db.Column(db.Integer, default=0)

    scores = db.relationship('Score', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<Player {}>'.format(self.username)

    def __str__(self):
        return self.username

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

