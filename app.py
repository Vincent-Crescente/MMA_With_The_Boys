from flask import Flask, render_template, session, make_response, url_for, redirect, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegister, UserLogin, UserLogout
from resources.homepage import HomePage
from resources.tournament import Tournament
from resources.draftpage import DraftPage
from resources.userpicks import UserPicks
from resources.enrolled import Enrolled
from resources.fillTournament import FillTournament
from resources.viewevents import ViewEvents
from resources.profile import Profile
from resources.instruction import Instructions
from resources.standings import Standings
from db import db

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.secret_key = 'vinnyc'
api = Api(app)

jwt = JWTManager(app)  # does not create /auth, must create ourselves ex/login


api.add_resource(UserRegister, '/register')
# api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login', "/")
# api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(HomePage, '/home')
api.add_resource(DraftPage, '/draftpage/', '/draftpage/<int:tid>')
api.add_resource(Tournament, '/makeTournament')
# api.add_resource(FightersLineUp, '/fighterlist/<int:tour_id>')
api.add_resource(UserPicks, '/viewpicks/<int:id>')
api.add_resource(Enrolled, '/enrolled')
api.add_resource(FillTournament, '/filltournament/', '/filltournament/<int:id1>')
# api.add_resource(Season, '/addseason/<int:sid>')
api.add_resource(ViewEvents, '/viewevents/<int:sid>')
api.add_resource(Profile, '/profile/')
api.add_resource(Instructions, '/instructions/')
api.add_resource(Standings,  '/standings/')
#
#

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
