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

CITY = [
  {
    'id': 1,
    'title': 'Moers',
    'lat': 51.451117,
    'lon': 6.629194
  },
  {
    'id': 2,
    'title': 'Bochum',
    'lat': 51.451117,
    'lon': 6.629194
  },
  {
    'id': 3,
    'title': 'Aachen',
    'lat': 51.451117,
    'lon': 6.629194
  }
]

SOURCE = [
  {
    'title': 'ENNI',
    'website': 'https://www.enni.de/enni-gruppe/hier-bauen-wir.html',
    'city_id': 1
  },
  {
    'title': 'Bochum',
    'website': '',
    'city_id': 1
  },
  {
    'title': 'Aachen',
    'website': 'http://www.bsis.regioit.de/geoserver/BSISPROD/wms?service=wfs&version=2.0.0&request=GetFeature&typeNames=BSISPROD:Baustellen_7Tage_Punkte&outputFormat=json',
    'city_id': 1
  }
]