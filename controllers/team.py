from base import BaseHandler
import json
from models.models import *

class index(BaseHandler):
    def get(self):
        self.login()

        teams = team.query().fetch(limit=5)

        template_values={
        "teams":teams,
        }
        self.render_template('/templates/team/index.html', template_values)


class team_page(BaseHandler):
    def get(self, id):
        self.login()

        teamo = team.get_by_id(int(id))
        div_urls=[]
        for member in teamo.members:
            div_urls.append(rank_to_url(key_object(member).division))
        template_values={
            "team":teamo,
            "div_urls":json.dumps(div_urls),
        }

        self.render_template('/templates/team/team_page.html', template_values)

class new_team(BaseHandler):
    def get(self):
        self.login()
        user = users.get_current_user()
        if user:
            template_values={}
            self.render_template('/templates/team/new_team.html', template_values)
        else:
            self.redirect(get_login_url("/team/new_team"))
        
    def post(self):
        user = users.get_current_user()
        team_name=self.request.get("team_name")
        player_names=[]
        #get player names
        for x in range(1,8):
            name=self.request.get("player"+str(x))
            if name !="":
                player_names.append(name)
        new_team_key=create_team_players(user, player_names, team_name)
        self.redirect("/team/"+str(new_team_key.id()))


class admin_page(BaseHandler):
    def get(self):
        self.login()



        template_values={}
        self.render_template('/templates/team/new_team.html', template_values)

class check_summoner_name(BaseHandler):
    def get(self, name, position):
        logging.info("check_summoner_name")
        self.response.out.write(json.dumps({"id":get_sum_id(name), "position":position}));

class get_team(BaseHandler):
    def get (self, type, input):
        output={"teams":[]}
        if(type=="Name"):
            teams = team.query(team.name==input).fetch()
            for group in teams:
                output["teams"].append({"name":group.name, "id":group.key.id()})
        elif type=="Team Member":
            all_teams = team.query().fetch()
            teams=[]
            for teamo in all_teams:
                for member in teamo.members:
                    if(key_object(member).name.lower()==input.lower()):
                        teams.append(teamo)
            for group in teams:
                output["teams"].append({"name":group.name, "id":group.key.id()})
        else:
            output["error"]="not_valid"
        self.response.out.write(json.dumps(output))
class check_team_name_handler(BaseHandler):
    def get(self, name):
        logging.info(check_name_team(name))
        self.response.out.write(json.dumps({"name":check_name_team(name)}));