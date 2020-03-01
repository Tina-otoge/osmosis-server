from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
moment = Moment()

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
moment.init_app(app)


from . import models, routes, cli

cli.register(app)

from app.models import Chart, Player, Score


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Chart': Chart,
        'Player': Player,
        'Score': Score
    }
