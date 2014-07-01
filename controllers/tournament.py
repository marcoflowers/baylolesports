import webapp2
import os
from models import models
import jinja2
import logging
from base import BaseHandler
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape']
)



class tournament_page(BaseHandler):
    def get(self, ukey):
        self.login()
        template_values = {}
        #key = to_key(ukey)
        #tournament = key_object(key)
        size = ukey
        template_values["size"] = size
        self.render_template('/templates/tournament/bracket_%s.html' % size, template_values)

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
        #query = tournament.query(active=True).order(-tournament.created)
        #template_values = {"tournaments", query.fetch()}
        template_values={}
        self.render_template('/templates/tournament/index.html', template_values) 


class new_tournament(BaseHandler):
    def get(self):
        self.login()
        template_values = {}
        self.render_template('/templates/tournament/new_tournament.html', template_values)

    def post(self):
        name = self.request.get("tournament_name")
        size = int(self.request.get("size").encode())
        key = models.new_tournament(name, size)
        self.redirect('/tournament/' + key.urlsafe())


class check_name(BaseHandler):
    def get(self, name):
        tournament_list = tournament.query(tournament.name==name).fetch()
        available = True
        if(tournament_list > 0):
            available = False
        self.response.out.write(json.dumps({"available":available}))

