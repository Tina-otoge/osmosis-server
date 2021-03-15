class Score:
    def __init__(self):
        self.great = None
        self.good = None
        self.meh = None
        self.miss = None
        self.rank = None
        self.max_combo = None
        self.accuracy = None
        self.mods = []
        self.mode = None
        self.achieved_at = None
        self.client = None


class Chart:
    def __init__(self):
        self.chart_id = None
        self.mode = None
        self.duration = None
        self.bpm = None
        self.song_name = None
        self.romanized_name = None
        self.artist_name = None
        self.romanized_artist = None
        self.difficulty_name = None
        self.set_creator_name = None
        self.hp = None
        self.cs = None
        self.od = None
        self.ar = None
        self.sr = None
        self.hash = None


class Player:
    def __init__(self):
        self.id = None
        self.name = None
        self.join_date = None
        self.avatar = None
        self.cover = None
        self.country = None
        self.country_code = None
        self.twitter = None
        self.discord = None
        self.website = None


def process_lazer_payload(data):
    score = Score()
    chart = Chart()
    player = Player()

    user = data['user']
    player.id = user['id']
    player.name = user['username']
    player.join_date = user['join_date']
    player.avatar = user['avatar_url']
    player.cover = user['cover_url']
    player.country = user['country']['name']
    player.country_code = user['country']['code']
    player.twitter = user['twitter']
    player.discord = user['discord']
    player.website = user['website']

    score.perfect = data['statistics'].get('Perfect')
    score.great = data['statistics'].get('Great')
    score.good = data['statistics'].get('Good')
    score.ok = data['statistics'].get('Ok')
    score.meh = data['statistics'].get('Meh')
    score.miss = data['statistics'].get('Miss')
    score.rank = data['rank']
    score.accuracy = data['accuracy']
    score.max_combo = data['max_combo']
    score.mods = data['mods']
    score.mode = data['user']['Activity']['Ruleset']['ShortName']
    score.client = 'osu! lazer'

    map = data['user']['Activity']['Beatmap']
    chart.chart_id = map['id']
    chart.set_id = map['BeatmapSet'].get('OnlineBeatmapSetID')
    chart.mode = map['Ruleset']['ShortName']
    chart.duration = map['Length']
    chart.bpm = map['BPM']
    chart.song_name = map['Metadata']['TitleUnicode']
    chart.romanized_name = map['Metadata']['Title']
    chart.artist_name = map['Metadata']['ArtistUnicode']
    chart.romanized_artist = map['Metadata']['Artist']
    chart.difficulty_name = map['Version']
    chart.set_creator_name = map['Metadata']['creator']
    chart.hp = map['BaseDifficulty']['DrainRate']
    chart.cs = map['BaseDifficulty']['CircleSize']
    chart.od = map['BaseDifficulty']['OverallDifficulty']
    chart.ar = map['BaseDifficulty']['ApproachRate']
    chart.sr = map['difficulty_rating']
    chart.hash = map['file_md5']

    return {
        'score': score.__dict__,
        'chart': chart.__dict__,
        'player': player.__dict__,
    }
