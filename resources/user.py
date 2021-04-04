import re
from flask_restful import Resource, reqparse
from flask import session, redirect, url_for
from models.user import UserModel
from passlib.hash import pbkdf2_sha256
from resources.homepage import HomePage
from models.tournament import TournamentModel
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from flask import render_template, make_response
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This username field cannot be left blank")

_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This password field cannot be left blank")


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return make_response(render_template("registered-already.html"), 400)

        reg = "(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
        # compiling regex
        match_re = re.compile(reg)

        res = re.search(match_re, data['password'])

        if res:
            hash1 = pbkdf2_sha256.hash(data['password'])

            user = UserModel(data['username'], hash1)
            user.save_to_db()

            return make_response(render_template("register-complete.html"), 201)
        else:
            return make_response(render_template("register-problem.html"), 201)



    def get(self):
        return make_response(render_template("register.html"), 200)


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User does not exist.'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User does not exist.'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    def get(self):
        return make_response(render_template("mainSignIn.html"), 200)

    @classmethod
    def post(cls):

        data = _user_parser.parse_args()

        user = UserModel.find_by_username((data['username']))

        if user:

            # access_token = create_access_token(identity=user.id, fresh=True)
            # refresh_token = create_refresh_token(user.id)

            if pbkdf2_sha256.verify(data['password'], user.password):

                session['user'] = user.username
                session['id'] = user.id

                return redirect(url_for("homepage"))
            return make_response(render_template("signin-invalid.html"))
        return make_response(render_template("signin-dne.html"))



class UserLogout(Resource):
    #@jwt_required
    def get(self):
        session.pop("user", None)
        return make_response(render_template("loggedout.html"), 200)
        # jti = get_raw_jwt()['jti']  # jti is "JWT ID", a unique identifier for a JWT
        # BLACKLIST.add(jti)
        # return make_response(render_template("loggedout.html"))


class TokenRefresh(Resource):
    # @jwt_refresh_token_required  # will not enter this code unless you have a
    def post(self):                        # refresh token
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200



