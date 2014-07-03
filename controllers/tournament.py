import webapp2
import os
from models.models import *
import jinja2
import logging
from base import BaseHandler
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape']
)


class display_tournament(BaseHandler):
    def get(self, ukey):
        self.login()
        template_values = {}
        key = to_key(ukey)
        tournament = key_object(key)
        template_values['tournament'] = tournament
        self.render_template('/templates/tournament/display_%s.html' % tournament.size, template_values)

class admin_page(BaseHandler):
    def get(self, ukey):
        self.login()
        template_values = {}
        key = to_key(ukey)
        tournament = key_object(key)
        template_values['tournament'] = tournament
        #size = ukey
        #template_values["size"] = size
        self.render_template('/templates/tournament/admin_%s.html' % tournament.size, template_values)

    def post(self, ukey):
        logging.info("Data Saved")
        tournament = key_object(to_key(ukey))
        if self.request.get("save_bracket"):
            position = self.request.get("position").split("-")
            game_number = int(position[0])
            slot = int(position[1])
            team = self.request.get("team")
            game = tournament.games[game_number]
            game.bracket_spot = game_number
            game.teams[slot] = team
            game.put()
        #    for position in range(1, tournament.size + 1):
        #        team = self.request.get("1-" + str(position)
        #        if(team):
        #            game = tournament.games[position/2]
        #            game.teams[position % 2] = to_key(team)
        #            game.put()
        elif self.request.get("finalize_bracket"):
            tournament.finalized = True
            tournament.put()
        #elif self.request.get("join"):
        #elif self.request.get("settings"):
        #elif self.request.get("schedule"):
        #elif self.request.get("results"):


class index(BaseHandler):
    def get(self):
        self.login()
        query = tournament.query(tournament.active==True).order(-tournament.created)
        tournaments = query.fetch()
        template_values = {"tournaments":tournaments}
        logging.info(tournaments)
        self.render_template('/templates/tournament/index.html', template_values) 


class new_tournament(BaseHandler):
    def get(self):
        self.login()
        template_values = {}
        self.render_template('/templates/tournament/new_tournament.html', template_values)

    def post(self):
        name = self.request.get("tournament_name").encode()
        size = int(self.request.get("size").encode())
        new_tournament = tournament(name=name, size=size)
        placeholder_teams = []
        for num in range(0, size):
            new_team = team(name="Seed " + str(num + 1))
            placeholder_teams.append(new_team)
        for num in range(0, size/2):
            round = 1
            spot = num
            teams = [placeholder_teams.pop(0).put(),placeholder_teams.pop(0).put()]
            placeholder_game = game(round=round, spot=spot, teams=teams)
            key = placeholder_game.put()
            new_tournament.games.append(key)
        if size >= 8:
            for num in range(0, size/4):
                round = 2
                spot = num
                teams = [team().put(), team().put()]
                placeholder_game = game(round=round, spot=spot, teams=teams)
                key = placeholder_game.put()
                new_tournament.games.append(key)
        if size >= 16:
            for num in range(0, size/8):
                round = 2
                spot = num
                teams = [team().put(), team().put()]
                placeholder_game = game(round=round, spot=spot, teams=teams)
                key = placeholder_game.put()
                new_tournament.games.append(key)
        if size == 32:
            for num in range(0, size/16):
                round = 2
                spot = num
                teams = [team().put(), team().put()]
                place_holder_game = game(round=round, spot=spot, teams=teams)
                key = placeholder_game.put()
                new_tournament.games.append(key)
        new_tournament.finalized = False
        new_tournament.admins.append(users.get_current_user())
        new_tournament.active = True
        key = new_tournament.put()
        self.redirect('/tournament/admin/' + key.urlsafe())


class check_name(BaseHandler):
    def get(self, name):
        tournament_list = tournament.query(tournament.name==name).fetch()
        available = True
        if(len(tournament_list) > 0):
            available = False
        self.response.out.write(json.dumps({"available":available}))

