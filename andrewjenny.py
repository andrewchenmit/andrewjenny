import bcrypt
import datetime
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

class Story(webapp2.RequestHandler):
  def post(self):
    hashed_pass1 = '$2a$02$CuYXjCoFCfe/wLsHB67AzuLSxOUOldxQ1/j.IOIiH1uaaW0SLx8v6'
    hashed_pass2 = '$2a$02$ajup6q7vDIT7.6Z.AYtNnOBDRW0XQgEaGGfLEFd1nx7DdVMNN4jCO'
    if bcrypt.hashpw(self.request.get('password'), hashed_pass1) == hashed_pass1 or bcrypt.hashpw(self.request.get('password'), hashed_pass2) == hashed_pass2:
      with open('pages/story/data.json') as json_data:
        events = json.load(json_data)
      template_values = events
      template = JINJA_ENVIRONMENT.get_template('pages/story/index.html')
      self.response.write(template.render(template_values))
    else:
      self.get('visible')

  def get(self, error_visibility=None):
    template_values = {'error_visibility': error_visibility}
    template = JINJA_ENVIRONMENT.get_template('pages/story/login.html')
    self.response.write(template.render(template_values))

class Bday(webapp2.RequestHandler):
  def get(self):
    template_values = {'disabled': 'disabled', 'url': ''}
    timenow = datetime.datetime.now()-datetime.timedelta(hours=8)
    timethreshold = datetime.datetime(year=2021, month=02, day=15, hour=13, minute=0, second=0, microsecond=0)
    correcttime = timenow >= timethreshold
    print correcttime
    print "now", timenow
    print "threshold", timethreshold
    if correcttime:
      template_values['disabled'] = 'enabled'
      template_values['url'] = 'https://fb.zoom.us/j/8191834030?pwd=c2RIT2NVNnNEenpxTFhHZVFJdUF1Zz09'
    template = JINJA_ENVIRONMENT.get_template('pages/bday/index.html')
    self.response.write(template.render(template_values))

class Vday(webapp2.RequestHandler):
  def post(self):
    form = None
    with open('pages/vday/data.json') as json_data:
      messages = json.load(json_data)
    template_values = messages
    key = self.request.get('key').lower().replace('il', '').replace('#', '').replace('\'','').replace('chicken', '').replace('zoo', '').replace(' ', '')
    last = self.request.get('last')
    print(key)
    if key in messages.keys():
      if key == 'duomo':
        form = 'hidden'
      self.get(messages[key], None, form)
    else:
      self.get(last, 'visible')

  def get(self, message=None, wrong=None, form=None):
    with open('pages/vday/data.json') as json_data:
      messages = json.load(json_data)
    timenow = datetime.datetime.now()-datetime.timedelta(hours=8)
    timethreshold = datetime.datetime(year=2021, month=02, day=14, hour=12, minute=0, second=0, microsecond=0)
    correcttime = timenow >= timethreshold
    print correcttime
    print "now", timenow
    print "threshold", timethreshold
    if not correcttime:
      message = messages['early']
      form = 'hidden'
    else:
      if message == None:
        message = messages['default']
    template_values = {'wrong': wrong, 'message': message, 'form': form}
    template = JINJA_ENVIRONMENT.get_template('pages/vday/index.html')
    self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/photobooth', Photobooth),
    ('/share', Share),
    ('/life', Life),
    ('/timeline', Timeline),
    ('/christmas', Christmas),
    ('/story', Story),
    ('/bday', Bday),
    ('/vday', Vday)
], debug=True)
