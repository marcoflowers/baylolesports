import webapp2
import os
from models.models import *
import jinja2
import logging
from base import BaseHandler
import json
from math import log
from google.appengine.api import users
from datetime import datetime

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
        template_values['log'] = log
        self.render_template('/templates/tournament/admin_%s.html' % tournament.size, template_values)

class post:
    def post(self, ukey):
        user = users.get_current_user()
        tournament = key_object(to_key(ukey))
        if(user not in tournament.admins):
            self.redirect('/tournament/%s' % ukey)
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
        elif self.request.get("join"):
            pass
        elif self.request.get("settings"):
            pass
        elif self.request.get("results"):
            pass

class events:
    def __init__(self):
        self.service = build_calendar_service()
    def get(self, ukey):
        tournament = tournament.get(to_key(ukey))
        calendar_id = tournament.calendar
        list = self.service.events().list(calendar_id=calendar_id).execute()
        nextPageToken = list['nextPageToken']
        nextSyncToken = list['nextSyncToken']
        events = list['items']
        games = []
        for event in events:
            game = {}
            game['id'] = event['etag']
            game_datetime= event['start']['datetime'].split('T')
            game_time = game_datetime[1][0:5]
            game_date = game_datetime[0].replace('-', '/')
            game['time'] = game_time
            game['date'] = game_date
            games.append(game)
        return games

    def post(self, ukey):
        #
        # etag should give useful info about placement of game
        # the POST should include:
        # [notifications, game]
        tournament = tournament.get(to_key(ukey))
        notifications = self.request.get("notifications")
        game = self.request.get("game_ukey")
        calendar_id = tournament.calendar
        game = key_object(game_ukey)
        teams = [key_object(game.teams[0]), key_object(game.teams[1])]
        attendees = []
        for team in teams:
            for player in team.members:
                email = player.user.email()
                attendee = {
                    'displayName':player.name,
                    'email':email,
                    'response_status':'needsAction'
                }
                attendees.append(attendee)
        #body = {
        #    'attendees': attendees,
        #    'start': {
        #        'date':, #yyyy-mm-dd
        #        'dateTime':, #yyyy-mm-ddThh:mm:ss
        #    },
        #    'etag':round + "-" + game_num,#round-game_num, #Gives useful info about game round and spot
        #    'visibility':'public',
        #    'kind':'calendar#event',

#        }

#        calendar_id = tournament.get(to_key(ukey)).calendar
#        self.service.events().insert(calendar_id=calendar_id, body=body, sendNotifications=notifications).execute()
        return {"success":True}


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
        tournament_key = new_tournament.put()
        placeholder_team = team.query(team.name=="None").fetch()
        try:
            team_key = placeholder_team[0].key()
        except:
            team_key = team(name="None").put()
        teams = [team_key, team_key]

        round1 = round(round=1, games=[])
        for num in range(0, size / 2):
            round1.games.append(game(teams=teams, tournament=tournament_key).put())
        new_tournament.rounds.append(round1)

        round2 = round(round=2, games=[])
        for num in range(0, size / 4):
            round2.games.append(game(teams=teams, tournament=tournament_key).put())
        new_tournament.rounds.append(round2)

        if(size / 8 > 0):
            round3 = round(round=3, games=[])
            for num in range(0, size / 8):
                round3.games.append(game(teams=teams, tournament=tournament_key).put())
            new_tournament.rounds.append(round3)

        if(size / 16 > 0):
            round4 = round(round=4, games=[])
            for num in range(0, size / 16):
                round4.games.append(game(teams=teams, tournament=tournament_key).put())
            new_tournament.rounds.append(round4)

        if(size / 32 > 0):
            round5 = round(round=5, games=[])
            for num in range(0, size / 32):
                round5.games.append(game(teams=teams, tournament=tournament_key).put())
            new_tournament.rounds.append(round5)


        new_tournament.winner = team_key
        new_tournament.current_round = 1
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

