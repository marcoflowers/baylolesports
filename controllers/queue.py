from base import BaseHandler
import json
from models.models import *
import os
import time

from google.appengine.api import taskqueue
from google.appengine.ext import ndb
import datetime



class update_stats(BaseHandler):
    def get(self):
        teams = team.query().fetch(100)
        for teamo in teams:
            for memberk in teamo.members:
                member_id = memberk.id()
                member_stats=[]
                try:
                    member_stats = player_stats.query(player=memberk).fetch()
                except:
                    print "excepted"
                if(len(member_stats)>0):
                    continue
                else:
                    try:
                        taskqueue.add(name="player"+str(member_id)+str(datetime.date.today()), queue_name="riot", url='/queue/player_stats', params={'id': member_id})
                    except:
                        logging.info("same_as_other_task")


class player_stats_handler(BaseHandler):
    def post(self):
        player_id = int(self.request.get("id"))
        key = player.get_by_id(player_id).key
        @ndb.transactional
        def get_stats():
            api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
            if player_stats.get_by_id(player_id):
                return
            #take out spaces and make lower case
            try:
                #query riot
                url = "https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/"+str(player_id)+"/summary?season=SEASON4&api_key="+api_key
                response=urllib2.urlopen(url)
                result = json.loads(response.read())
                queue_stats = result["playerStatSummaries"]
                for summary in queue_stats:
                    if(summary["playerStatSummaryType"]=="RankedSolo5x5"):
                        new_player_stats = player_stats(id=player_id, ranked_stats=summary["aggregatedStats"])
                        new_player_stats.put()
            except urllib2.URLError, e:
                time.sleep(5)
                get_stats()
            except:
                logging.info("other error")
        @ndb.transactional
        def get_summoner_rank():
            api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
            playero = player.get_by_id(player_id)
            try:
                url = 'https://na.api.pvp.net/api/lol/na/v2.4/league/by-summoner/' + str(player_id) + '?api_key=' + api_key
                result = json.loads(urllib2.urlopen(url).read())
                for queue in result[str(player_id)]:
                    if queue["queue"]=="RANKED_SOLO_5x5":
                        tier = queue["tier"]
                        for entry in queue["entries"]:
                            if entry['playerOrTeamId'] == str(player_id):
                                number = entry['division']
                                rank = tier.title() + ' ' + number
                playero.division=rank
                playero.put()
                logging.info("gucci")
            except urllib2.URLError, e:
                if(e.code=="404"):
                    playero.division="Unranked"
                    playero.put()
                    logging.info("404")
                elif e.code=="429":
                    time.sleep(5)
                    get_summoner_rank(summoner_id)
                    logging.info("429")
                else:
                    playero.division="Unranked"
                    playero.put()
                    logging.info("otherother")
            except:
                playero.division="Unranked"
                playero.put()
                logging.info("other")
        get_summoner_rank()
        get_stats()