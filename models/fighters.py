from db import db

# Admin will add a tournament with player and details.


class FightersLineUpModel(db.Model):

    __tablename__ = "fighters"

    id = db.Column(db.Integer, primary_key=True)
    opp1 = db.Column(db.String(80))
    opp2 = db.Column(db.String(80))
    rd = db.Column(db.String(1))
    winner = db.Column(db.String(80))
    how = db.Column(db.String(80))
    when = db.Column(db.String(1))
    prelim = db.Column(db.String(3))

    tour_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    tournament = db.relationship('TournamentModel',)

    def __init__(self, tour_id, opp1, opp2, rd, winner="-1", how="-1", when="-1", prelim=-1):
        self.tour_id = tour_id
        self.opp1 = opp1
        self.opp2 = opp2
        self.rd = rd
        self.winner = winner
        self.how = how
        self.when = when
        self.prelim = prelim


    def json(self):
        return {
            'id': self.id,
            'tour_id': self.tour_id,
            'opp1': self.opp1,
            'opp2': self.opp2,
            'rd': self.rd,
            'winner': self.winner,
            "how": self.how,
            "when": self.when,
            "prelim": self.prelim
        }

    @classmethod
    def all_fighters(cls):
        return cls.query.all()

    @classmethod
    def all_fighters_specific_tourn(cls, id):
        return cls.query.filter_by(tour_id=id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
