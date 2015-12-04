# encoding: utf-8

"""
Copyright (c) 2012 - 2015, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from webapp import app, basic_auth, mail
from flask import render_template, make_response, abort, request, Response, redirect, flash, send_file
from flask.ext.mail import Message
from models import *
from forms import *
import models, util
import json, time, os, datetime
from subprocess import call
from sqlalchemy import or_
import socket
import sources


@app.route('/')
def index():
  return render_template('index.html')

@app.route("/region-list")
def region_list():
  start_time = time.time()
  ret = {
    'status': 0,
    'duration': round((time.time() - start_time) * 1000),
    'request': {},
    'response': app.config['REGIONS']
  }
  json_output = json.dumps(ret, cls=util.MyEncoder, sort_keys=True)
  response = make_response(json_output, 200)
  response.mimetype = 'application/json'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = -1
  response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
  return(response)

@app.route("/construction-list")
def construction_list():
  start_time = time.time()
  constructions = ConstructionSite.query.filter(ConstructionSite.end > datetime.datetime.now()).all()
  result = []
  for construction in constructions:
    result.append({
      'id': construction.id,
      'lat': construction.lat,
      'lng': construction.lon
    })
  ret = {
    'status': 0,
    'duration': round((time.time() - start_time) * 1000),
    'request': {},
    'response': result
  }
  json_output = json.dumps(ret, cls=util.MyEncoder, sort_keys=True)
  response = make_response(json_output, 200)
  response.mimetype = 'application/json'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = -1
  response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
  return(response)

@app.route("/construction-area-list")
def construction_area_list():
  start_time = time.time()
  n = request.args.get('n', 0)
  w = request.args.get('w', 0)
  e = request.args.get('e', 0)
  s = request.args.get('s', 0)
  constructions = ConstructionSite.query.filter(ConstructionSite.end > datetime.datetime.now()).filter(ConstructionSite.lat > s).filter(ConstructionSite.lat < n).filter(ConstructionSite.lon > w).filter(ConstructionSite.lon < e).all()
  result = []
  for construction in constructions:
    if construction.area:
      result.append({
        'id': construction.id,
        'area': json.loads(construction.area),
      })
  ret = {
    'status': 0,
    'duration': round((time.time() - start_time) * 1000),
    'request': {},
    'response': result
  }
  json_output = json.dumps(ret, cls=util.MyEncoder, sort_keys=False)
  response = make_response(json_output, 200)
  response.mimetype = 'application/json'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = -1
  response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
  return(response)

@app.route("/construction-details")
def construction_details():
  start_time = time.time()
  try:
    construction_id = int(request.args.get('id'))
  except ValueError:
    abort(500)
  construction = ConstructionSite.query.filter_by(id=construction_id).first_or_404()
  result = {
    'id': construction.id,
    'title': construction.title,
    'descr': construction.descr,
    'location_descr': construction.location_descr,
    'constructor': construction.constructor,
    'reason': construction.reason,
    'execution': construction.execution,
    'lat': construction.lat,
    'lon': construction.lon,
    'area': construction.area,
    'begin': construction.begin,
    'end': construction.end,
    'type': construction.type,
    'restriction': construction.restriction,
    'external_id': construction.external_id,
    'external_url': construction.external_url,
    'created_at': construction.created_at,
    'updated_at': construction.updated_at,
    'licence_name': construction.licence_name,
    'licence_url': construction.licence_url,
    'licence_owner': construction.licence_owner
  }
  ret = {
    'status': 0,
    'duration': round((time.time() - start_time) * 1000),
    'request': {},
    'response': result
  }
  json_output = json.dumps(ret, cls=util.MyEncoder, sort_keys=True)
  response = make_response(json_output, 200)
  response.mimetype = 'application/json'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = -1
  response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
  return(response)

@app.route("/information")
def information():
  data_sources = []
  for source_id, source_name in app.config['SOURCES'].iteritems():
    source_class = getattr(sources, source_name)
    source_object = source_class()
    data_sources.append({
      'id': source_object.id,
      'title': source_object.title,
      'url': source_object.url,
      'contact_mail': source_object.contact_mail,
      'licence_url': source_object.licence_url,
      'licence_name': source_object.licence_name
    })
  return render_template('information.html', sources=data_sources)

@app.route("/impressum")
def impressum():
  return render_template('impressum.html')

@app.route("/daten")
def api():
  return render_template('daten.html')

