import click

from app import db
from app.ranking import rank_chart, big_button

def register(app):
    @app.cli.command()
    @click.argument('chart')
    @click.option('--ssr', default=None, type=float)
    @click.option('--hash', default=None)
    def rank(chart, ssr=None, hash=None):
        if ssr:
            ssr = round(ssr * 2)
        chart = rank_chart(chart, ssr=ssr, hash=hash)
        db.session.commit()
        print('ranked', chart)

    @app.cli.command()
    def bigbutton():
        big_button()
