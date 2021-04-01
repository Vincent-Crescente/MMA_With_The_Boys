from models.enrolled import EnrolledTournamentModel
from flask_restful import Resource


class Enrolled(Resource):

    def get(self):
        en = EnrolledTournamentModel.all_enrolled()

        enrollmentList = [e1.json() for e1 in en]


        return {"message": enrollmentList}
