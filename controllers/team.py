from base import BaseHandler
import json
from models.models import *
from google.appengine.api import mail
import cgi

class index(BaseHandler):
    def get(self):
        self.login()

        teams = team.query().fetch(limit=5)

        template_values={
        "teams":teams,
        }
        self.render_template('/templates/team/index.html', template_values)

class admin(BaseHandler):
    def get(self, id):
        self.login()
        teamo = team.get_by_id(int(id))
        if not self.user:
            self.redirect(get_login_url("/team/admin/"+id))
        if self.user==teamo.admin:
            

            template_values={
            "team":teamo,
            }
            self.render_template('/templates/team/admin_page.html', template_values)
        else:
             self.redirect("/team/"+id)
        


class team_page(BaseHandler):
    def get(self, id):
        self.login()

        teamo = team.get_by_id(int(id))
        div_urls=[]
        for member in teamo.members:
            div_urls.append(rank_to_url(key_object(member).division))
        logging.info(self.user)
        logging.info(teamo.admin)
        team_stats = team_stat.query(team_stat.team==teamo.key).fetch()
        if(len(team_stats)<=0):
            team_stats=False
        
        if self.user==teamo.admin:
            admin=1
        else:
            admin=2
        logging.info(admin)
        template_values={
            "team":teamo,
            "div_urls":json.dumps(div_urls),
            "admin":admin,
            "team_stats":team_stats
        }

        self.render_template('/templates/team/team_page.html', template_values)

class new_team(BaseHandler):
    def get(self):
        self.login()
        user = users.get_current_user()
        if user:
            template_values={}
            self.render_template('/templates/team/new_team2.html', template_values)
        else:
            self.redirect(get_login_url("/team/new_team"))
        
    def post(self):
        user = users.get_current_user()
        team_id=cgi.escape(self.request.get("optionsRadios"))
        new_team_key=create_team_players(user, team_id)
        message = mail.EmailMessage(sender="marco.flowers12@gmail.com",subject="Welcome to Baylolesports")
        message.to = user.email()
        message.body = """
        Hello,

        Welcome to Baylolesports

        -The Baylolesports Team
        """

        message.send()
        self.redirect("/team/"+str(new_team_key.id()))

class check_summoner_name(BaseHandler):
    def get(self, name, position):
        logging.info("check_summoner_name")
        self.response.out.write(json.dumps({"id":get_sum_id(name), "position":position}));

class get_team(BaseHandler):
    def get (self, type, input):
        teams=[]
        output={"teams":[]}
        
        if(input=="dfskldfkdssdfklsdfkl"):
            teams = team.query().fetch(limit=5)
        elif(type=="Team Name "):
            all_teams = team.query().fetch()
            teams=[]
            for teamo in all_teams:
                if(input in teamo.name):
                    teams.append(teamo)
        elif type=="Team Member ":
            all_teams = team.query().fetch()
            teams=[]
            teams=[]
            for teamo in all_teams:
                for member in teamo.members:
                    if(input.lower() in key_object(member).name.lower() ):
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

class add_member(BaseHandler):
    def post(self, id):
        self.login()
        logging.info(id)
        teamo = team.get_by_id(int(id))
        if not self.user:
            self.redirect(get_login_url("/team/admin/"+id))
        if self.user==teamo.admin:
            player_name=self.request.get("form")
            player_name=player_name[8:]
            logging.info(player_name)
            teamo.members.append(create_player(player_name))
            teamo.put()
        self.response.out.write(json.dumps("1"))

class delete_member(BaseHandler):
    def post(self, id):
        self.login()
        logging.info(id)
        teamo = team.get_by_id(int(id))
        if not self.user:
            self.redirect(get_login_url("/team/admin/"+id))
        if self.user==teamo.admin:
            player_id=self.request.get("member_id")
            logging.info(player.get_by_id(int(player_id)))
            teamo.members.remove(player.get_by_id(int(player_id)).key)
            teamo.put()
        self.response.out.write(json.dumps("1"))


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
class return_list_of_teams(BaseHandler):
    def post(self):
        self.login()
        #get summoner name
        name=json.loads(self.request.get("name"))
        if not self.user:
            self.redirect(get_login_url("/team/admin/"+id))
        #get summoner id
        summoner_id=get_sum_id(name)
        #get list of teams
        teams = get_list_of_teams(summoner_id)
        #remove any that are already teams
        for teamo in teams:
            if(team.query(team.name==teamo["name"]).get()):
                teams.remove(teamo)
        self.response.out.write(json.dumps(teams))
class check_rune(BaseHandler):
    def post(self):
        name=self.request.get("sum_name")
        code=self.request.get("code")
        summoner_id=get_sum_id(name)
        self.response.out.write(json.dumps(check_rune_page(summoner_id, code)))
