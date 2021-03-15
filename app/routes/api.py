from datetime import datetime
import logging
from flask import jsonify, request

from app import app, db
from app.models import Player, Chart, Score
from app.ranking import update_pb_for_score, update_player_osmos
from app.lazer import process_lazer_payload
from . import dumb_decryption


@app.route('/versions')
def versions():
    return jsonify({
        'osu': app.config.get('REQUIRED_OSU_VERSION', 0),
        'pusher': app.config.get('REQUIRED_PUSHER_VERSION', 0),
    })


@app.route('/lazer', methods=['POST'])
def lazer_score():
    return score(process_lazer_payload(request.json), decrypt=False)

@app.route('/score', methods=['POST'])
def score(data=None, decrypt=True):
    data = data or request.data
    if not data:
        logging.warning('Empty request')
        return 'No data', 400
    print('got a score!!')
    print(data)
    data = dumb_decryption(data) if decrypt else data
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
        score.player = player
        score.version = 6
        if not score.is_supported():
            db.session.rollback()
            print('score ignored because not supported')
            return 'Not OK'
        db.session.add_all([player, chart, score])
        db.session.commit()
        print('pushed to db! ({} played by {})'.format(
            chart.name, player.username
        ))
        score.set_osmos()
        print('osmos set')
        print('updating pb if needed')
        if update_pb_for_score(player, score):
            print('updated pb returned true')
            update_player_osmos(player)
        player.playcount += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Malformed score payload: \n{data}')
        raise logging.warning(e, exc_info=True)
    return 'OK'
