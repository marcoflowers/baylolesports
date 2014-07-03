
***git***
    only push a deployable app to master
    develop should only have changes that are for everyone
    branch features off of develop
        git checkout -b feature develop
    push features as branches while you work on them
    close features when complete
        git checkout develop
        git merge feature
        git branch -d feature
        git push origin develop

FOLLOW GOOGLE'S STYLE GUIDE

Style Guide
Forms col-md-6(offset 3 to be centered)
Tourney/Team pages(col-md-3(sidebar) and col-md-9(main content))
Index Pages col-md-6 offset 3

To Do:
(Everything)


controllers extend BaseHandler (in controllers/base.py)
    use self.render_template()

Build a framework that allows for expansion and revision

Brainstorm and finalize ndb models
	Split up models.py, its going to get pretty big

Incorporate Javascript(AJAX)=JSON encoding

Brainstorm Integration with Riot API
	(and how to adhere to their rate-limiting), Maybe just pull most of the data during chron jobs where we can wait as long as we want and no one cares(like stats)



Templates to create:

teams/
    team_page.html
    index.html
    new_team.html|almost done|
    admin_page.html
    check_summoner_name(ajax call to make sure the summoner_name is good)
home/
	index

Tournament Tasklist
Index
View
