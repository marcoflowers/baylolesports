from google.appengine.ext import ndb
import logging
from google.appengine.api import users
import json
import urllib
import os
import urllib2
import time
from google.appengine.api import taskqueue
import datetime
from oauth2client.appengine import AppAssertionCredentials
    
import httplib2
from apiclient import discovery
from oauth2client import client
from google.appengine.api import memcache
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open(r'models/api_key.pem'))
api_key = config.get('My Section', 'api_key')

class team_stat(ndb.Model):
    team=ndb.KeyProperty()
    division=ndb.StringProperty()
    league_points=ndb.IntegerProperty()
    wins=ndb.IntegerProperty()
    queue=ndb.StringProperty()
class team(ndb.Model): #don't touch
    name = ndb.StringProperty()
    members = ndb.KeyProperty(repeated=True)
    admin = ndb.UserProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    tournaments = ndb.KeyProperty()
    color = ndb.StringProperty()
    fullId=ndb.StringProperty()
    tag=ndb.StringProperty()

class player(ndb.Model): #don't touch
    # query with player.get_by_id(id)
    name = ndb.StringProperty()
    division = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty()

class round(ndb.Model):
    round = ndb.IntegerProperty()
    games = ndb.KeyProperty(repeated=True)

class tournament(ndb.Model): #by no means final
    name = ndb.StringProperty()
    active = ndb.BooleanProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    admins = ndb.UserProperty(repeated=True)
    teams = ndb.KeyProperty(repeated=True)
    size = ndb.IntegerProperty()
    join_requests = ndb.KeyProperty(repeated=True)
    rounds = ndb.LocalStructuredProperty(round, repeated=True)
    current_round = ndb.IntegerProperty()
    winner = ndb.KeyProperty()
    finalized = ndb.BooleanProperty()
    calendar = ndb.StringProperty()
    description = ndb.KeyProperty()

class tournament_descriptions(ndb.Model):
    tournament = ndb.KeyProperty()
    description = ndb.TextProperty()

class game(ndb.Model):
    round = ndb.IntegerProperty()
    index=ndb.IntegerProperty()
    tournament = ndb.KeyProperty()
    teams = ndb.KeyProperty(repeated=True)
    happened = ndb.BooleanProperty()
    event_id = ndb.StringProperty()
    winner = ndb.KeyProperty()
    stats = ndb.JsonProperty()

class player_stats(ndb.Model):
    ranked_stats = ndb.JsonProperty()



def get_login_url(endpage):
     return users.create_login_url(endpage)




def new_team(name, admin, members):
    new_team = team(name=name, admin=admin, members=members)
    new_team.put()

def new_player(name, division, id):
    new_player = player(name=name, division=division, id=id)
    new_team.put()

        



def get_ukey(object):
    return object.key.urlsafe()

def to_key(ukey):
    key = ndb.Key(urlsafe=ukey)
    return key
def to_ukey(key):
    return key.urlsafe()

def to_id(obj):
    return obj.key.id()

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
    #take out spaces and make lower case
    sum_name_unspaced = sum_name.replace(" ", "").lower()
    try:
        #query riot
        url = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/"+sum_name_unspaced+"?api_key="+api_key
        result = json.loads(urllib2.urlopen(url).read())
        return result[sum_name_unspaced]['id']
    except urllib2.URLError, e:
        logging.info(e.code)
        if e.code == "429":
            logging.info("sleep")
            time.sleep(5)
            get_sum_id(sum_name)
        else:
            return False
        print 'you got an error with the code', e
        
        
    except:
        return False
    #return the summoner_id
    
def rank_to_url(division):
    if division=="empty":
        return ""
    rank_switch = {"I":"1","II":"2","III":"3","IV":"4","V":"5"}
    if division != "Unranked":
        division = division.split(" ")
        lowercase=division[0].lower()
        new_rank = lowercase+"_"+rank_switch[division[1]]
        return "http://lkimg.zamimg.com/images/medals/"+new_rank+".png"
    else:
        return "http://lkimg.zamimg.com/images/medals/placing.png"


