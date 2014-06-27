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
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape']
)

class BaseHandler(webapp2.RequestHandler):
	def render_template(self, file_name, params={}):
		params.update(self.template_values)
		logging.info("HELLOOOOO")
		logging.info(params)
		template = JINJA_ENVIRONMENT.get_template(file_name)
		self.response.write(template.render(params))

	def login(self):
		user = users.get_current_user()
		if user:
		    message = user.nickname()
		    url = users.create_logout_url()
		    url_text = "Logout"
		else:
		    message = ''
		    url = users.create_login_url()
		    url_text = "Login"


		self.template_values = {
		    'message':message,
		    'url':url,
		    'url_text':url_text,
		    'key_object':key_object,
		    'keys_objects':keys_objects,
		    'rank_to_url':rank_to_url,
		}
