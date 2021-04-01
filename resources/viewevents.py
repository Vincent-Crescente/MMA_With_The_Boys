from models.season import SeasonModel
from models.enrolled import EnrolledTournamentModel
from models.season_enrolled import SeasonEnrolledModel
from models.user import UserModel
from flask_restful import Resource
from flask import make_response, render_template, session


class ViewEvents(Resource):

    def get(self, sid):

        if "user" in session:

            tournaments_info = SeasonModel.get_season_byid(sid)

            tournaments_info1 = tournaments_info.json()

            user = UserModel.find_by_username(session['user'])
            u1 = user.json()

            s_enrolled_obj = SeasonEnrolledModel.all_seasons_user_enrolled_in(u1['id'])
            s_enrolled_by_user = [s.season_id for s in s_enrolled_obj]

            # If the user is not enrolled in the season we enroll them.
            if sid not in s_enrolled_by_user:
                user_enrolled = SeasonEnrolledModel(u1['id'], sid)
                user_enrolled.save_to_db()

            enObj = EnrolledTournamentModel.all_torns_user_enrolled_in(u1['id'])
            tournsEnrolled_byUser = [e.tourn_id for e in enObj]

            return make_response(render_template("viewevents.html", tournaments_info=tournaments_info1, season_name=tournaments_info1['name'], tournsEnrolled_byUser=tournsEnrolled_byUser), 200)
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)