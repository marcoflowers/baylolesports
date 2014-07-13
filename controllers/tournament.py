import webapp2
import os
from models.models import *
import jinja2
import logging
from base import BaseHandler
import json
from google.appengine.api import users

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
        user = users.get_current_user()
        if user:
            teams = team.query(team.admin==user).fetch()
            template_values['teams'] = teams
        template_values['tournament'] = tournament
        self.render_template('/templates/tournament/display_%s.html' % tournament.size, template_values)
    def post(self, ukey):
        teams = self.request.get("join")
        tournament = key_object(to_key(ukey))
        for team in teams:
            tournament.join_requests.append(to_key(team))
        tournament.put()
        

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
        self.render_template('/templates/tournament/index.html', template_values) 


class new_tournament(BaseHandler):
    def get(self):
        self.login()
        user = users.get_current_user()
        if user:
            template_values = {}
            self.render_template('/templates/tournament/new_tournament.html', template_values)
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        service = build_calendar_service()

        name = self.request.get("tournament_name").encode()
        size = int(self.request.get("size").encode())
        new_tournament = tournament(name=name, size=size)
        placeholder_teams = []
        for num in range(0, 32):
            new_team = team(name="Seed " + str(num + 1))
            placeholder_teams.append(new_team)
        for num in range(0, 16):
            spot = num
            teams = [placeholder_teams.pop(0).put(),placeholder_teams.pop(0).put()]
            placeholder_game = game(spot=spot, teams=teams)
            key = placeholder_game.put()
            new_tournament.round1.append(key)
        for num in range(0, 8):
            spot = num
            teams = [team().put(), team().put()]
            placeholder_game = game(spot=spot, teams=teams)
            key = placeholder_game.put()
            new_tournament.round2.append(key)
        for num in range(0, 4):
            spot = num
            teams = [team().put(), team().put()]
            placeholder_game = game(spot=spot, teams=teams)
            key = placeholder_game.put()
            new_tournament.round3.append(key)
        for num in range(0, 2):
            spot = num
            teams = [team().put(), team().put()]
            place_holder_game = game(spot=spot, teams=teams)
            key = placeholder_game.put()
            new_tournament.round4.append(key)
        for num in range(0, 1):
            spot = num
            teams = [team().put(), team().put()]
            place_holder_game = game(spot=spot, teams=teams)
            key = placeholder_game.put()
            new_tournament.round5.append(key)
        spot = 0
        teams = [team().put(), team().put()]
        place_holder_game = game(spot=spot, teams=teams)
        key = placeholder_game.put()
        new_tournament.round6.append(key)

        new_tournament.finalized = False
        new_tournament.admins.append(users.get_current_user())
        new_tournament.active = True
        calendar = {}
        calendar['kind'] = "calendar#calendar"
        calendar['summary'] = name
        calendar['timeZone'] = 'America/Los_Angeles'
        response = service.calendars().insert(body=calendar).execute()
        calendar_id = response['id']
        body = {}
        body['scope'] = {'type':'user', 'value':users.get_current_user().email()}
        body['etag'] = '1'
        body['role'] = 'writer'
        service.acl().insert(calendarId=calendar_id, body=body).execute()
        body['scope'] = {'type':'default','value':''}
        body['role'] = 'reader'
        service.acl().insert(calendarId=calendar_id, body=body).execute()
        new_tournament.calendar = calendar_id
        key = new_tournament.put()
        self.redirect('/tournament/admin/' + key.urlsafe())


class check_name(BaseHandler):
    def get(self, name):
        tournament_list = tournament.query(tournament.name==name).fetch()
        available = True
        if(len(tournament_list) > 0):
            available = False
        self.response.out.write(json.dumps({"available":available}))

