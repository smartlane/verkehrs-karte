# encoding: utf-8
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://mysqluser:mysqlpassword@mysqlhost/mysqltable'
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'database')

#Debugging?
DEBUG = True

SECRET_KEY = 'secret-key'

#Auto Generated Config Values
SQLALCHEMY_ECHO = False

BASIC_AUTH_USERNAME = 'admin-username'
BASIC_AUTH_PASSWORD = 'admin-password'
BASIC_AUTH_REALM = 'Bitte geben Sie Nutzername und Passwort fuer das Admin-Interface ein.'


REGIONS = {
  0: {
    'name': u'Deutschland',
    'lat': '51.163375',
    'lon': '10.447683',
    'zoom': 6
  },
  1: {
    'name': u'Baden-Württemberg',
    'lat': '48.695833',
    'lon': '9.0025',
    'zoom': 7
  },
  2: {
    'name': 'Bayern',
    'lat': '48.946389',
    'lon': '11.404167',
    'zoom': 7
  },
  3: {
    'name': 'Berlin',
    'lat': '52.502778',
    'lon': '13.404167',
    'zoom': 10
  },
  4: {
    'name': 'Brandenburg',
    'lat': '52.4592577',
    'lon': '13.0165528',
    'zoom': 8
  },
  5: {
    'name': 'Bremen',
    'lat': '53.3425297',
    'lon': '8.5905613',
    'zoom': 10
  },
  6: {
    'name': 'Hamburg ',
    'lat': '53.568889',
    'lon': '10.028889',
    'zoom': 10
  },
  7: {
    'name': 'Hessen',
    'lat': '50.608047',
    'lon': '9.0284650',
    'zoom': 8
  },
  8: {
    'name': 'Mecklenburg-Vorpommern',
    'lat': '53.773439',
    'lon': '12.575558',
    'zoom': 8
  },
  9: {
    'name': 'Niedersachsen',
    'lat': '52.839831',
    'lon': '9.075918',
    'zoom': 8
  },
  10: {
    'name': 'Nordrhein-Westfalen',
    'lat': '51.476631',
    'lon': '7.555005',
    'zoom': 8
  },
  11: {
    'name': 'Rheinland-Pfalz',
    'lat': '49.955139',
    'lon': '7.310417',
    'zoom': 8
  },
  12: {
    'name': 'Saarland',
    'lat': '49.37715',
    'lon': '6.878378',
    'zoom': 10
  },
  13: {
    'name': 'Sachsen',
    'lat': '51.0529280',
    'lon': '13.345149',
    'zoom': 8
  },
  14: {
    'name': 'Sachsen-Anhalt',
    'lat': '51.924506',
    'lon': '11.83587',
    'zoom': 8
  },
  15: {
    'name': 'Schleswig-Holstein',
    'lat': '54.184640',
    'lon': '9.82169',
    'zoom': 8
  },
  16: {
    'name': u'Thüringen',
    'lat': '50.907439',
    'lon': '11.037875',
    'zoom': 8
  },
  17: {
    'name': u'Schweiz',
    'lat': '46.7976552',
    'lon': '8.236315',
    'zoom': 8
  },
  18: {
    'name': u'Österreich',
    'lat': '47.61',
    'lon': '13.782778',
    'zoom': 8
  },
  19: {
    'name': 'Moers',
    'lat': '51.4573083',
    'lon': '6.6185085',
    'zoom': 11,
    'parent': 10
  },
  20: {
    'name': 'Rostock',
    'lat': '54.147551',
    'lon': '12.1469532',
    'zoom': 11,
    'parent': 8
  },
  21: {
    'name': 'Aachen',
    'lat': '50.75968',
    'lon': '6.0965247',
    'zoom': 11,
    'parent': 10
  },
  22: {
    'name': u'Bonn',
    'lat': '50.703577',
    'lon': '7.1157122',
    'zoom': 11,
    'parent': 10
  },
  23: {
    'name': u'Zürich',
    'lat': '47.377455',
    'lon': '8.536715',
    'zoom': 11,
    'parent': 17
  }
}

SOURCES = {
  1: 'AachenStadt',
  2: 'RostockStadt',
  3: 'KoelnStadt',
  4: 'BonnStadt',
  5: 'ZuerichStadt',
  6: 'HamburgStadt'
}
