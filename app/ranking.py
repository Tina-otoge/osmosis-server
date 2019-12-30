from flask import current_app

from app import db
from app.models import Chart, Player, Score

def get_scores_query(chart, player=None, only_best=True):
    conditions = {}
    if player:
        conditions['player_id'] = player.id
    if only_best:
        conditions['player_best'] = True
    if chart.hash:
        conditions['hash'] = chart.hash
    else:
        conditions['chart_id'] = chart.id
    return Score.query.filter_by(**conditions)

def get_pb(player, chart):
    return Score.query.filter(
        Score.chart == chart,
        Score.player == player
    ).order_by(
        Score.sortable_points.desc()
    ).first()

def update_pb(player, chart, score=None, set_osmos=False):
    current_best = get_pb(player, chart)
    if score:
        if current_best is None or score.points > current_best.points:
            current_best.player_best = False
            score.player_best = True
            if set_osmos:
                current_best.osmos = None
                score.set_osmos()
        return
    for score in Score.query.filter(
        Score.chart == chart,
        Score.player == player,
        Score.player_best == True
    ).all():
        score.player_best = False
        if set_osmos:
            score.osmos = None
    if current_best is None:
        return
    current_best.player_best = True
    if set_osmos:
        current_best.set_osmos()

def update_all_pb(set_osmos=False):
    '''
    This is a slow op that should only be used during migrations
    '''
    players = Player.query.all()
    for chart in Chart.query.all():
        for player in players:
            update_pb(player, chart, set_osmos=set_osmos)

def update_player_osmos(player):
    scores = Score.query.join(Score.chart).filter(
        Score.player == player,
        Score.player_best == True,
        Chart.ranked == True,
        Score.osmos > 0
    ).limit(current_app.config.get('TOP_OSMOS', 20)).all()
    result = 0
    for score in scores:
        result += score.osmos
    player.osmos = result

def update_all_player_osmos():
    for player in Player.query.all():
        update_player_osmos(player)

def update_player_playcount(player):
    player.playcount = player.scores.count()

def update_all_player_playcount():
    for player in Player.query.all():
        update_player_playcount(player)

def big_button():
    players = Player.query.all()
    for player in players:
        update_player_osmos(player)
        update_player_playcount(player)
    update_all_pb()
    db.session.commit()
