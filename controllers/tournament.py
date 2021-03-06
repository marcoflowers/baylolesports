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
        logging.info(teams)
        tournament = key_object(to_key(ukey))
        logging.info(tournament.join_requests)
        tournament.join_requests=[to_key(teams)]
        tournament.put()
        self.redirect("/tournament/"+ukey)
        

class admin_page(BaseHandler):
    def get(self, ukey):
        self.login()
        template_values = {}
        key = to_key(ukey)
        tournament = key_object(key)
        template_values['tournament'] = tournament
        template_values['log'] = log
        self.render_template('/templates/tournament/admin_%s.html' % tournament.size, template_values)

    def post(self, ukey):
        user = users.get_current_user()
        tournament = key_object(to_key(ukey))
        if(user not in tournament.admins):
            self.redirect('/tournament/%s' % ukey)
        if self.request.get("bracket"):
            #for every sent data get the place and value
            for field in (self.request.arguments()):
                if(field=="bracket"):
                    continue
                value = self.request.get(field)
                position = field.split("-")
                game_number = int(position[0])
                slot = int(position[1])
                #only set the first round for teams
                for rounds in tournament.rounds:
                    if(rounds.round==1):
                        roundo=rounds
                #get the team based o its name
                teamo=team.query(team.name==value).get()
                team_key=teamo.key
                #for each game in the round if that game has the right index number set the team at its slot
                for games in roundo.games:
                    if(key_object(games).index==game_number):
                        key_object(games).teams[slot]=team_key
                        logging.info(key_object(games))
                        key_object(games).put()
                logging.info("Swag")
        elif self.request.get("finalize_bracket"):
            tournament.finalized = True
            tournament.put()
        elif self.request.get("join"):
            logging.info("yes")
            for x in range(0,tournament.size-1):
                teamo=self.request.get("join"+str(x))
                logging.info(team)
                if(team):
                    logging.info("team")
                    team_key=to_key(teamo)
                    tournament.join_requests.remove(team_key)
                    tournament.teams.append(team_key)
                    tournament.put()
        elif self.request.get("settings"):
            pass
        elif self.request.get("results"):
            pass
        self.redirect("/tournament/admin/"+ukey)

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
            round1.games.append(game(round=1,index=num,teams=teams, tournament=tournament_key).put())
        new_tournament.rounds.append(round1)

        round2 = round(round=2, games=[])
        for num in range(0, size / 4):
            round2.games.append(game(round=2,index=num,teams=teams, tournament=tournament_key).put())
        new_tournament.rounds.append(round2)

        if(size / 8 > 0):
            round3 = round(round=3, games=[])
            for num in range(0, size / 8):
                round3.games.append(game(round=3,index=num,teams=teams, tournament=tournament_key).put())
            new_tournament.rounds.append(round3)

        if(size / 16 > 0):
            round4 = round(round=4, games=[])
            for num in range(0, size / 16):
                round4.games.append(game(round=4,index=num,teams=teams, tournament=tournament_key).put())
            new_tournament.rounds.append(round4)

        if(size / 32 > 0):
            round5 = round(round=5, games=[])
            for num in range(0, size / 32):
                round5.games.append(game(round=5,index=num,teams=teams, tournament=tournament_key).put())
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




def get_game(game): #game must be a key
    api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
    summoners = []
    game = key_object(game)
    total_games = {}
    game_list = []
    games = {}
    summoner_ids = []
    for team in game.teams:
        for member in team.members:
            url = "https://na.api.pvp.net/api/lol/na/v1.3/game/by-summoner/%s/recent?api_key=%s" % [member.key().id(), api_key]
            try:
                response = json.load(urllib2.urlopen(url))
                games_found = response['games']
                summoner_id = response['summonerId']
                total_games[member.key().id()] = games
                for game_found in games_found:
                    if(game_found['gameType'] != 'CUSTOM_GAME'):
                        continue
                    game_id = game_found['gameId']
                    if(game_id in games.keys()):
                        games[game_id][summoner_id] = game_found['stats']
                    else:
                        games[game_id] = {}



            except Exception as e:
                print e


    target_game = ''
    game_count = {}
    for game_found in game_list:
        if game_found[gameId] in game_list.keys():
            game_count[gameId] += 1
        else:
            game_count[gameId] = 1
    



# games
#     gameid
#         game_info
#         summoner
#             stats
#         summoner
#             stats
#         summoner
#             stats
#         summoner
#             stats
#         summoner
#             stats



class new(BaseHandler):
    def get(self):
        pass





















