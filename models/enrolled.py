from db import db
# Keeps track of who is enrolled in which tournament.

class EnrolledTournamentModel(db.Model):

    __tablename__ = 'enrolled'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    tourn_id = db.Column(db.Integer)
    points = db.Column(db.Integer)

    def __init__(self, user_id, tourn_id, points=-1):
        self.user_id = user_id
        self.tourn_id = tourn_id
        self.points = points

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tourn_id': self.tourn_id,
            'points': self.points
        }

    @classmethod
    def all_enrolled(cls):
        return cls.query.all()

    @classmethod
    def all_enrolled_in_tourn_id(cls, tid):
        return cls.query.filter_by(tourn_id=tid).all()

    @classmethod
    def all_torns_user_enrolled_in(cls, userid):
        return cls.query.filter_by(user_id=userid).all()

    @classmethod
    def specific_torn_user_enrolled_in(cls, userid, tid):
        return cls.query.filter_by(user_id=userid, tourn_id=tid).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
