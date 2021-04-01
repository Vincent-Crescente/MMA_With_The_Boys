from db import db


class UserModel(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(110))
    totalPoints = db.Column(db.Integer)

    picks = db.relationship('UserPicksModel', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.totalPoints = 0

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'total_points': self.totalPoints,
            'picks': [pick.json() for pick in self.picks.all()]
        }


    def json_points(self):
        return {
            'username': self.username,
            'Total Points': self.totalPoints
        }

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()






