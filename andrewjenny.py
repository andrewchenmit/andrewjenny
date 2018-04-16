import json
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

class Photobooth(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    template = JINJA_ENVIRONMENT.get_template('photobooth.html')
    self.response.write(template.render(template_values))

class Share(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    template = JINJA_ENVIRONMENT.get_template('share.html')
    self.response.write(template.render(template_values))

class Life(webapp2.RequestHandler):
  def get(self):
    with open('life/events.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('life/life.html')
    self.response.write(template.render(template_values))

class Timeline(webapp2.RequestHandler):
  def get(self):
    with open('timeline/events.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('timeline/timeline.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/photobooth', Photobooth),
    ('/share', Share),
    ('/life', Life),
    ('/timeline', Timeline)
], debug=True)
