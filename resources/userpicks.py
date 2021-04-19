from models.user import UserModel
from models.tournament import TournamentModel
from flask_restful import Resource
from flask import render_template, session, make_response


class UserPicks(Resource):

    def get(self, id):
        
        if 'user' in session:

            user = UserModel.find_by_username((session['user']))
            data = UserModel.find_by_id(user.id)
            tournData = TournamentModel.get_tourn_by_id(id)

            d1 = data.json()

            filtered_picks_by_tourn = []

            for d in d1['picks']:
                if d['tournid'] == id:
                    filtered_picks_by_tourn.append(d)

            sorted_picks_by_id = sorted(filtered_picks_by_tourn, key=lambda k: k['id'])

            if tournData:
                if data:
                    return make_response(render_template("viewpicks.html", data=sorted_picks_by_id, user=user, tname=tournData.name, t_id=tournData.id, tournData=tournData), 200)
                else:
                    return {"message": "User does not exist"}
            else:
                return {"message": "Tournament doesn't exist."}
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)