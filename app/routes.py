from flask import request, render_template

from app import app, db
from app.models import Chart, Player, Score

try:
    from secret import dumb_decryption
except:
    print('Score decrypter not found, will not be able to parse scores')
    dumb_decryption = lambda x: x

@app.route('/')
@app.route('/index')
def index():
    latest_scores = Score.query.order_by(Score.achieved_at.desc()).limit(10)
    return render_template('home.html', scores=latest_scores)

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
            score.player_id = player.id
            score.chart_id = chart.id
            score.version = 1
            db.session.add_all([player, chart, score])
            db.session.commit()
            print('pushed to db!')
        except Exception as e:
            print('malformed score payload')
            print('data:', data, sep='\n')
            print(e)
        return 'OK'

@app.route('/scores')
def scores():
    return 'TODO'

@app.route('/players')
def players():
    return 'TODO'

@app.route('/charts')
def charts():
    return 'TODO'
