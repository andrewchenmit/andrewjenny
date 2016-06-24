import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        template_values = {
            'user': 'ANDREW CHENNNN',
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class RSVP(webapp2.RequestHandler):
  def post(self):
    self.response.write(self.request)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rsvphandler', RSVP),
], debug=True)
