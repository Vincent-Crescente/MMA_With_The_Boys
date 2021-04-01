from flask import session, make_response, render_template
from flask_restful import Resource
from models.season import SeasonModel


class Season(Resource):

    def get(self, sid):
        season_info = SeasonModel.get_season_byid(sid)
        return season_info.json()

