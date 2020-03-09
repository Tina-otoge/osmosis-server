import requests
from flask import current_app


def get_legacy_mode(id):
    return {
        0: 'osu',
        1: 'taiko',
        2: 'catch',
        3: 'mania',
    }.get(id)


class osuAPI:
    @staticmethod
    def get_key():
        return current_app.config.get('OSU_API_KEY')

    @staticmethod
    def api_call(endpoint, args={}):
        if 'k' not in args:
            args['k'] = osuAPI.get_key()
        return requests.get('https://osu.ppy.sh/api/' + endpoint, args).json()

    @staticmethod
    def beatmap(id):
        result = osuAPI.api_call('get_beatmaps', {'b': id})
        if result is None:
            return None
        if result.get('error'):
            print('An error occured:', result['error'])
            return None
        result = result[0]
        return {
            'chart_id': int(result['beatmap_id']),
            'set_id': int(result['beatmapset_id']),
            'mode': get_legacy_mode(int(result['mode'])),
            'duration': float(result['total_length']),
            'bpm': float(result['bpm']),
            'song_name': result['title_unicode'],
            'romanized_name': result['title'],
            'artist_name': result['artist_unicode'],
            'romanized_artist': result['artist'],
            'difficulty_name': result['version'],
            'hp': float(result['diff_drain']),
            'cs': float(result['diff_size']),
            'od': float(result['diff_overall']),
            'ar': float(result['diff_approach']),
            'sr': float(result['difficultyrating']),
            'set_creator_name': result['creator'],
        }
