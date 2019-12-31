from flask import render_template, request

from app import app
from app.models import Score, Chart, Player
from app.ranking import get_scores_query, get_player_scores
from . import build_pager

@app.route('/index')
@app.route('/')
def index():
    latest_scores = (Score.query
        .order_by(Score.achieved_at.desc())
    )
    return render_template(
        'home.html',
        **build_pager('index', latest_scores, per_page=20)
    )

@app.route('/scores')
def scores():
    return 'TODO'

@app.route('/players')
def players():
    players = Player.query.order_by(Player.osmos.desc())
    return render_template(
        'players.html',
        title='Players list',
        **build_pager('players', players, per_page=50)
    )

@app.route('/charts')
def charts():
    return 'TODO'

@app.route('/charts/<id>')
def chart(id):
    chart = Chart.query.get_or_404(id)
    print(chart)
    scores_query = get_scores_query(chart, only_best=True)
    print(scores_query)
    scores = (scores_query
        .order_by(Score.points.desc())
    )
    return render_template(
        'chart.html',
        title=chart.display_short(),
        chart=chart,
        **build_pager('chart', scores, per_page=50, id=id)
    )

@app.route('/players/<id>')
def player(id):
    player = Player.query.get_or_404(id)
    scores = Score.query.filter_by(player=player).order_by(Score.achieved_at.desc())
    return render_template(
        'player.html',
        player=player,
        **build_pager('player', scores, per_page=20, id=id)
    )
