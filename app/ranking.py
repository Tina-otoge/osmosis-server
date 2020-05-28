from flask import current_app

from app import db
from app.models import Chart, Player, Score
from app.osu import osuAPI
from app.rulings import RANKS
from app.discord import hook


def rank_chart(chart, ssr=None, hash=None):
    if isinstance(chart, str):
        chart = int(chart.split('/')[-1])
    if isinstance(chart, int):
        id = chart
        chart = Chart.query.get(chart)
    if chart is None:
        print('getting chart info from osu! servers')
        data = osuAPI.beatmap(id)
        if data is None:
            return None
        hash = data['hash']
        chart = Chart(data)
        db.session.add(chart)
        db.session.commit()
    elif hash is None and chart.scores.filter(Score.hash != None).count() != 0:
        print('missing hash, getting chart info from osu! servers')
        data = osuAPI.beatmap(id)
        hash = data['hash']
    if ssr is None:
        if chart.sr < 5:
            ssr = round(chart.sr * 2) * 2 / 4
        else:
            ssr = round(chart.sr * 4)
    if hash is None:
        hash = chart.scores[-1].hash
    chart.ssr = ssr
    chart.hash = hash
    chart.ranked = True
    update_all_pb(charts=[chart])
    update_all_player_osmos()
    db.session.commit()
    if current_app.config.get('DISCORD_NOTIFICATIONS'):
        hook('❗ New ranked map!\n{}/charts/{}'.format(
            current_app.config.get('WEBSITE'),
            chart.id
        ), 'charts')
    return chart


def rescale_charts(scale):
    charts = Chart.query.filter_by(ranked=True)
    for chart in charts:
        chart.ssr *= scale
    db.session.commit()


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
    return get_scores_query(chart=chart, player=player, only_best=False).order_by(
        Score.accuracy.desc()
    ).first()


def update_pb_for_score(player, score, set_osmos=True):
    current_best = get_scores_query(chart=score.chart, player=player).first()
    print('current best:', current_best)
    if current_app.config.get('DISCORD_NOTIFICATIONS'):
        absolute_best = get_scores_query(chart=score.chart).first()
        if absolute_best is None or score.accuracy > absolute_best.accuracy:
            print('new server best!')
            if (score.chart.ranked):
                extra_text = ' on a **ranked chart**'
            elif (score.chart.hash is not None):
                extra_text = ' on a **verified chart**'
            else:
                extra_text = ''
            hook('🥇 New server best{}!\n{}/share/{}'.format(
                extra_text,
                current_app.config.get('WEBSITE'),
                score.id
            ), 'scores')
    if current_best is None or score.accuracy > current_best.accuracy:
        print('new personal best!')
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
        Score.player_best
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
        Score.player_best,
        Chart.ranked,
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
