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
from oauth2client import appengine
from controllers import home, team, tournament, calendar
import httplib2
import logging
import os
from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache






CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'controllers/client_secrets.json')

MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS

decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=MISSING_CLIENT_SECRETS_MESSAGE)

app = webapp2.WSGIApplication([
    ('/', home.index),
    ('/team/check_summoner_name/(.*)/(.*)', team.check_summoner_name),
    ('/team/new_team', team.new_team),
    ('/team/(.*)', team.team_page),
    ('/team/', team.index),
    ('/tournament/check_name/(.*)', tournament.check_name),
    ('/tournament/new', tournament.new_tournament),
    ('/tournament/index', tournament.index),
    ('/tournament/admin/(.*)', tournament.admin_page),
    ('/schedule/authorize', calendar.calendar),
    ('/schedule/add_schedule', calendar.add_calendar),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
