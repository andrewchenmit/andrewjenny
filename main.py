from __future__ import absolute_import
from __future__ import print_function
import bcrypt
import datetime
import json
import os
import six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error

import jinja2
from flask import Flask, render_template, redirect, url_for, request

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True)

app = Flask(__name__)

@app.route("/")
def MainPage():
  print("Main Page")
  template_values = {
    'user': 'ANDREW CHENNNN',
  }
  template = JINJA_ENVIRONMENT.get_template('index.html')
  return template.render(template_values)

@app.route("/photobooth")
def Photobooth():
  template_values = {}
  template = JINJA_ENVIRONMENT.get_template('pages/photobooth/photobooth.html')
  return template.render(template_values)

@app.route("/share")
def Share():
  template_values = {}
  template = JINJA_ENVIRONMENT.get_template('pages/share/share.html')
  return template.render(template_values)

@app.route("/life")
def Life():
  with open('pages/life/events.json') as json_data:
    events = json.load(json_data)
  template_values = events
  template = JINJA_ENVIRONMENT.get_template('pages/life/life.html')
  return template.render(template_values)

@app.route("/timeline")
def Timeline():
  with open('pages/timeline/events.json') as json_data:
    events = json.load(json_data)
  template_values = events
  template = JINJA_ENVIRONMENT.get_template('pages/timeline/timeline.html')
  return template.render(template_values)

@app.route("/christmas")
def Christmas():
  template_values = {}
  template = JINJA_ENVIRONMENT.get_template('pages/xmas2019/index.html')
  return template.render(template_values)

@app.route("/xmas24")
def xmas24():
  template_values = {}
  template = JINJA_ENVIRONMENT.get_template('pages/xmas24/index.html')
  return template.render(template_values)

@app.route("/story", methods = ['POST', 'GET'])
def Story(error_visibility=None):
  if request.method == 'POST':
    hashed_pass1 = '$2a$02$CuYXjCoFCfe/wLsHB67AzuLSxOUOldxQ1/j.IOIiH1uaaW0SLx8v6'
    hashed_pass2 = '$2a$02$ajup6q7vDIT7.6Z.AYtNnOBDRW0XQgEaGGfLEFd1nx7DdVMNN4jCO'
    if bcrypt.hashpw(request.form['password'], hashed_pass1) == hashed_pass1 or bcrypt.hashpw(request.form['password'], hashed_pass2) == hashed_pass2:
      with open('pages/story/data.json') as json_data:
        events = json.load(json_data)
      template_values = events
      template = JINJA_ENVIRONMENT.get_template('pages/story/index.html')
      return template.render(template_values)
    else:
      request.method = 'GET'
      return Story(error_visibility='visible')

  if request.method == 'GET':
    template_values = {'error_visibility': error_visibility}
    template = JINJA_ENVIRONMENT.get_template('pages/story/login.html')
    return template.render(template_values)

#class Story(webapp2.RequestHandler):
#  def post(self):
#    hashed_pass1 = '$2a$02$CuYXjCoFCfe/wLsHB67AzuLSxOUOldxQ1/j.IOIiH1uaaW0SLx8v6'
#    hashed_pass2 = '$2a$02$ajup6q7vDIT7.6Z.AYtNnOBDRW0XQgEaGGfLEFd1nx7DdVMNN4jCO'
#    if bcrypt.hashpw(self.request.get('password'), hashed_pass1) == hashed_pass1 or bcrypt.hashpw(self.request.get('password'), hashed_pass2) == hashed_pass2:
#      with open('pages/story/data.json') as json_data:
#        events = json.load(json_data)
#      template_values = events
#      template = JINJA_ENVIRONMENT.get_template('pages/story/index.html')
#      self.response.write(template.render(template_values))
#    else:
#      self.get('visible')
#
#  def get(self, error_visibility=None):
#    template_values = {'error_visibility': error_visibility}
#    template = JINJA_ENVIRONMENT.get_template('pages/story/login.html')
#    self.response.write(template.render(template_values))

