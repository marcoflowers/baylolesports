from google.appengine.ext import ndb
import logging
from google.appengine.api import users
import json
import urllib
import urllib2
import time
from google.appengine.api import taskqueue
import datetime


class team(ndb.Model): #don't touch
    name = ndb.StringProperty()
    members = ndb.KeyProperty(repeated=True)
    admin = ndb.UserProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    color = ndb.StringProperty()

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
    return ndb.Key(urlsafe=ukey)

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
    api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
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


def create_team_players(user, player_names, team_name,team_color):
    player_keys=[]
    for player_name in player_names:
        sum_id = get_sum_id(player_name)
        logging.info("gotdata")
        try:
            oldplayer = player.get_by_id(sum_id)
        except:
            oldplayer = False
        if(oldplayer):
            player_keys.append(oldplayer.key)
        else:
            new_player=player(name=player_name, id=int(sum_id), division="empty")
            player_key=new_player.put()
            player_keys.append(player_key)
            taskqueue.add(countdown=20,name="player"+str(player_key.id())+str(datetime.date.today()), queue_name="riot", url='/queue/player_stats', params={'id': player_key.id()})
    new_team = team(name=team_name,members=player_keys,admin=user, color=team_color)
    new_team_key = new_team.put()
    return new_team_key

def check_name_team(team_name):
    query = team.query(team.name==team_name).fetch()
    logging.info(len(query))
    if(len(query)>0):
        return False
    else:
        return True
