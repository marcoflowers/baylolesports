import webapp2
import os
from models.models import *
import jinja2
import logging
from base import BaseHandler
import json
from google.appengine.api import users
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape']
)



class map(BaseHandler):
    def get(self):
        self.login()
        self.render_template('/templates/admin/index.html', {})
