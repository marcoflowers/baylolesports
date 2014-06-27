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
        self.login()
        #key = to_key(ukey)
        #tournament = key_object(key)
        #template = JINJA_ENVIRONMENT.get_template('/templates/tournament/bracket_%s.html' % tournament.size)
        template = JINJA_ENVIRONMENT.get_template('/templates/tournament/bracket_experiment.html')
        self.response.write(template.render(self.template_values))


class index(BaseHandler):
    def get(self, key):
        #query = tournament.query(active=True).order(-tournament.created)
        #for tournament in query.fetch():
        self.login()
            
        template = JINJA_ENVIRONMENT.get_template('/templates/tournament/index.html')
        self.response.write(template.render(self.template_values))



