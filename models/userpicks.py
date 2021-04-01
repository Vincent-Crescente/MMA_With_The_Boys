from db import db
from sqlalchemy import and_

class UserPicksModel(db.Model):

    __tablename__ = "userspicks"

    id = db.Column(db.Integer, primary_key=True)
    tournid = db.Column(db.Integer)
    fightid = db.Column(db.Integer)
    pickedwinner = db.Column(db.String(80), nullable=False)
    how = db.Column(db.String(80))
    rd = db.Column(db.String(1))
    points = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates="picks", uselist=False)

    def __init__(self, tournid, fightid, pickedwinner, how, rd, user_id, points=-1):
        self.tournid = tournid
        self.fightid = fightid
        self.pickedwinner = pickedwinner
        self.how = how
        self.rd = rd
        self.user_id = user_id
        self.points = points


    def json(self):
        return {
            "id": self.id,
            "tournid": self.tournid,
            "userid": self.user_id,
            "fightid": self.fightid,
            "pickedwinner": self.pickedwinner,
            "how": self.how,
            "rd": self.rd,
            "points": self.points
        }

    @classmethod
    def all_picks(cls):
        return cls.query.all()

    @classmethod
    def picks_by_tourn_id(cls, tournid):
        return cls.query.filter_by(tournid=tournid).all()

    @classmethod
    def picks_by_user_id(cls, userid):
        return cls.query.filter_by(user_id=userid).all()

    @classmethod
    def picks_for_tourn_user_id(cls, tid, userid):
        return cls.query.filter_by(tournid=tid, user_id=userid).all()

    @classmethod
    def specific_pick_by_tourn_andFight_id(cls, tid, fid):
        return cls.query.filter_by(tournid=tid, fightid=fid).all()

    @classmethod
    def specific_pick_by_tourn_and_user_Fight_id(cls, uid, tid, fid):
        return cls.query.filter_by(user_id=uid, tournid=tid, fightid=fid).all()

    @classmethod
    def specific_pick_by_user_and_fightid(cls, uid, fid):
        return cls.query.filter_by(user_id=uid, fightid=fid).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()







