# encoding: utf-8

"""
Copyright (c) 2014 Ernesto Ruge

Hiermit wird unentgeltlich jeder Person, die eine Kopie der Software und
der zugehörigen Dokumentationen (die "Software") erhält, die Erlaubnis
erteilt, sie uneingeschränkt zu benutzen, inklusive und ohne Ausnahme, dem
Recht, sie zu verwenden, kopieren, ändern, fusionieren, verlegen,
verbreiten, unterlizenzieren und/oder zu verkaufen, und Personen, die diese
Software erhalten, diese Rechte zu geben, unter den folgenden Bedingungen:

Der obige Urheberrechtsvermerk und dieser Erlaubnisvermerk sind in allen
Kopien oder Teilkopien der Software beizulegen.

Die Software wird ohne jede ausdrückliche oder implizierte Garantie
bereitgestellt, einschließlich der Garantie zur Benutzung für den
vorgesehenen oder einen bestimmten Zweck sowie jeglicher Rechtsverletzung,
jedoch nicht darauf beschränkt. In keinem Fall sind die Autoren oder
Copyrightinhaber für jeglichen Schaden oder sonstige Ansprüche haftbar zu
machen, ob infolge der Erfüllung eines Vertrages, eines Delikts oder anders
im Zusammenhang mit der Software oder sonstiger Verwendung der Software
entstanden.
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

