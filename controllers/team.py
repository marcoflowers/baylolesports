from base import BaseHandler
import json
from models.models import *

class index(BaseHandler):
    def get(self):
        self.login()

        template_values={}
        self.render_template('/templates/team/team_page.html', template_values)


        template = JINJA_ENVIRONMENT.get_template('/templates/team/new_team.html')
        self.response.write(template.render(template_values))


class team_page(BaseHandler):
    def get(self, id):
        self.login()

        teamo = team.get_by_id(int(id))
        template_values={
            "team":teamo
        }

        self.render_template('/templates/team/team_page.html', template_values)

class new_team(BaseHandler):
    def get(self):
        self.login()

        template_values={}
        self.render_template('/templates/team/new_team.html', template_values)
    def post(self):
        team_name=self.request.get("team_name")
        player_names=[]
        #get player names
        for x in range(1,8):
            name=self.request.get("player"+str(x))
            if name !="":
                player_names.append(name)
        player_keys=[]
        for player_name in player_names:
            sum_id = get_sum_id(player_name)
            summoner_rank=get_summoner_rank(sum_id)
            try:
                oldplayer = player.get_by_id(sum_id)
            except:
                oldplayer = False
            if(oldplayer):
                player_keys.append(oldplayer.key)
            else:
                new_player=player(name=player_name, id=int(sum_id), division=summoner_rank)
                player_keys.append(new_player.put())
        new_team = team(name=team_name,members=player_keys )
        new_team_key = new_team.put()
        self.redirect("/team/"+str(new_team_key.id()))


class admin_page(BaseHandler):
    def get(self):
        self.login()



        template_values={}
        self.render_template('/templates/team/new_team.html', template_values)

class check_summoner_name(BaseHandler):
    def get(self, name, position):
        self.response.out.write(json.dumps({"id":get_sum_id(name), "position":position}));
