

FOLLOW GOOGLE'S STYLE GUIDE

To Do:
(Everything)

Think up better UI, right now its all white

There has to be some way to put the login()=login and template vals in the parent login class so we don't have to type it for every class(isnt that the point of the parent class)In the child we can just append to the template vals
^^^^^NO REPEATINGGGG
    All controllers must extend models.py. Therefore a a template_values in models.py will be in all controllers - Adrian

***From now on, all template values must be entered as template_values['key'] = value***
this will let us always have login

Build a framework that allows for expansion and revision

Brainstorm and finalize ndb models
	Split up models.py, its going to get pretty big

Brainstorm and finalize tournament filling methods (HTML5 Drag and Drop?)

Incorporate Javascript(AJAX)=JSON encoding

Brainstorm Integration with Riot API
	(and how to adhere to their rate-limiting), Maybe just pull most of the data during chron jobs where we can wait as long as we want and no one cares(like stats)


Follow MVC?(Model, View, Controller) - yes

Templates to create:

teams/
    team_page.html
    index.html
    new_team.html|almost done|
    admin_page.html
    check_summoner_name(ajax call to make sure the summoner_name is good)
home/
	index
