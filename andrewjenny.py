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
    template_values = {
      'events': [
        {
          'year': 2018,
          'events': [
            'hi',
            'bye',
            'three'
          ]
        },
        {
          'year': 2017,
          'events': [
            '1',
            '2',
            '3'
          ]
        },
        {
          'year': 2016,
          'events': [
            'Woos got engaged!',
            'Woos went to South Africa!',
            'Turkey!'
          ]
        }
      ]
    }
    template = JINJA_ENVIRONMENT.get_template('life/life.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/photobooth', Photobooth),
    ('/share', Share),
    ('/life', Life)
], debug=True)
