from flask_restful import Resource, request
from flask import session, make_response, render_template

from models.tournament import TournamentModel
from models.enrolled import EnrolledTournamentModel

from models.user import UserModel
from models.userpicks import UserPicksModel


class DraftPage(Resource):

    def get(self, tid):

        if "user" in session:

            tourn_info = TournamentModel.get_tourn_by_id(tid)

            user = UserModel.find_by_username((session['user']))

            pick = UserPicksModel.picks_for_tourn_user_id(tid, session['id'])

            if pick:
                picks_already_made = [p1.json() for p1 in pick]
            else:
                picks_already_made = []

            if tourn_info:
                if tourn_info.started:

                    tourn_info1 = tourn_info.json()
                    fighter_list = tourn_info1['fighters']

                    return make_response(render_template("draftpage-started.html", userdata=user, fighterList=fighter_list, season_id=tourn_info1['season_id'], tourn_id=tourn_info1['id'], picks_already_made=picks_already_made, started=1), 200)

                else:

                    tourn_info1 = tourn_info.json()
                    fighter_list = tourn_info1['fighters']

                    picked_cleaned = {}

                    for p1 in picks_already_made:
                        picked_cleaned[str(p1['fightid'])] = {"pickedwinner": p1['pickedwinner'], "how": p1['how'], "rd": p1['rd']}

                    return make_response(render_template("draftpage.html", userdata=user, fighterList=fighter_list, season_id=tourn_info1['season_id'], tourn_id=tourn_info1['id'], picks_already_made=picked_cleaned, started=0), 200)
            else:
                return {"message": "Tournament Doesn't Exist. Please go back"}
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)

    def post(self):

        if "user" in session:

            data = request.get_json()
            tour_id = data[0]['tour_id']
            season_id = data[0]['season_id']


            try:
                enrolledobj = EnrolledTournamentModel.specific_torn_user_enrolled_in(session['id'], tour_id)
                if not enrolledobj:
                    newEnrolled = EnrolledTournamentModel(session['id'], tour_id)
                    newEnrolled.save_to_db()
            except RuntimeWarning as e:
                return {"message": e}

            try:
                for d1 in data:

                    existing_pick = UserPicksModel.specific_pick_by_user_and_fightid(session['id'], d1['id'])
                    if existing_pick:
                        existing_pick.pickedwinner = d1['winner']
                        existing_pick.how = d1['how']
                        existing_pick.rd = d1['when']
                        existing_pick.save_to_db()
                    else:
                        pick = UserPicksModel(d1['tour_id'], d1['id'], d1['winner'], d1['how'], d1['when'], session['id'])
                        pick.save_to_db()

            except RuntimeError:
                return {"message": "Submission Unsuccessful"}

            return "viewevents/"+str(season_id)
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)