import json


class AttrDict(dict):
    def __getattr__(self, key):
        try:
            value = self.get(key)
            if isinstance(value, dict):
                value = AttrDict(value)
            return value
        except AttributeError:
            return None


def process_lazer_payload(data):
    with open('lazer-request.json', 'w') as f:
        json.dump(data, f, indent=2)

    data = AttrDict(data)
    user = AttrDict(data.user)
    map = AttrDict(data.Beatmap)

    result = {
        'player': {
            'id': user.id,
            'name': user.username,
            'join_data': user.join_date,
            'avatar': user.avatar_url,
            'cover': user.cover_url,
            'country': user.country.name,
            'country_code': user.country.code,
            'twitter': user.twitter,
            'discord': user.discord,
            'website': user.website,
        },
        'score': {
            'perfect': data.statistics.Perfect,
            'great': data.statistics.Great,
            'good': data.statistics.Good,
            'ok': data.statistics.Ok,
            'meh': data.statistics.Meh,
            'miss': data.statistics.Miss,
            'accuracy': data.accuracy,
            'max_combo': data.accuracy,
            'mods': data.mods,
            'mode': user.Activity.Ruleset.ShortName,
            'client': 'osu! lazer',
        },
        'chart': {
            'chart_id': map.id,
            'set_id': map.BeatmapSet.OnlineBeatmapSetID,
            'mode': map.Ruleset.ShortName,
            'duration': map.Length,
            'bpm': map.BPM,
            'song_name': map.Metadata.title_unicode,
            'romanized_name': map.Metadata.Title,
            'artist_name': map.Metadata.artist_unicode,
            'romanized_artist': map.Metadata.Artist,
            'difficulty_name': map.Version,
            'set_creator_name': map.Metadata.creator,
            'sr': map.difficulty_rating,
            'hp': map.BaseDifficulty.DrainRate,
            'cs': map.BaseDifficulty.CircleSize,
            'od': map.BaseDifficulty.OverallDifficulty,
            'ar': map.BaseDifficulty.ApproachRate,
            'hash': map.file_md5,
        },
    }
    with open('lazer-request-filtered.json', 'w') as f:
        json.dump(result, f, indent=2)
    return result
