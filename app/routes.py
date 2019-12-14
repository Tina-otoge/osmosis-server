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
            print('malformed score payload', 'data:', data, sep='\n')
            raise e
        return 'OK'

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/scores')
def scores():
    return 'TODO'

@app.route('/players')
def players():
    players = Player.query.all()
    return render_template('players.html', players=players)

@app.route('/charts')
def charts():
    return 'TODO'

@app.route('/charts/<id>')
def chart(id):
    chart = Chart.query.get_or_404(id)
    scores = (Score.query.filter_by(chart_id=chart.id)
        .order_by(Score.sortable_points.desc())
        .limit(app.config['BOARD_SIZE'])
        .all()
    )
    return render_template('chart.html', chart=chart, scores=scores)

@app.route('/players/<id>')
def player(id):
    player = Player.query.get_or_404(id)
    scores = Score.query.filter_by(player=player).order_by(Score.achieved_at.desc()).all()
    return render_template('player.html', player=player, scores=scores)
