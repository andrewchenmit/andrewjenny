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
    template = JINJA_ENVIRONMENT.get_template('pages/photobooth/photobooth.html')
    self.response.write(template.render(template_values))

class Share(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    template = JINJA_ENVIRONMENT.get_template('pages/share/share.html')
    self.response.write(template.render(template_values))

class Life(webapp2.RequestHandler):
  def get(self):
    with open('pages/life/events.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('pages/life/life.html')
    self.response.write(template.render(template_values))

class Timeline(webapp2.RequestHandler):
  def get(self):
    with open('pages/timeline/events.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('pages/timeline/timeline.html')
    self.response.write(template.render(template_values))

class Christmas(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    template = JINJA_ENVIRONMENT.get_template('pages/xmas2019/index.html')
    self.response.write(template.render(template_values))

class StoryCategories(webapp2.RequestHandler):
  def get(self):
    with open('pages/story/categories.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('pages/story/categories.html')
    self.response.write(template.render(template_values))

class StoryYears(webapp2.RequestHandler):
  def get(self):
    with open('pages/story/years.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('pages/story/years.html')
    self.response.write(template.render(template_values))

class Story(webapp2.RequestHandler):
  def get(self):
    with open('pages/story/categories.json') as json_data:
      events = json.load(json_data)
    template_values = events
    template = JINJA_ENVIRONMENT.get_template('pages/story/index.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/photobooth', Photobooth),
    ('/share', Share),
    ('/life', Life),
    ('/timeline', Timeline),
    ('/christmas', Christmas),
    ('/story', Story),
    ('/story/categories', StoryCategories),
    ('/story/years', StoryYears)
], debug=True)
