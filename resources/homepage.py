from flask import session, make_response, render_template
from models.user import UserModel
from models.season_enrolled import SeasonEnrolledModel
from models.season import SeasonModel
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
)

class HomePage(Resource):

    # @jwt_required
    def get(self):
        if "user" in session:
            user = UserModel.find_by_username((session['user']))

            if user:
                u1 = user.json()
                seasonData = SeasonModel.all_seasons()
                enObj = SeasonEnrolledModel.all_seasons_user_enrolled_in(u1['id'])

                seasonsEnrolled_byUser = [e.season_id for e in enObj]

                # match to tounrey being shown, if match button changes to view picks
                return make_response(render_template("mainHome.html", userdata=user, seasondata=seasonData, seasonsEnrolled_byUser=seasonsEnrolled_byUser))
            else:
                return make_response(render_template("mainSignIn-pleasesignin.html"), 200)
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)

