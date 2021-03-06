import sys
sys.path.insert(0, "libs")

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
import httplib2
import logging
import os

PRODUCTION_MODE = not os.environ.get(
    'SERVER_SOFTWARE', 'Development').startswith('Development')
if not PRODUCTION_MODE:
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']
# to allow service building, run appserver with this command:
# python $gae/dev_appserver.py ~/projects/baylolesports/ --appidentity_email_address=64791344032-c65sddh2n9opu1peb8f2nlkr9rhsvr6e@developer.gserviceaccount.com --appidentity_private_key_path=/home/adrian/projects/baylolesports/models/private_key.pem
#dev_appserver.py baylolesports2 --appidentity_email_address=64791344032-c65sddh2n9opu1peb8f2nlkr9rhsvr6e@developer.gserviceaccount.com --appidentity_private_key_path=baylolesports2/models/private_key.pem
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'maqFDAFDSFS3132',
}

app = webapp2.WSGIApplication([
    ('/', home.index),
    ('/team/get_more_teams', team.get_more_teams),
    ('/team/set_session_sum_name',team.set_session_sum_name),
    ('/team/check_rune', team.check_rune),
    ('/team/admin/(.*)', team.admin),
    ('/team/check_team_name/(.*)', team.check_team_name_handler),
    ('/team/return_list_of_teams', team.return_list_of_teams),
    ('/team/check_summoner_name/(.*)/(.*)', team.check_summoner_name),
    ('/team/new_team', team.new_team),
    ('/team/get_team/(.*)/(.*)', team.get_team),
    ('/team/(.*)', team.team_page),
    ('/team', team.index),
    ('/queue/update_stats', queue.update_stats),
    ('/queue/player_stats', queue.player_stats_handler),
    ('/tournament/events', tournament.events),
    ('/tournament/check_name/(.*)', tournament.check_name),
    ('/tournament/new', tournament.new_tournament),
    ('/tournament/index', tournament.index),
    #('/tournament/post/(.*)', tournament.post),
    ('/tournament/admin/(.*)', tournament.admin_page),
    ('/tournament/(.*)', tournament.display_tournament),
], debug=True, config=config)
