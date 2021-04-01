from db import db
from models.fighters import FightersLineUpModel
from models.season import SeasonModel
# Keeps track of tournaments created.

class TournamentModel(db.Model):

    __tablename__ = 'tournaments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    active = db.Column(db.Boolean)
    started = db.Column(db.Boolean)

    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    season = db.relationship('SeasonModel')

    fighterList = db.relationship('FightersLineUpModel', lazy='dynamic')

    def __init__(self, name, season_id):
        self.name = name
        self.season_id = season_id
        self.active = True
        self.started = False

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'active': self.active,
            'started':self.started,
            'season_id': self.season_id,
            'season_name': self.season.name,
            'fighters': [fighter.json() for fighter in self.fighterList.all()]
        }

    @classmethod
    def all_tournaments(cls):
        return cls.query.all()

    @classmethod
    def get_tourn_by_season_id(cls, sid):
        return cls.query.filter_by(season_id=sid).first()

    @classmethod
    def get_tourn_by_season_name(cls, sname):
        return cls.query.filter_by(name=sname).first()

    @classmethod
    def get_tourn_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_tourn_by_id(cls, id1):
        return cls.query.filter_by(id=id1).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
