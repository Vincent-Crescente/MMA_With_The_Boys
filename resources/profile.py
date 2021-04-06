from models.user import UserModel
from models.tournament import TournamentModel
from models.season import SeasonModel
from models.season_enrolled import SeasonEnrolledModel
from flask_restful import Resource, reqparse
from flask import render_template, session, make_response, url_for
from models.userpicks import UserPicksModel
from models.enrolled import EnrolledTournamentModel
from models.fighters import FightersLineUpModel
from werkzeug.security import safe_str_cmp
import re


class Profile(Resource):

    _user_parser = reqparse.RequestParser()

    _user_parser.add_argument('season_name',
                          type=str)

    _user_parser.add_argument('deactivate',
                              type=str)

    _user_parser.add_argument('delete',
                              type=str)

    _user_parser.add_argument('name_update',
                              type=str)


    @classmethod
    def calculate_season_pts(self):

        return_values = []

        if "user" in session:

            season_names = []
            all_tourn_ids_of_this_season = []
            points_for_each_season = {}
            summation = 0
            return_values = []

            # Getting all seasons this user is enrolled in

            season_enr_obj = SeasonEnrolledModel.all_seasons_user_enrolled_in(session['id'])

            # Getting user picks to calculate points per season or event.
            data = UserModel.find_by_id(session['id'])
            d1 = data.json()
            picks = d1['picks']

            season_enr = [s.json() for s in season_enr_obj]


            for s1 in season_enr:
                season = SeasonModel.get_season_byid(s1['season_id'])

                season_json = season.json()
                season_names.append(season.name)
                for tourn_ids in season_json['events']:
                    all_tourn_ids_of_this_season.append(tourn_ids['id'])

            # Looping through seasons to calculate points
            for seasonName in season_names:
                total_points = 0
                season = SeasonModel.get_season_byname(seasonName)
                season_json = season.json()
                for s2 in season_json['events']:
                    if s2['id'] in all_tourn_ids_of_this_season:
                        if picks:
                            for p1 in picks:
                                if int(p1['tournid']) == int(s2['id']):
                                    if p1['points'] > 0:
                                        total_points = total_points + p1['points']
                                        points_for_each_season[seasonName] = total_points
                                    else:
                                        total_points = total_points + 0
                                        points_for_each_season[seasonName] = total_points

                        else:
                            points_for_each_season[seasonName] = 0

            for a, b in points_for_each_season.items():
                summation = summation + b

            return_values.append(points_for_each_season)
            return_values.append(summation)

        return return_values

    @classmethod
    def admin_table_info(cls, admins_seasons):

        admin_value = []

        if admins_seasons:

            for season_name in admins_seasons:
                admin_controls_table = {}
                season_obj = SeasonModel.get_season_byname(season_name)
                season_json = season_obj.json()
                for s1 in season_json['events']:
                    admin_controls_table['season_name'] = season_json['name']
                    admin_controls_table['sid'] = season_json['season_id']
                    admin_controls_table['event_name'] = s1['name']
                    admin_controls_table['eid'] = s1['id']
                    admin_controls_table['active'] = s1['active']
                    admin_value.append(admin_controls_table)
                    admin_controls_table = {}
            return admin_value

        else:
            return admin_value

    def get(self):

        if "user" in session:

            values = Profile.calculate_season_pts()

            seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
            admins_seasons = [s.json()['name'] for s in seasons_objs]

            admin_value = Profile.admin_table_info(admins_seasons)

            user = UserModel.find_by_username(session['user'])

            return make_response(render_template("profile.html", season_names=values[0], total=values[1], admin_table=admin_value, tourns=[], username=user.username, popover=0), 200)

        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)

    def post(self):

        values = []
        total = 0
        tourns = {}

        if 'user' in session:

            data = Profile._user_parser.parse_args()

            if data['season_name']:

                values = Profile.calculate_season_pts()

                seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                admins_seasons = [s.json()['name'] for s in seasons_objs]

                admin_value = Profile.admin_table_info(admins_seasons)

                season = SeasonModel.get_season_byname(data['season_name'])
                season_json = season.json()

                all_tourn_names = [s1['name'] for s1 in season_json['events']]

                for event in season_json['events']:

                    # for some reason UserPicksModel.picks_by_user_id doesnt work the way youd expect"
                    picks = UserPicksModel.picks_by_tourn_id(event['id'])

                    for p1 in picks:
                        temp = p1.json()

                        if session['id'] is temp['userid']:
                            if temp['points'] == -1:
                                tourns[event['name']] = "-"
                            else:

                                if event['name'] in tourns.keys():
                                    temp1 = tourns[event['name']]
                                    tourns[event['name']] = temp1 + temp['points']
                                    total = p1.json()['points'] + total
                                else:
                                    tourns[event['name']] = temp['points']
                                    total = p1.json()['points'] + total

                for t in all_tourn_names:
                    if t not in tourns.keys():
                        tourns[t] = "DND"

                user = UserModel.find_by_username(session['user'])

                return make_response(render_template("profile.html", season_names=values[0], total=values[1], tourns=tourns, admin_table=admin_value, total_tourn=total, username=user.username, popover=0), 200)

            elif data['deactivate']:
                values = Profile.calculate_season_pts()

                seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                admins_seasons = [s.json()['name'] for s in seasons_objs]

                admin_value = Profile.admin_table_info(admins_seasons)

                if Profile.validate_admin_of_season(data['deactivate']):
                    tourn_obj = TournamentModel.get_tourn_by_id(data['deactivate'])
                    tourn_obj.active = False
                    tourn_obj.save_to_db()

                user = UserModel.find_by_username(session['user'])

                seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                admins_seasons = [s.json()['name'] for s in seasons_objs]

                admin_value = Profile.admin_table_info(admins_seasons)

                return make_response(render_template("profile.html", season_names=values[0], total=values[1], admin_table=admin_value, tourns=[], username=user.username, popover=0), 200)

            elif data['delete']:

                if Profile.validate_admin_of_season(data['delete']):
                    enroll_obj = EnrolledTournamentModel.all_enrolled_in_tourn_id(data['delete'])
                    tourn_obj = TournamentModel.get_tourn_by_id(data['delete'])
                    fighters_obj = FightersLineUpModel.all_fighters_specific_tourn(data['delete'])
                    picks_obj = UserPicksModel.picks_by_tourn_id(data['delete'])

                    if enroll_obj:
                        for obj in enroll_obj:
                            obj.delete_from_db()

                    if tourn_obj:
                        sid = tourn_obj.season_id
                        tourn_obj.delete_from_db()

                        seasonObj = SeasonModel.get_season_byid(sid)
                        seasonObj_events = seasonObj.json()['events']

                        if not seasonObj_events:
                            seasonObj.delete_from_db()

                    if fighters_obj:
                        for obj in fighters_obj:
                            obj.delete_from_db()

                    if picks_obj:
                        for obj in picks_obj:
                            obj.delete_from_db()

                values = Profile.calculate_season_pts()

                seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                admins_seasons = [s.json()['name'] for s in seasons_objs]

                admin_value = Profile.admin_table_info(admins_seasons)

                user = UserModel.find_by_username(session['user'])

                return make_response(render_template("profile.html", season_names=values[0], total=values[1], admin_table=admin_value, tourns=[], username=user.username, popover=0), 200)
            elif data['name_update']:

                reg = "(?=.*[a-z])(?=.*[A-Z]).{8,}"
                # compiling regex
                match_re = re.compile(reg)

                res = re.search(match_re, data['name_update'])

                if res:
                    user = UserModel.find_by_username(session['user'])
                    new_name = UserModel.find_by_username(data['name_update'])

                    if not new_name and user:

                        try:
                            user.username = data['name_update']
                            user.save_to_db()

                            seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])

                            if seasons_objs:
                                for s in seasons_objs:
                                    s.admin = user.username
                                    try:
                                        s.save_to_db()
                                    except:
                                        return {'message': "An error occurred while updating admin names due to username change."}

                            session['user'] = user.username

                        except:
                            return {'message': "An error occurred while changing the name."}

                        values = Profile.calculate_season_pts()

                        seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                        admins_seasons = [s.json()['name'] for s in seasons_objs]

                        admin_value = Profile.admin_table_info(admins_seasons)

                        return make_response(render_template("profile.html", season_names=values[0], total=values[1], tourns=[], admin_table=admin_value, username=user.username, popover=1), 200)

                    else:

                        values = Profile.calculate_season_pts()

                        seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                        admins_seasons = [s.json()['name'] for s in seasons_objs]

                        admin_value = Profile.admin_table_info(admins_seasons)

                        return make_response(render_template("profile.html", season_names=values[0], total=values[1], tourns=[], admin_table=admin_value, username=user.username, popover=2), 200)

                else:

                    user = UserModel.find_by_username(session['user'])

                    values = Profile.calculate_season_pts()

                    seasons_objs = SeasonModel.get_seasons_by_admin(session['user'])
                    admins_seasons = [s.json()['name'] for s in seasons_objs]

                    admin_value = Profile.admin_table_info(admins_seasons)

                    return make_response(render_template("profile.html", season_names=values[0], total=values[1], tourns=[], admin_table=admin_value, username=user.username, popover=0), 200)


            else:
                user = UserModel.find_by_username(session['user'])

            return make_response(render_template("profile.html", season_names=values[0], total=values[1], tourns=[], admin_table=[], username=user.username, popover=0), 200)
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 301)

    @classmethod
    def validate_admin_of_season(cls, tid):
        tournObj = TournamentModel.get_tourn_by_id(tid)
        seasonObj = SeasonModel.get_season_byid(tournObj.season_id)

        if tournObj and seasonObj:
            if safe_str_cmp(seasonObj.admin, session['user']):
                return 1
            else:
                return 0
        else:
            return 0

