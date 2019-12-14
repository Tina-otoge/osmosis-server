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
print(app.config.get('SQLALCHEMY_DATABASE_URI'))

db.init_app(app)
migrate.init_app(app, db)
moment.init_app(app)


from . import models, routes
