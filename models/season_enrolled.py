from db import db
# Keeps track of who is enrolled in which tournament.

class SeasonEnrolledModel(db.Model):

    __tablename__ = 'season_enrolled'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    season_id = db.Column(db.Integer)
    points = db.Column(db.Integer)

    def __init__(self, user_id, season_id, points=-1):
        self.user_id = user_id
        self.season_id = season_id
        self.points = points

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'season_id': self.season_id,
            'points': self.points
        }

    @classmethod
    def all_enrolled(cls):
        return cls.query.all()

    @classmethod
    def all_enrolled_by_user(cls, uid):
        return cls.query.filter_by(user_id=uid).all()

    @classmethod
    def specific_season_by_user(cls, uid, sid):
        return cls.query.filter_by(user_id=uid, season_id=sid).first()

    @classmethod
    def all_seasons_user_enrolled_in(cls, userid):
        return cls.query.filter_by(user_id=userid).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
