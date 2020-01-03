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

@app.route('/share/<id>')
def share(id):
    score = Score.query.get_or_404(id)
    title = '{} [{}] ({}) {}⭐'.format(
        score.chart.display_name(),
        score.chart.difficulty_name,
        score.chart.mode,
        score.chart.display_difficulty(),
    )
    description = '\n'.join(filter(lambda x: x, [
        'Played by {}\non {}\n'.format(score.player.username, score.display_time()),
        'Mapset by: {}'.format(score.creator_name),
        'Artist: {}\n'.format(score.chart.display_artist()),
        'Accuracy: {} ({})'.format(score.display_accuracy(), score.display_rank()),
        'Judges: {}'.format(score.display_judges()),
        ' | '.join(['+{}'.format(mod['acronym']) for mod in score.get_mods()]) or None,
        ' | '.join(score.flairs) or None,
    ]))
    meta = {
        'title': title,
        'image': score.chart.get_osu_thumbnail_url(),
        'description': description,
    }
    return chart(score.chart.id, highlight=score, meta=meta)


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
    rankeds = Chart.query.filter(Chart.ranked == True).order_by(
        Chart.name_romanized.asc(),
        Chart.ssr.desc(),
        Chart.difficulty_name.asc(),
    )
    return render_template(
        'charts.html',
        title='Ranked charts',
        **build_pager('charts', rankeds, per_page=50)
    )

@app.route('/charts/<id>')
def chart(id, highlight=None, meta={}):
    chart = Chart.query.get_or_404(id)
    scores_query = get_scores_query(chart, only_best=True)
    scores = (scores_query
        .order_by(Score.points.desc())
    )
    return render_template(
        'chart.html',
        title=meta.get('title', chart.display_short()),
        chart=chart,
        meta=meta,
        score=highlight,
        **build_pager('chart', scores, per_page=50, id=id)
    )

@app.route('/players/<id>')
def player(id):
    player = Player.query.get_or_404(id)
    top = Score.query.filter(Score.player == player, Score.osmos > 0).order_by(Score.osmos.desc()).limit(20)
    scores = Score.query.filter_by(player=player).order_by(Score.achieved_at.desc())
    return render_template(
        'player.html',
        player=player,
        top=top,
        **build_pager('player', scores, per_page=20, id=id)
    )
