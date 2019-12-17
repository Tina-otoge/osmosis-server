from flask import render_template, request

from app import app
from app.models import Score, Chart, Player

@app.route('/index')
@app.route('/')
def index():
    latest_scores = (Score.query
        .order_by(Score.achieved_at.desc())
        .limit(10)
    )
    return render_template('home.html', scores=latest_scores)

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
    scores_query = chart.get_scores_query()
    scores = (scores_query
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
