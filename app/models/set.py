from app import db

class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    charts = db.relationship('Chart', backref='set', lazy='dynamic')
