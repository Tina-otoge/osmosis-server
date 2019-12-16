from datetime import datetime

from flask import jsonify, request

from app import app, db
from app.models import Player, Chart, Score
from . import dumb_decryption

@app.route('/versions')
def versions():
    return jsonify({
        'osu': 2,
        'pusher': 3,
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
            score = Score(data['score'])
            score.achieved_at = datetime.utcnow()
            score.player_id = player.id
            score.chart_id = chart.id
            score.version = 2
            if not score.is_supported(chart):
                db.session.rollback()
                print('score ignored because not supported')
                return 'Not OK'
            db.session.add_all([player, chart, score])
            db.session.commit()
            print('pushed to db! ({} played by {})'.format(
                chart.name, player.username
            ))
        except Exception as e:
            db.session.rollback()
            print('malformed score payload', 'data:', data, sep='\n')
            raise e
        return 'OK'

