from flask_restful import Resource, reqparse, request
from flask import render_template, make_response, session
from models.tournament import TournamentModel
from models.season import SeasonModel
from models.fighters import FightersLineUpModel


class Tournament(Resource):
    _user_parser = reqparse.RequestParser()
    _user_parser.add_argument('opp1[]',
                              type=str,
                              required=True,
                              help="This field cannot be left blank", action='append')

    _user_parser.add_argument('opp2[]',
                              type=str,
                              required=True,
                              help="This field cannot be left blank", action='append')

    _user_parser.add_argument('rd[]',
                              type=str,
                              required=True,
                              help="This field cannot be left blank", action='append')

    _user_parser.add_argument('prelim[]',
                              type=str,
                              required=True,
                              help="This field cannot be left blank", action='append')

    _user_parser.add_argument('tourName',
                              type=str,
                              required=True,
                              help="This field cannot be left blank")

    _user_parser.add_argument('newSeasonName',
                              type=str,
                              )

    _user_parser.add_argument('existingSeasonId',
                              type=str,)

    def post(self):
        if request.method == "POST":
            data = Tournament._user_parser.parse_args()

            # Get rid of empty strings
            data['prelim[]'] = list(filter(lambda prelim1: prelim1 != '', data['prelim[]']))

            try:

                if data['existingSeasonId']:

                    existing_season = SeasonModel.get_season_byid(data['existingSeasonId'])
                    existing_tourn = TournamentModel.get_tourn_by_name(data['tourName'])

                    'If existing season actually exists.'
                    if not existing_season:
                        admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                        if admin_seasons:
                            seasons = [s1.json() for s1 in admin_seasons]
                        else:
                            seasons = []

                        return make_response(render_template("makeTournament.html", curr_season=seasons, success=-3))

                    else:

                        'If existing event already exists.'
                        if existing_tourn:
                            admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                            if admin_seasons:
                                seasons = [s1.json() for s1 in admin_seasons]
                            else:
                                seasons = []

                            return make_response(render_template("makeTournament.html", curr_season=seasons, success=-4))
                        else:

                            existing_tourn = TournamentModel(data['tourName'], existing_season.id)
                            existing_tourn.save_to_db()

                            # ---------------------------------------------

                            all_tournaments = TournamentModel.all_tournaments()
                            torns = [torn.json() for torn in all_tournaments]

                            nextid = max([tor['id'] for tor in torns])

                            for opp1, opp2, rd, prelim in zip(data['opp1[]'], data['opp2[]'], data['rd[]'], data['prelim[]']):
                                fight = FightersLineUpModel(nextid, opp1, opp2, rd, prelim=prelim)
                                fight.save_to_db()

                            success = 1

                            admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                            if admin_seasons:
                                seasons = [s1.json() for s1 in admin_seasons]
                            else:
                                seasons = []

                            return make_response(render_template("makeTournament.html", curr_season=seasons, success=success))

                elif data['newSeasonName']:

                    exists = SeasonModel.get_season_byname(data['newSeasonName'])

                    if exists:
                        admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                        if admin_seasons:
                            seasons = [s1.json() for s1 in admin_seasons]
                        else:
                            seasons = []
                        return make_response(render_template("makeTournament.html", curr_season=seasons, success=-2))

                    else:
                        newseason = SeasonModel(data['newSeasonName'], session['user'])
                        newseason.save_to_db()

                        tourn_exist = TournamentModel.get_tourn_by_name(data['tourName'])

                        if tourn_exist:
                            admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                            if admin_seasons:
                                seasons = [s1.json() for s1 in admin_seasons]
                            else:
                                seasons = []
                            return make_response(render_template("makeTournament.html", curr_season=seasons, success=-4))

                        else:

                            newtorn = TournamentModel(data['tourName'], newseason.id)
                            newtorn.save_to_db()

                            all_tournaments = TournamentModel.all_tournaments()

                            torns = [torn.json() for torn in all_tournaments]

                            nextid = max([tor['id'] for tor in torns])

                            for opp1, opp2, rd, prelim in zip(data['opp1[]'], data['opp2[]'], data['rd[]'], data['prelim[]']):
                                fight = FightersLineUpModel(nextid, opp1, opp2, rd, prelim=prelim)
                                fight.save_to_db()

                            admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                            if admin_seasons:
                                seasons = [s1.json() for s1 in admin_seasons]
                            else:
                                seasons = []

                            success = 1

                            return make_response(render_template("makeTournament.html", curr_season=seasons, success=success))

                else:

                    admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
                    if admin_seasons:
                        seasons = [s1.json() for s1 in admin_seasons]
                    else:
                        seasons = []

                return make_response(render_template("makeTournament.html", curr_season=seasons, success=0))


            except RuntimeError():

                return {"Message": "There was something wrong with inserting in the DB."}
        else:
            return {"message": "Not Allowed"}

    def get(self):

        if 'user' in session:

            admin_seasons = SeasonModel.get_seasons_by_admin(session['user'])
            if admin_seasons:
                seasons = [s1.json() for s1 in admin_seasons]
            else:
                seasons = []

            return make_response(render_template("makeTournament.html", curr_season=seasons, success=-1))
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)