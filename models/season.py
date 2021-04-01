from db import db


class SeasonModel(db.Model):

    __tablename__ = 'season'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    active = db.Column(db.Boolean)
    admin = db.Column(db.String(80))

    eventList = db.relationship('TournamentModel', lazy='dynamic')

    def __init__(self, season_name, admin):
            self.name = season_name
            self.admin = admin
            self.active = True

    def json(self):
        return {
            "name": self.name,
            "active": self.active,
            "admin": self.admin,
            "season_id": self.id,
            "events": [events.json() for events in self.eventList.all()]
        }

    @classmethod
    def all_seasons(cls):
        return cls.query.all()

    @classmethod
    def get_season_byid(cls, id1):
        return cls.query.filter_by(id=id1).first()

    @classmethod
    def get_seasons_by_admin(cls, admin_name):
        return cls.query.filter_by(admin=admin_name).all()

    @classmethod
    def get_season_byname(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
