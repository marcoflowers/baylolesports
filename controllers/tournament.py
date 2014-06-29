import webapp2
import os
from models.models import *
import jinja2
import logging
from base import BaseHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape']
)



class tournament_page(BaseHandler):
    def get(self, ukey):
        key = to_key(ukey)
        #tournament = key_object(key)
        #size = ukey
        #self.render_template('/templates/tournament/bracket_%s.html' % size, template_values)

           


    def post(self, ukey):
        logging.info("Data Saved")
        self.redirect(self.request.uri)



class index(BaseHandler):
    def get(self):
        #query = tournament.query(active=True).order(-tournament.created)
        #template_values = {"tournaments", query.fetch()}
        template_values={}
        self.render_template('/templates/tournament/index.html', template_values) 



