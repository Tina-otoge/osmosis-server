import click

from app import db
from app.ranking import rank_chart, big_button, rescale_charts


def register(app):
    @app.cli.command()
    @click.argument('chart')
    @click.option('--ssr', default=None, type=float)
    @click.option('--hash', default=None)
    def rank(chart, ssr=None, hash=None):
        if ssr:
            ssr = round(ssr * 4)
        chart = rank_chart(chart, ssr=ssr, hash=hash)
        db.session.commit()
        print('ranked', chart)

    @app.cli.command()
    def bigbutton():
        big_button()

    @app.cli.command()
    @click.argument('scale', type=int)
    def rescale(scale):
        rescale_charts(scale)