def create_team_players(user, team_id):
    team_json = get_team_by_id(team_id)
    team_name=team_json["name"]
    team_tag=team_json["tag"]
    player_keys=[]
    for member in team_json["roster"]["memberList"]:
        sum_id=member["playerId"]
        player_json=get_player_by_id(sum_id)
        name=player_json["name"]
        try:
            oldplayer = player.get_by_id(sum_id)
        except:
            oldplayer = False
        if(oldplayer):
            player_keys.append(oldplayer.key)
        else:
            new_player=player(name=name, id=int(sum_id), division="empty")
            player_key=new_player.put()
            player_keys.append(player_key)
            try:
                taskqueue.add(countdown=20,name="player"+str(player_key.id())+str(datetime.date.today()), queue_name="riot", url='/queue/player_stats', params={'id': player_key.id()})
            except TombstonedTaskError, e:
                logging.info("error")
        time.sleep(1)
    new_team = team(name=team_name,members=player_keys,admin=user,fullId=team_id,tag=team_tag)
    new_team_key = new_team.put()
    get_team_stats(team_id,new_team_key)
    return new_team_key

def check_name_team(team_name):
    query = team.query(team.name==team_name).fetch()
    logging.info(len(query))
    if(len(query)>0):
        return False
    else:
        return True

def build_calendar_service():
    scope = 'https://www.googleapis.com/auth/calendar'
    credentials = AppAssertionCredentials(scope=scope)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def get_list_of_teams(summoner_id):
    #query riot
    url = "https://na.api.pvp.net/api/lol/na/v2.3/team/by-summoner/"+str(summoner_id)+"?api_key="+api_key
    result = json.loads(urllib2.urlopen(url).read())
    output=[]
    for team in result[str(summoner_id)]:
        output.append({"id":team["fullId"],"name":team["name"]})
    return output
    #return the summoner_id
def get_team_by_id(team_id):
    #query riot
    url = "https://na.api.pvp.net/api/lol/na/v2.3/team/"+str(team_id)+"?api_key="+api_key
    result = json.loads(urllib2.urlopen(url).read())
    return result[str(team_id)]
def get_player_by_id(player_id):
    
    #query riot
    for try_url in range(0,5):
        try:
            url = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/"+str(player_id)+"?api_key="+api_key
            result = json.loads(urllib2.urlopen(url).read())
            break
        except urllib2.URLError, e:
            logging.info(e.code)
            handle_riot_codes(e.code)
            if e.code == "429":
                logging.info("sleep")
                time.sleep(5)
            else:
                return False
        except:
            return False
    return result[str(player_id)]
def get_team_stats(team_id, team_key):
    for try_url in range(0,5):
        try:
            url = "https://na.api.pvp.net/api/lol/na/v2.4/league/by-team/"+str(team_id)+"/entry?api_key="+api_key
            result = json.loads(urllib2.urlopen(url).read())
            break
        except urllib2.URLError, e:
            logging.info(e.code)
            handle_riot_codes(e.code)
            if e.code == "429":
                logging.info("sleep")
                time.sleep(5)
            else:
                return
        except:
            return
    results=result[team_id]
    for array in results:
        league_points=array["entries"][0]["leaguePoints"]
        division=array["entries"][0]["division"]
        wins=array["entries"][0]["wins"]
        tier=array["tier"]
        queue=array["queue"]
        division=tier+" "+division
        #stats = team_stat.query(team_stat.team==team_key).fetch()
        #check for old stats
        new_team_stats=team_stat(team=team_key,league_points=league_points,division=division,wins=wins,queue=queue)
        new_team_stats.put()
def check_rune_page(summoner_id, string_check):
    url="https://na.api.pvp.net/api/lol/na/v1.4/summoner/"+str(summoner_id)+"/runes?api_key="+api_key
    result = json.loads(urllib2.urlopen(url).read())
    runes=result[str(summoner_id)]["pages"]
    check=False
    for rune_page in runes:
        if(rune_page["name"]==string_check):
            check=True
    return check
def handle_riot_codes(code):
    if code=="400":
        logging.info("bad request")
    elif code=="401":
        logging.info("Unauthorized")
    elif code=="404":
        logging.info("Not Found")
    elif code=="429":
        logging.info("Rate Limit Exceded")
    elif code=="500":
        logging.info("Internal Service Error")
    elif code=="503":
        logging.info("Service Unavailable")
    else:
        logging.info("unknown url error code")


    return result[str(player_id)]
