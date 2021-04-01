from models.tournament import TournamentModel
from flask_restful import Resource


class FightersLineUp(Resource):

    def get(self, tour_id):
        user = TournamentModel.get_tourn_by_id(tour_id)
        if user:
            return user.json()
        else:
            return {"message": "Dne"}

