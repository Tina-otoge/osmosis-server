from datetime import datetime
import json
from urllib.parse import urlencode

from sqlalchemy.ext.hybrid import hybrid_property

from app import app, db
from app.rulings import Judge, MAX_JUDGE, MODS_WHITELIST, calculate_osmos, get_rank
from . import DATETIME_BACK, DATETIME_FRONT


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accuracy = db.Column(db.Float, default=0.)
    perfect = db.Column(db.Integer, default=0)
    ok = db.Column(db.Integer, default=0)
    great = db.Column(db.Integer, default=0)
    good = db.Column(db.Integer, default=0)
    meh = db.Column(db.Integer, default=0)
    miss = db.Column(db.Integer, default=0)
    max_combo = db.Column(db.Integer)
    mods = db.Column(db.String(128))
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.Column(db.String(128))
    mode = db.Column(db.String(128), default='osu')
    hash = db.Column(db.String(64))

    osmos = db.Column(db.Integer)
    player_best = db.Column(db.Boolean, default=False)

    chart_id = db.Column(db.Integer, db.ForeignKey('chart.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    '''
    Score versions:
    1: initial, mod format=[MOD:[, ...]], ie: DT:HR:
    2: new mod format: [[key=value [, ...]]\n[, ...]] ie: acronym=DT rate=3\nacronym=HR
    3: hash
    4: mod translation
    5: osmos and pb
    6: client-side accuracy
    '''
    version = db.Column(db.Integer)

    def __repr__(self):
        return '<Score {0.id}: {1} on {2} by {3}>'.format(
            self, self.display_accuracy(), self.chart.display_short(), str(self.player)
        )

    @hybrid_property
    def max_notes(self):
        return self.perfect + self.great + self.good + self.ok + self.meh + self.miss

    @max_notes.expression
    def max_notes(cls):
        return cls.perfect + cls.great + cls.good + cls.ok + cls.meh + cls.miss

    @hybrid_property
    def points(self):
        return (
            self.perfect * Judge.PERFECT +
            self.great * Judge.GREAT +
            self.good * Judge.GOOD +
            self.ok * Judge.OK +
            self.meh * Judge.MEH
        ) / self.max_notes

    @points.expression
    def points(cls):
        return (
            cls.perfect * Judge.PERFECT +
            cls.great * Judge.GREAT +
            cls.good * Judge.GOOD +
            cls.ok * Judge.OK +
            cls.meh * Judge.MEH
        ) / cls.max_notes

    def get_absolute_accuracy(self):
        return self.points / self.max_points

    def get_slider_amount(self):
        return self.get_absolute_accuracy() - self.accuracy

    @hybrid_property
    def flairs(self):
        result = []
        if self.accuracy == 1:
            result.append('perfect')
        elif self.miss == 0:
            result.append('full combo')
        elif self.miss < 4:
            result.append('almost fc')
        if self.good == self.max_notes:
            result.append('only GOODs')
        return result

    @hybrid_property
    def max_points(self):
        return MAX_JUDGE.get(self.mode, Judge.GREAT)

    @max_points.expression
    def max_points(cls):
        return cls.max_notes * MAX_JUDGE.get(cls.mode, Judge.GREAT)

    def is_supported(self):
        if not self.chart:
            print('no chart')
            return False
        if self.is_convert():
            print('is convert')
            return False
        return True

    def is_convert(self):
        return self.mode != self.chart.mode

    def is_rankable(self):
        mods_used = [x['acronym'] for x in self.get_mods()]
        for mod in mods_used:
            if mod not in MODS_WHITELIST:
                return False
        return True

    def get_osmos(self, osu=False, max=False):
        mods = self.get_mods() if not max else []
        if self.chart.ssr is None and osu:
            difficulty = self.chart.sr
        else:
            difficulty = self.chart.ssr / 4
        accuracy = self.accuracy if not max else 1
        return calculate_osmos(accuracy, difficulty, mods)

    def set_osmos(self):
        if not self.chart or not self.chart.ranked or not self.chart.ssr or self.hash != self.chart.hash or not self.is_rankable():
            self.osmos = None
        else:
            self.osmos = self.get_osmos()

    def display_accuracy(self, suffix='%'):
        accuracy = self.accuracy
        if accuracy == 1:
            return '100' + suffix
        return ('%.2f' % (accuracy * 100)) + suffix

    def display_judges(self):
        modes_judges = {
            'osu': [self.great, self.ok, self.meh, self.miss],
            'taiko': [self.great, self.good, self.miss],
            'fruits': [self.perfect, self.miss],
            'mania': [self.perfect, self.great, self.good, self.ok, self.meh, self.miss]
        }
        return ' | '.join(map(str, modes_judges[self.mode]))

    def display_mod(self, mod):
        infos = []
        for key, value in mod.items():
            if key != 'acronym':
                infos.append('{}: {}'.format(key, value))
        return '<span data-toggle="tooltip" data-html="true" title="{}">{}</span>'.format(
            '\n'.join(infos), mod['acronym']
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
            result = []
            for mod in mods:
                mod_info = {}
                for pair in mod.split(' '):
                    parts = pair.split('=')
                    mod_info[parts[0]] = parts[1] if len(parts) > 1 else None
                result.append(mod_info)
            return result
        return []

    def display_rank(self):
        return get_rank(self.accuracy)

    def display_time(self):
        return self.achieved_at.strftime(DATETIME_FRONT)

    def get_cbcard_link(self):
        data = {
            'game': self.mode + '!',
            'copyright': 'osmosis, accuracy based osu!',

            'username': self.player.username,
            'avatar': self.player.avatar_url,

            'title': self.chart.display_name(prefer_romanzied=True),
            'artist': self.chart.display_artist(prefer_romanzied=True),
            'bpm': self.chart.bpm,
            'jacket': self.chart.get_osu_thumbnail_url(),
            'level': self.chart.display_difficulty(),
            'difficulty': self.chart.difficulty_name,
            'creator': self.chart.creator_name,

            'mods': json.dumps([mod['acronym'] for mod in self.get_mods()]),
            'max_combo': self.max_combo,
            'score': self.display_accuracy(),
            'grade': self.display_rank(),

            'pp': self.osmos or 'unranked',
            'judges': json.dumps({
                'GREAT': self.great,
                'OK': self.ok,
                'MEH': self.meh,
                'MISS': self.miss,
            }),
            'date': self.achieved_at,

            'class': json.dumps({'pp_name': 'osmos', 'level_suffix': '⭐'}),
            'settings': json.dumps({'preset': 'osu!', 'auto_fc': True}),
        }
        return app.config.get('COFFEEBREAK_URL', 'https://coffee.tina.moe') + '/api/card.jpg?' + urlencode(data)


    def translate_mods(self, raw_score):
        chart = self.chart
        for mod in raw_score['mods']:
            if (
                mod['acronym'] == 'AR' and
                mod['ApproachRate'] == chart.ar
            ) or (
                mod['acronym'] == 'DA' and
                mod.get('ApproachRate') == chart.ar and
                mod.get('CircleSize') == chart.cs and
                mod.get('DrainRate') == chart.hp and
                mod.get('OverallDifficulty') == chart.od
            ):
                raw_score['mods'].remove(mod)
            elif (
                mod['acronym'] == 'DA' and
                mod.get('ApproachRate') and
                mod['ApproachRate'] != chart.ar and
                mod.get('CircleSize') == chart.cs and
                mod.get('DrainRate') == chart.hp and
                mod.get('OverallDifficulty') == chart.od
            ):
                raw_score['mods'].append({
                    'acronym': 'AR',
                    'ApproachRate': mod['ApproachRate'],
                })
                raw_score['mods'].remove(mod)
        return raw_score['mods']

    def update_fields(self, data):
        if data.get('accuracy'):
            self.accuracy = data['accuracy']
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
        if data.get('max_combo'):
            self.max_combo = data['max_combo']
        if data.get('mods'):
            if isinstance(data['mods'], str) and ':' in data['mods']:
                self.mods = '\n'.join([
                    'acronym={}'.format(x) for x in data['mods'][:-1].split(':')
                ])
            else:
                mods = self.translate_mods(data)
                self.mods = '\n'.join([' '.join(['{}={}'.format(key, value)
                    for key, value in mod.items()])
                          for mod in mods])
        if data.get('mode'):
            self.mode = data['mode']
        if data.get('achieved_at'):
            self.achieved_at = datetime.strptime(
                data['achieved_at'].split(',')[0], DATETIME_BACK
            )
        if data.get('client'):
            self.client = data['client']
        if data.get('hash'):
            self.hash = data['hash']

    def __init__(self, data={}, chart=None):
        self.chart = chart
        self.update_fields(data)

