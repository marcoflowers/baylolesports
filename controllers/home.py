from google.appengine.ext import ndb
import jinja2
from jinja2 import Environment, FileSystemLoader
import webapp2
import os
import urllib2
import urllib
from datetime import *
import json
import unicodedata
import logging
import time
from base import BaseHandler


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(''),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class index(BaseHandler):
    
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('/templates/home/index.html')
		self.response.write(template.render(template_values))
