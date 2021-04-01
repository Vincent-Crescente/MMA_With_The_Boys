from flask_restful import Resource, request, url_for
from flask import session, make_response, render_template
from models.fighters import FightersLineUpModel
from models.tournament import TournamentModel
from models.userpicks import UserPicksModel
from models.enrolled import EnrolledTournamentModel
from models.season_enrolled import SeasonEnrolledModel
from models.user import UserModel
from werkzeug.security import safe_str_cmp


class FillTournament(Resource):

    @staticmethod
    def calculate(tid):
        try:
            fighters_results = FightersLineUpModel.all_fighters_specific_tourn(tid)
            picks_for_this_tourn = UserPicksModel.picks_by_tourn_id(tid)

            for f1 in fighters_results:
                fight = f1.json()

                userpick = {}
                fid = 0

                for p1 in picks_for_this_tourn:
                    if p1.fightid == f1.id:
                        userpick = p1.json()
                        fid = p1.fightid

                        pick = UserPicksModel.specific_pick_by_tourn_and_user_Fight_id(userpick['userid'], tid, fid)

                        for fightEntry in pick:

                            if fight['winner'] == userpick['pickedwinner']:
                                fightEntry.points = 0

                                if fight['prelim'] == "n":  # meaning main card n = 'not prelim'
                                    fightEntry.points = fightEntry.points + 3

                                    if fight['how'] == userpick['how']:
                                        fightEntry.points = fightEntry.points + 1

                                    if fight['how'] != "DEC" and fight['when'] == userpick['rd']:
                                        fightEntry.points = fightEntry.points + 1

                                    if fight['how'] != "DEC" and fight['when'] == userpick['rd'] and fight['how'] == userpick['how']:
                                        fightEntry.points = fightEntry.points + 5

                                elif fight['prelim'] == "y":
                                    fightEntry.points = fightEntry.points + 2

                                    if fight['how'] == userpick['how']:
                                        fightEntry.points = fightEntry.points + 1

                                    if fight['how'] != "DEC" and fight['when'] == userpick['rd']:
                                        fightEntry.points = fightEntry.points + 1

                                    if fight['how'] != "DEC" and fight['when'] == userpick['rd'] and fight['how'] == userpick['how']:
                                        fightEntry.points = fightEntry.points + 5

                                fightEntry.save_to_db()
                            else:
                                fightEntry.points = 0
                                fightEntry.save_to_db()


        except RuntimeWarning as e:
            return {"message": e}

    # destroy
    def get(self, id1):

        if 'user' in session:

            t_model = TournamentModel.get_tourn_by_id(id1=id1)
            if t_model:
                fighters = FightersLineUpModel.all_fighters_specific_tourn(id1)

                fighter_list = [f1.json() for f1 in fighters]

                user = UserModel.find_by_username((session['user']))

                return make_response(render_template("fillTournament.html", userdata=user, fighterList=fighter_list, t_id=t_model.id, tname=t_model.name), 200)

            else:
                return {"message": "Tournament Not Active"}

        return make_response(render_template("mainSignIn-pleasesignin.html"), 200)

    def post(self):

        if 'user' in session:

            data = request.get_json()

            tour_id = data[0]['tour_id']

            try:
                fighters = FightersLineUpModel.all_fighters_specific_tourn(tour_id)

                for f1 in fighters:
                    for d1 in data:
                        if safe_str_cmp(d1['id'], str(f1.id)):
                            f1.winner = d1['winner']
                            f1.how = d1['how']
                            f1.when = d1['when']

                FillTournament.calculate(tour_id)

                # Update total tournament numbers for each player affected
                enObj = EnrolledTournamentModel.all_enrolled_in_tourn_id(tour_id)

                for e in enObj:
                    temp = 0
                    specific_picks = UserPicksModel.picks_for_tourn_user_id(e.tourn_id, e.user_id)
                    for sp in specific_picks:
                        if e.user_id == sp.user_id:
                            temp = temp + sp.points
                    e.points = temp
                    e.save_to_db()

                tourn_obj = TournamentModel.get_tourn_by_id(tour_id)
                tourn_obj.started = True
                tourn_obj.save_to_db()

            except RuntimeWarning as e:
                return {"message": e}

            try:
                for f1 in fighters:
                    f1.save_to_db()
            except RuntimeError:
                return {"message": "Submission Unsuccessful"}

            return "profile/"
        else:
            return make_response(render_template("mainSignIn-pleasesignin.html"), 200)
