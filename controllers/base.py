from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images
import webapp2
import os
from webob import Request
from models.models import *
import base
import jinja2
import logging
import json
from webapp2_extras import sessions
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape']
)



class BaseHandler(webapp2.RequestHandler):

    def render_template(self, file_name, params={}):
        params.update(self.template_values)
        template = JINJA_ENVIRONMENT.get_template(file_name)
        self.response.write(template.render(params))

    def login(self):
        user = users.get_current_user()
        if user:
            message = user.nickname()
            url = users.create_logout_url(self.request.uri)
            url_text = "Logout"
        else:
            message = ''
            url = users.create_login_url(self.request.uri)
            url_text = "Login"
        self.user=user

        self.template_values = {
            'message':message,
            'url':url,
            'url_text':url_text,
            'key_object':key_object,
            'keys_objects':keys_objects,
            'rank_to_url':rank_to_url,
            'get_login_url':get_login_url,
                    'get_ukey':get_ukey,
                    'key_object':key_object,
                    'to_ukey':to_ukey,
            'to_id':to_id,
        }
        if user:
            self.template_values["user"]=user

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

