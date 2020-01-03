from flask import current_app

from app import db
from app.models import Chart, Player, Score
from app.rulings import RANKS

def rank_chart(chart, ssr=None, hash=None):
    if isinstance(chart, str):
        chart = int(chart.split('/')[-1])
    if isinstance(chart, int):
        chart = Chart.query.get(chart)
    if ssr is None:
        ssr = round(chart.sr * 2)
    if hash is None:
        hash = chart.scores[-1].hash
    chart.ssr = ssr
    chart.hash = hash
    chart.ranked = True
    update_all_pb(charts=[chart])
    update_all_player_osmos()
    return chart

def get_scores_query(chart=None, player=None, only_best=True):
    conditions = {}
    if player:
        conditions['player_id'] = player.id
    if only_best:
        conditions['player_best'] = True
    if chart:
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
        Score.points.desc()
    ).first()

def update_pb_for_score(player, score, set_osmos=True):
    current_best = get_pb(player, score.chart)
    print('current best:', current_best)
    if current_best is score or current_best is None or score.points > current_best.points:
        print('new best!')
        if current_best:
            current_best.player_best = False
        score.player_best = True
        if set_osmos:
            if current_best:
                current_best.osmos = None
            score.set_osmos()
        return True
    return False

def update_pb(player, chart, set_osmos=True):
    for score in Score.query.filter(
        Score.chart == chart,
        Score.player == player,
        Score.player_best == True
    ).all():
        score.player_best = False
        if set_osmos:
            score.osmos = None
    current_best = get_pb(player, chart)
    if current_best is None:
        return
    current_best.player_best = True
    if set_osmos:
        current_best.set_osmos()

def update_all_pb(charts=None, set_osmos=True):
    '''
    This is a slow op that should only be used during migrations
    '''
    players = Player.query.all()
    for chart in (charts or Chart.query.all()):
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

def get_player_scores(player, min_accuracy=0):
    if isinstance(min_accuracy, str):
        min_accuracy = RANKS.get(min_accuracy, 0)
    return player.scores.filter(Score.accuracy > min_accuracy)

def big_button():
    update_all_pb()
    players = Player.query.all()
    for player in players:
        update_player_osmos(player)
        update_player_playcount(player)
    db.session.commit()
