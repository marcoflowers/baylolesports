from base import BaseHandler
import json
from models.models import *
from google.appengine.api import mail

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
        message = mail.EmailMessage(sender="marco.flowers12@gmail.com",subject="Welcome to Baylolesports")
        message.to = user.email()
        message.body = """
        Hello,

        Welcome to Baylolesports

        -The Baylolesports Team
        """

        message.send()
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
        teams=[]
        output={"teams":[]}
        if(type=="Team Name "):
            teams = team.query(team.name==input).fetch()
        elif type=="Team Member ":
            all_teams = team.query().fetch()
            teams=[]
            for teamo in all_teams:
                for member in teamo.members:
                    if(key_object(member).name.lower()==input.lower()):
                        teams.append(teamo)
        else:
            output["error"]="not_valid"
        for group in teams:
            players=[]
            for member in group.members:
                players.append(key_object(member).name)
            output["teams"].append({"name":group.name, "id":group.key.id(), "players":players})
        
        self.response.out.write(json.dumps(output))
class check_team_name_handler(BaseHandler):
    def get(self, name):
        logging.info(check_name_team(name))
        self.response.out.write(json.dumps({"name":check_name_team(name)}));
class get_more_teams(BaseHandler):
    def post(self):
        output={"teams":[]}
        current_teams=json.loads(self.request.get("current_teams"))
        logging.info
        teams = team.query().fetch()
        count=0
        for teamo in teams:
            if count==5:
                break
            check=True
            for current_team in current_teams:
                logging.info(teamo.key.id())
                logging.info(current_team)
                logging.info("------")
                if teamo.key.id() == int(current_team):
                    check=False
                    logging.info(teamo.name)
            if (check):
                players=[]
                for member in teamo.members:
                    players.append(key_object(member).name)
                output["teams"].append({"name":teamo.name, "id":teamo.key.id(), "players":players})
                count=count+1
        logging.info(output)
        self.response.out.write(json.dumps(output))
