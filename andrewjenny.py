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
          'year': 2017,
          'events': [
            {
              'title': 'Vacation to Mexico & Aruba',
              'date': '2017/12/26',
              'score': 5,
              'category': 'travel'
            },
          ]
        },
        {
          'year': 2016,
          'events': [
            {
              'title': 'Engagement at Table Mountain',
              'date': '2016/04/15',
              'score': 9,
              'category': 'relationship'
            },
          ]
        },
        {
          'year': 2015,
          'events': [
            {
              'title': 'Vacation to Turkey',
              'date': '2015/12/28',
              'score': 7,
              'category': 'travel'
            },
            {
              'title': 'Vacation to Victoria & Vancouver',
              'date': '2015/05/09',
              'score': 5,
              'category': 'travel'
            },
            {
              'title': 'test',
              'date': '2015/99/99',
              'score': 1,
              'category': 'test'
            },
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
