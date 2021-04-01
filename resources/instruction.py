from flask_restful import Resource, url_for
from resources.homepage import HomePage
from flask import render_template, session, make_response


class Instructions(Resource):

    def get(self):
        if 'user' in session:
            return make_response(render_template("instructions.html"), 200)
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)