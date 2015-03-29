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

import datetime
import calendar
import email.utils
import re
import urllib
import urllib2
import json
import bson
import math
import requests
import utm
from models import *
from webapp import app, db
from lxml import etree, html
from lxml.cssselect import CSSSelector
import sources

def rfc1123date(value):
  """
  Gibt ein Datum (datetime) im HTTP Head-tauglichen Format (RFC 1123) zurück
  """
  tpl = value.timetuple()
  stamp = calendar.timegm(tpl)
  return email.utils.formatdate(timeval=stamp, localtime=False, usegmt=True)

def expires_date(hours):
  """Date commonly used for Expires response header"""
  dt = datetime.datetime.now() + datetime.timedelta(hours=hours)
  return rfc1123date(dt)

def cache_max_age(hours):
  """String commonly used for Cache-Control response headers"""
  seconds = hours * 60 * 60
  return 'max-age=' + str(seconds)

def sync():
  for source_id, source_name in app.config['SOURCES'].iteritems():
    source_class = getattr(sources, source_name)
    source_object = source_class()
    print "Syncing %s (ID %s)" % (source_name, source_id)
    source_object.sync()

def test():
  foo = sources.HamburgStadt()
  foo.sync()

def geocode(location_string):
  """
  Löst eine Straßen- oder Lat,Lon-Angabe zu einer Geo-Postion auf.
  """
  location_string = location_string.encode('utf-8')
  url = 'http://open.mapquestapi.com/nominatim/v1/search.php'
  params = {'format': 'json',  # json
            'q': location_string,
            'addressdetails': 1,
            'accept-language': 'de_DE'}#,
            #'countrycodes': app.config['GEOCODING_DEFAULT_COUNTRY']}
  request = urllib2.urlopen(url + '?' + urllib.urlencode(params))
  response = request.read()
  addresses = json.loads(response)
  addresses_out = []
  for address in addresses:
    for key in address.keys():
      if key in ['address', 'boundingbox', 'lat', 'lon', 'osm_id']:
        continue
      del address[key]
    # skip if not in correct county
    if 'county' not in address['address']:
      continue
    #if address['address']['county'] != app.config['GEOCODING_FILTER_COUNTY']:
    #  continue
    addresses_out.append(address)
  return addresses_out

def distance_earth(lat1, long1, lat2, long2):
  degrees_to_radians = math.pi/180.0
  
  phi1 = (90.0 - float(lat1))*degrees_to_radians
  phi2 = (90.0 - float(lat2))*degrees_to_radians
  
  theta1 = float(long1)*degrees_to_radians
  theta2 = float(long2)*degrees_to_radians
  
  cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
  arc = math.acos( cos )
  
  return arc * 6373 * 1000
  
def obscuremail(mailaddress):
  return mailaddress.replace('@', '__AT__').replace('.', '__DOT__')
app.jinja_env.filters['obscuremail'] = obscuremail

app.jinja_env.globals.update(dumps=json.dumps)

def deref_type(type_id):
  type_id = int(type_id)
  if type_id >= 0 and type_id <= 5:
    return app.config['MARKER_DEF'][type_id]
  else:
    return ''
app.jinja_env.filters['deref_type'] = deref_type

class MyEncoder(json.JSONEncoder):
  def default(self, obj):
    return str(obj)