@app.route("/bday")
def Bday():
  template_values = {'disabled': 'disabled', 'url': ''}
  timenow = datetime.datetime.now()-datetime.timedelta(hours=8)
  timethreshold = datetime.datetime(year=2021, month=0o2, day=15, hour=13, minute=0, second=0, microsecond=0)
  correcttime = timenow >= timethreshold
  print(correcttime)
  print("now", timenow)
  print("threshold", timethreshold)
  if correcttime:
    template_values['disabled'] = 'enabled'
    template_values['url'] = 'https://fb.zoom.us/j/8191834030?pwd=c2RIT2NVNnNEenpxTFhHZVFJdUF1Zz09'
  template = JINJA_ENVIRONMENT.get_template('pages/bday/index.html')
  return template.render(template_values)

@app.route('/vday22', methods = ['POST', 'GET'])
def Vday22(message=None, wrong=None, form=None):
  if request.method == 'POST':
    form = None
    with open('pages/vday22/data.json') as json_data:
      messages = json.load(json_data)
    template_values = messages
    key = request.form['key'].lower().replace('50', '5').replace(',', '').replace('#', '').replace('\'','').replace('chicken', '').replace('zoo', '').replace(' ', '')
    last = request.form['last']
    if key in list(messages.keys()):
      if key == 'jenny':
        form = 'hidden'
      request.method = 'GET'
      return Vday22(message=messages[key], wrong=None, form=form)
    else:
      request.method = 'GET'
      return Vday22(message=last, wrong='visible')

  if request.method == 'GET':
    with open('pages/vday22/data.json') as json_data:
      messages = json.load(json_data)
    timenow = datetime.datetime.now()-datetime.timedelta(hours=8)
    timethreshold = datetime.datetime(year=2022, month=0o2, day=13, hour=11, minute=0, second=0, microsecond=0)
    correcttime = timenow >= timethreshold
    print(correcttime)
    print("now", timenow)
    print("threshold", timethreshold)
    if not correcttime:
      message = messages['early']
      form = 'hidden'
    else:
      if message == None:
        message = messages['default']
    template_values = {'wrong': wrong, 'message': message, 'form': form}
    template = JINJA_ENVIRONMENT.get_template('pages/vday22/index.html')
    return template.render(template_values)

@app.route('/vday', methods = ['POST', 'GET'])
def Vday(message=None, wrong=None, form=None):
  if request.method == 'POST':
    form = None
    with open('pages/vday/data.json') as json_data:
      messages = json.load(json_data)
    template_values = messages
    key = request.form['key'].lower().replace('il ', '').replace(',', '').replace('.', '').replace('#', '').replace('\'','').replace('chicken', '').replace('zoo', '').replace(' ', '')
    last = request.form['last']
    if key in list(messages.keys()):
      if key == 'jenny':
        form = 'hidden'
      request.method = 'GET'
      return Vday(message=messages[key], wrong=None, form=form)
    else:
      request.method = 'GET'
      return Vday(message=last, wrong='visible')

  if request.method == 'GET':
    with open('pages/vday/data.json') as json_data:
      messages = json.load(json_data)
    timenow = datetime.datetime.now()-datetime.timedelta(hours=8)
    timethreshold = datetime.datetime(year=2021, month=0o2, day=14, hour=11, minute=0, second=0, microsecond=0)
    correcttime = timenow >= timethreshold
    print(correcttime)
    print("now", timenow)
    print("threshold", timethreshold)
    if not correcttime:
      message = messages['early']
      form = 'hidden'
    else:
      if message == None:
        message = messages['default']
    template_values = {'wrong': wrong, 'message': message, 'form': form}
    template = JINJA_ENVIRONMENT.get_template('pages/vday/index.html')
    return template.render(template_values)

@app.errorhandler(500)
def server_error(e):
  return "An internal error.", 500

#if __name__ == "__main__":
#  app.run(debug=True)
