import httplib2
import logging
import os
from apiclient import discovery
from oauth2client.appengine import AppAssertionCredentials
from oauth2client import appengine
from oauth2client import client
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from google.appengine.api import memcache
from oauth2client.appengine import CredentialsProperty
from google.appengine.ext import ndb
from oauth2client.appengine import StorageByKeyName
from google.appengine.api import users

import webapp2
import jinja2
from models import *
from base import BaseHandler
#https://developers.google.com/api-client-library/python/guide/google_app_engine#Flows
#https://developers.google.com/google-apps/calendar/v1/developers_guide_python
#https://google-api-client-libraries.appspot.com/documentation/calendar/v3/python/latest/



class Credentials(ndb.Model):
  credentials = CredentialsProperty()


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')


MISSING_CLIENT_SECRETS_MESSAGE = """
%s
""" % CLIENT_SECRETS
scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ]
user = users.get_current_user()
if(user):
    storage = StorageByKeyName(Credentials, user.user_id(), 'credentials')
    credentials = storage.get()
#http = credentials.authorize(httplib2.Http(memcache))
#service = discovery.build('calendar', 'v3', http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=scope,
    message=MISSING_CLIENT_SECRETS_MESSAGE)


class calendar(BaseHandler):
    @decorator.oauth_aware
    def get(self):
        self.login()
        if(decorator.has_credentials()):
            logging.info("Has Credentials")
            self.redirect("/tournament/4")
        else:
            logging.info("No Credentials")
            self.redirect(decorator.authorize_url())


class add_calendar(BaseHandler):
    @decorator.oauth_aware
    def get(self):
        self.login()
        if(decorator.has_credentials()):
            try:
                request = service.events().list(calendarId='primary')
                while request != None:
                    response = request.execute()
                    for event in response.get('items', []):
                        print repr(event.get('summary', 'NO SUMMARY')) + '\n'
                    request = service.events().list_next(request, response)
            except AccessTokenRefreshError:
                print "Oauth2 error"

