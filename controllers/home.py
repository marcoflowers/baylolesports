from base import BaseHandler
import json
from models.models import *



class index(BaseHandler):
    def get(self):
        self.login()

        template_values={
        }
        self.render_template('/templates/home/index.html', template_values)


