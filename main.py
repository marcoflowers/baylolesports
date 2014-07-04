from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
import jinja2
from jinja2 import Environment, FileSystemLoader
import webapp2
import os
import urllib2
import urllib
from datetime import *
import json
import unicodedata
from webob import Request
from google.appengine.api import mail
import logging
import time

from controllers import home, team, tournament, queue



app = webapp2.WSGIApplication([
    ('/', home.index),
    ('/team/get_more_teams', team.get_more_teams),
    ('/team/admin/(.*)', team.admin),
    ('/team/check_team_name/(.*)', team.check_team_name_handler),
    ('/team/check_summoner_name/(.*)/(.*)', team.check_summoner_name),
    ('/team/new_team', team.new_team),
    ('/team/get_team/(.*)/(.*)', team.get_team),
    ('/team/(.*)', team.team_page),
    ('/tournament/(.*)', tournament.tournament_page),
    ('/tournament_index', tournament.index),
    ('/team', team.index),
    ('/queue/update_stats', queue.update_stats),
    ('/queue/player_stats', queue.player_stats_handler),
], debug=True)