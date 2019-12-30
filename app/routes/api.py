from datetime import datetime

from flask import jsonify, request

from app import app, db
from app.models import Player, Chart, Score
from app.ranking import update_pb, update_player_osmos
from . import dumb_decryption

@app.route('/versions')
def versions():
    return jsonify({
        'osu': 8,
        'pusher': 4,
    })


@app.route('/score', methods=['POST'])
def score():
    if request.data:
        print('got a score!!')
        data = dumb_decryption(request.data)
        try:
            player = Player.query.get(data['player']['id'])
            if not player:
                player = Player(data['player'])
            else:
                player.update_fields(data['player'])
            chart = Chart.query.get(data['chart']['chart_id'])
            if not chart:
                chart = Chart(data['chart'])
            else:
                chart.update_fields(data['chart'])
            data['score']['hash'] = data['chart'].get('hash')
            score = Score(data['score'], chart)
            score.achieved_at = datetime.utcnow()
            score.player_id = player.id
            score.chart_id = chart.id
            score.version = 5
            if not score.is_supported(chart):
                db.session.rollback()
                print('score ignored because not supported')
                return 'Not OK'
            db.session.add_all([player, chart, score])
            db.session.commit()
            print('pushed to db! ({} played by {})'.format(
                chart.name, player.username
            ))
            print('updating pb if needed')
            if update_pb(player, chart, score=score, set_osmos=True):
                update_player_osmos(player)
            player.playcount += 1
            db.session.commit()
            print('set osmos')
        except Exception as e:
            db.session.rollback()
            print('malformed score payload', 'data:', data, sep='\n')
            raise e
        return 'OK'

