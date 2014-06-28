from base import BaseHandler
import json
from models.models import *
import os
import time

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from google.appengine.api import taskqueue


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
                        taskqueue.add(name=str(member_id), queue_name="pstats", url='/queue/player_stats', params={'id': member_id})
                    except:
                        logging.info("same_as_other_task")


class player_stats_handler(BaseHandler):
    def post(self):
        player_id = int(self.request.get("id"))
        key = player.get_by_id(player_id).key
        logging.info(key)
        @ndb.transactional
        def get_stats():
            api_key="655fefc4-c614-420f-895c-893e2c8b9aee"
            #take out spaces and make lower case
            try:
                #query riot
                url = "https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/"+str(player_id)+"/summary?season=SEASON4&api_key="+api_key
                response=urllib2.urlopen(url)
                print response.getcode()
                result = json.loads(response.read())
                queue_stats = result["playerStatSummaries"]
                for summary in queue_stats:
                    if(summary["playerStatSummaryType"]=="RankedSolo5x5"):
                        logging.info(summary["aggregatedStats"])
                        new_player_stats = player_stats(id=player_id, ranked_stats=summary["aggregatedStats"])
                        new_player_stats.put()
            except urllib2.URLError, e:
                time.sleep(5)
                get_stats()
        get_stats()