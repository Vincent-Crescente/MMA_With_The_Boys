from models.season_enrolled import SeasonEnrolledModel
from models.season import SeasonModel
from models.enrolled import EnrolledTournamentModel
from models.tournament import TournamentModel
from models.user import UserModel
from models.userpicks import UserPicksModel
from flask_restful import Resource, reqparse
from flask import render_template, make_response, session
import collections


class Standings(Resource):

    _user_parser = reqparse.RequestParser()

    _user_parser.add_argument('sid',
                              type=str)

    _user_parser.add_argument('season_dropdown',
                              type=str)

    _user_parser.add_argument('tourn_dropdown',
                              type=str)

    def get(self):
        if 'user' in session:

            all_seasons = SeasonModel.all_seasons()
            ids = {}
            for s in all_seasons:
                ids[s.name] = s.id
            return make_response(render_template("standings.html", ids=ids, names_and_points=[], season_chosen=-1, tourn_chosen=-1, sid=-1), 200)
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)

    def post(self):
        data = Standings._user_parser.parse_args()

        if data['sid'] and int(data['sid']) >= 0:

            if int(data['sid']) == 0:

                seasonObj = SeasonModel.all_seasons()

                users_season_totals = []
                ids_and_names = {}

                for s in seasonObj:
                    seasonObj = SeasonModel.get_season_byid(s.id)
                    events = seasonObj.json()['events']
                    for e in events:
                        enobj = EnrolledTournamentModel.all_enrolled_in_tourn_id(e['id'])

                        for e1 in enobj:
                            e1_json = e1.json()
                            temp = {e1_json['user_id']: e1_json['points']}
                            if temp[e1_json['user_id']] >= 0:
                                users_season_totals.append(temp)

                counter = collections.Counter()
                for d in users_season_totals:
                    counter.update(d)

                # { 1:5, 2:7 } => Added values to same keys
                ids_and_points = dict(counter)

                # { 1: 'Vincent', 2: 'Wally'}
                for id1, value in ids_and_points.items():
                    user = UserModel.find_by_id(id1)
                    ids_and_names[user.id] = user.username

                # {'Vincent': 5, 'Wally': 7}
                for key_to_map, name in ids_and_names.items():
                    if key_to_map in ids_and_points.keys():
                        ids_and_points[name] = ids_and_points.pop(key_to_map)

                # Names and points
                names_and_points = ids_and_points

                # { 'Wally': 7, 'Vincent': 5}
                sorted_points = {k: v for k, v in sorted(names_and_points.items(), key=lambda item: item[1], reverse=True)}

                all_seasons = SeasonModel.all_seasons()
                ids = {}
                for s in all_seasons:
                    ids[s.name] = s.id

                return make_response(render_template("standings.html", ids=ids, names_and_points=sorted_points,season_chosen=-1, tourn_chosen=-1, sid=data['sid']), 200)

            else:
                    seasonObj = SeasonModel.get_season_byid(data['sid'])
                    events = seasonObj.json()['events']

                    # {1: 2, 1: 3, 2:4, 2:3 } => Below
                    users_season_totals = []
                    ids_and_names = {}

                    for e in events:
                        enobj = EnrolledTournamentModel.all_enrolled_in_tourn_id(e['id'])

                        for e1 in enobj:
                            e1_json = e1.json()
                            temp = {e1_json['user_id']: e1_json['points']}
                            if temp not in users_season_totals:
                                if temp[e1_json['user_id']] >= 0:
                                    users_season_totals.append(temp)

                    counter = collections.Counter()
                    for d in users_season_totals:
                        counter.update(d)

                    # { 1:5, 2:7 } => Added values to same keys
                    ids_and_points = dict(counter)

                    # { 1: 'Vincent', 2: 'Wally'}
                    for id1, value in ids_and_points.items():
                        user = UserModel.find_by_id(id1)
                        ids_and_names[user.id] = user.username

                    # {'Vincent': 5, 'Wally': 7}
                    for key_to_map, name in ids_and_names.items():
                        if key_to_map in ids_and_points.keys():
                            ids_and_points[name] = ids_and_points.pop(key_to_map)

                    # Names and points
                    names_and_points = ids_and_points

                    # { 'Wally': 7, 'Vincent': 5}
                    sorted_points = {k: v for k, v in sorted(names_and_points.items(), key=lambda item: item[1], reverse=True)}

                    all_seasons = SeasonModel.all_seasons()
                    ids = {}
                    for s in all_seasons:
                        ids[s.name] = s.id

                    return make_response(render_template("standings.html", ids=ids, names_and_points=sorted_points, season_chosen=-1, tourn_chosen=-1, sid=data['sid']), 200)

        elif data['season_dropdown'] and not data['tourn_dropdown']:

            event_names = {}

            all_seasons = SeasonModel.all_seasons()
            ids = {}
            for s in all_seasons:
                ids[s.name] = s.id

            season_obj = SeasonModel.get_season_byid(data['season_dropdown'])
            if season_obj:
                events = season_obj.json()['events']
                for e in events:
                    event_names[e['name']] = e['id']

                name, id1 = next(iter(event_names.items()))

                all_picks_for_this_tourn = UserPicksModel.picks_by_tourn_id(id1)

                ids_and_points = {}
                ids_and_names = {}
                if all_picks_for_this_tourn:

                    for p in all_picks_for_this_tourn:
                        if p.user_id in ids_and_points.keys():
                            ids_and_points[p.user_id] = ids_and_points[p.user_id] + p.points
                        else:
                            ids_and_points[p.user_id] = p.points

                    for id1, value in ids_and_points.items():
                        user = UserModel.find_by_id(id1)
                        ids_and_names[user.id] = user.username

                    for key_to_map, name in ids_and_names.items():
                        if key_to_map in ids_and_points.keys():
                            ids_and_points[name] = ids_and_points.pop(key_to_map)

                    # { 'Wally': 7, 'Vincent': 5}
                    sorted_points = {k: v for k, v in sorted(ids_and_points.items(), key=lambda item: item[1], reverse=True)}

                    return make_response(render_template("standings.html", ids=ids, names_and_points={}, names_and_points_events=sorted_points, events=event_names, season_chosen=int(data['season_dropdown']),tourn_chosen=-1, sid=-1), 200)
                else:
                    return make_response(render_template("standings.html", ids=ids, names_and_points=[], events=event_names, season_chosen=int(data['season_dropdown']), tourn_chosen=-1, sid=-1), 200)
            else:
                all_seasons = SeasonModel.all_seasons()
                ids = {}
                for s in all_seasons:
                    ids[s.name] = s.id

                return make_response(render_template("standings.html", ids=ids,season_chosen=-1, tourn_chosen=-1, sid=-1), 200)

        elif data['season_dropdown'] and data['tourn_dropdown']:

            ids_and_points = {}
            ids_and_names = {}
            event_names = {}

            all_seasons = SeasonModel.all_seasons()
            ids = {}
            for s in all_seasons:
                ids[s.name] = s.id

            season_obj = SeasonModel.get_season_byid(data['season_dropdown'])
            if season_obj:
                events = season_obj.json()['events']
                for e in events:
                    event_names[e['name']] = e['id']

                all_picks_for_this_tourn = UserPicksModel.picks_by_tourn_id(data['tourn_dropdown'])

                ids_and_points = {}
                ids_and_names = {}
                if all_picks_for_this_tourn:

                    for p in all_picks_for_this_tourn:
                        if p.user_id in ids_and_points.keys():
                            ids_and_points[p.user_id] = ids_and_points[p.user_id] + p.points
                        else:
                            ids_and_points[p.user_id] = p.points

                    for id1, value in ids_and_points.items():
                        user = UserModel.find_by_id(id1)
                        ids_and_names[user.id] = user.username

                    for key_to_map, name in ids_and_names.items():
                        if key_to_map in ids_and_points.keys():
                            ids_and_points[name] = ids_and_points.pop(key_to_map)

                    # { 'Wally': 7, 'Vincent': 5}
                    sorted_points = {k: v for k, v in sorted(ids_and_points.items(), key=lambda item: item[1], reverse=True)}

                return make_response(render_template("standings.html", ids=ids, names_and_points={}, names_and_points_events=sorted_points, events=event_names, season_chosen=int(data['season_dropdown']),tourn_chosen=int(data['tourn_dropdown']), sid=-1), 200)

            else:
                all_seasons = SeasonModel.all_seasons()
                ids = {}
                for s in all_seasons:
                    ids[s.name] = s.id

                if int(data['season_dropdown']) > 0:
                    season_obj = SeasonModel.get_season_byid(data['season_dropdown'])
                    if season_obj:
                        season_event_names = [s1['name'] for s1 in season_obj.json()['events']]
                    else:
                        pass
                return make_response(render_template("standings.html", ids=ids, names_and_points=[],season_chosen=-1,tourn_chosen=-1, sid=-1), 200)

        else:

            all_seasons = SeasonModel.all_seasons()
            ids = {}
            for s in all_seasons:
                ids[s.name] = s.id

            return make_response(render_template("standings.html", ids=ids, names_and_points=[],season_chosen=-1, tourn_chosen=-1, sid=-1), 200)

