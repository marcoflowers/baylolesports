from google.appengine.ext import ndb
import logging
from google.appengine.api import users
import json
import urllib
import urllib2
import time


class team(ndb.Model): #don't touch
    name = ndb.StringProperty()
    members = ndb.KeyProperty(repeated=True)
    admin = ndb.UserProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class player(ndb.Model): #don't touch
    # query with player.get_by_id(id)
    name = ndb.StringProperty()
    division = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()

class tournament(ndb.Model): #by no means final
    name = ndb.StringProperty()
    active = ndb.BooleanProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    admins = ndb.UserProperty(repeated=True)
    teams = ndb.KeyProperty(repeated=True)
    size = ndb.IntegerProperty()
    join_requests = ndb.KeyProperty(repeated=True)
    games = ndb.KeyProperty(repeated=True)



class game(ndb.Model):
    round = ndb.IntegerProperty()
    spot = ndb.IntegerProperty()
    teams = ndb.KeyProperty(repeated=True)
    scheduled_date = ndb.DateTimeProperty()
    happened = ndb.BooleanProperty()





def get_summoner_rank(summoner_id):
    api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
    try:
        url = 'https://na.api.pvp.net/api/lol/na/v2.4/league/by-summoner/' + str(summoner_id) + '?api_key=' + api_key
        logging.info(url)
        result = json.loads(urllib2.urlopen(url).read())
        for queue in result[str(summoner_id)]:
            if queue["queue"]=="RANKED_SOLO_5x5":
                tier = queue["tier"]
                for entry in queue["entries"]:
                    if entry['playerOrTeamId'] == str(summoner_id):
                        number = entry['division']
                        rank = tier.title() + ' ' + number
        return rank
    except:
        return 'Unranked'


def new_team(name, admin, members):
    new_team = team(name=name, admin=admin, members=members)
    new_team.put()

def new_player(name, division, id):
    new_player = player(name=name, division=division, id=id)
    new_team.put()

def new_tournament(name, size):
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
    return new_tournament.put()


        



def get_ukey(object):
    return object.key.urlsafe()

def to_key(ukey):
    return ndb.Key(urlsafe=ukey)

def key_object(key):
    return key.get()

def keys_objects(keys):
    objects=[]
    for key in keys:
        dictionary = key.get().to_dict()
        dictionary["created"]=str(dictionary["created"])
        objects.append(dictionary)
    return json.dumps(objects)

def get_sum_id(sum_name):
    api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
    logging.error("start")
    #take out spaces and make lower case
    sum_name_unspaced = sum_name.replace(" ", "").lower()
    try:
        #query riot
        url = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/"+sum_name_unspaced+"?api_key="+api_key
        logging.error(url)
        result = json.loads(urllib2.urlopen(url).read())
        return result[sum_name_unspaced]['id']
    except:
        return False
    #return the summoner_id
    
def rank_to_url(division):
    rank_switch = {"I":"1","II":"2","III":"3","IV":"4","V":"5"}
    if division != "Unranked":
        division = division.split(" ")
        lowercase=division[0].lower()
        logging.info(lowercase)
        new_rank = lowercase+"_"+rank_switch[division[1]]
        return new_rank
    else:
        return "In Placements"



