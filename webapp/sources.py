# encoding: utf-8
from models import *
from webapp import app, db
import subprocess
import dateutil.parser
import requests
import json
import datetime

# apt-get install geographiclib-tools proj-bin
# download http://geographiclib.sourceforge.net/1.28/geoid.html

class FeatureCollection():
  contact_company = 'Baustelleninformationssystem des Bundes und der Länder'

class DefaultSource():
  # transforms from gauss kruger to wgs84 decimal
  def gk2latlon(self, x, y, gk_zone):
    if gk_zone > 1 and gk_zone < 6:
      gk_id = gk_zone * 3
    else:
      return False
    # transform gk -> wgs84 degree
    cmd = "echo %s %s | cs2cs +proj=tmerc +lat_0=0 +lon_0=%s  +k=1.000000 +x_0=2500000 +y_0=0 +ellps=bessel +units=m +no_defs +nadgrids=/srv/www/de.mobil-bei-uns/webapp/static/BETA2007.gsb +to +init=epsg:4326" % (x, y, gk_id)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = result.communicate()[0]
    
    # replace ' and "
    result = result.replace("'", "\\'")
    result = result.replace("\"", "\\\"")
    result = result.split()
    x = result[0]
    y = result[1]
    
    # transform wgs84 degree -> wgs84 decimal
    cmd = "echo %s %s | GeoConvert -p 3" % (x, y)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = result.communicate()[0]
    
    result = result.split()
    return {'lat': result[0], 'lon': result[1]}
  
  def epsg258322wsg84(self, x, y):
    # transform epsg258322 -> wgs84 degree
    cmd = "echo %s %s | cs2cs +init=epsg:25832 +to +init=epsg:4326" % (x, y)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = result.communicate()[0]
    
    # replace ' and "
    result = result.replace("'", "\\'")
    result = result.replace("\"", "\\\"")
    result = result.split()
    x = result[0]
    y = result[1]
    
    # transform wgs84 degree -> wgs84 decimal
    cmd = "echo %s %s | GeoConvert -p 3" % (x, y)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = result.communicate()[0]
    
    result = result.split()
    return {'lat': result[0], 'lon': result[1]}
  
  
  def save_mapping(self, source_data, current_construction, mapping):
    for mapping_from, mapping_to in mapping.iteritems():
      if mapping_from in source_data:
        if source_data[mapping_from]:
          setattr(current_construction, mapping_to, source_data[mapping_from])
    return current_construction
  
##############
### Aachen ###
##############

class AachenStadt(DefaultSource):
  id = 1
  title = ''
  url = 'http://offenedaten.aachen.de/dataset/baustellen-stadtgebiet-aachen'
  source_url = 'http://www.bsis.regioit.de/geoserver/BSISPROD/wms?service=wfs&version=2.0.0&request=GetFeature&typeNames=BSISPROD:Baustellen_7Tage_Punkte&outputFormat=json'
  contact_company = 'Geoservice der Stadt Aachen'
  contact_name = ''
  contact_mail = 'offenedaten@mail.aachen.de'
  licence_name = 'Datenlizenz Deutschland – Namensnennung – Version 2.0'
  licence_url = 'https://www.govdata.de/dl-de/by-2-0'
  mapping = {
    'NAME': 'title',
    'EINSCHRAEN': 'restriction',
    'HOTLINK': 'external_url',
    'FIRMA': 'execution',
    'BAUHERR': 'constructor',
    'SYMBOL': 'descr'
  }
  
  def sync(self):
    request_data = requests.get(self.source_url)
    data = json.loads(request_data.content)
    for construction in data['features']:
      current_external_id = construction['properties']['GID']
      current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
      # no database entry
      if not current_construction:
        current_construction = ConstructionSite()
        current_construction.external_id = current_external_id
        current_construction.created_at = datetime.datetime.now()
        current_construction.source_id = self.id
      # refresh values
      current_constuction = self.save_mapping(construction['properties'], current_construction, self.mapping)
      current_constuction.location_descr = "%s %s" % (construction['properties']['STRASSEN'], construction['properties']['STRASSEN'])
      period = construction['properties']['ZEITRAUM'].split(' - ')
      current_constuction.begin = datetime.datetime(int(period[0][6:10]), int(period[0][3:5]), int(period[0][0:2]), 0, 0, 0)
      current_constuction.end = datetime.datetime(int(period[1][6:10]), int(period[1][3:5]), int(period[1][0:2]), 23, 59, 59)
      current_construction.updated_at = datetime.datetime.now()
      position = self.gk2latlon(construction['geometry']['coordinates'][1], construction['geometry']['coordinates'][0], 2)
      current_construction.lat = position['lat']
      current_construction.lon = position['lon']
      current_construction.licence_name = self.licence_name
      current_construction.licence_url = self.licence_url
      current_construction.licence_owner = self.contact_company
      # save data
      db.session.add(current_construction)
      db.session.commit()

###############
### Rostock ###
###############

class RostockStadt(DefaultSource):
  id = 2
  title = 'Stadt Rostock'
  url = 'https://geo.sv.rostock.de/'
  source_url = 'https://geo.sv.rostock.de/download/opendata/baustellen/baustellen.json'
  contact_company = 'Rostock'
  contact_name = 'Geodienste der Stadt Rostock'
  contact_mail = 'geodienste@rostock.de'
  licence_name = 'unbekannt'
  licence_url = ''
  active = True
  mapping = {
    'art': 'title',
    'sperrung_art': 'restriction',
    'url': 'external_url',
    'sperrung_grund': 'descr',
    'sperrung_grund': 'reason',
    'durchfuehrung': 'execution'
  }

  def sync(self):
    request_data = requests.get(self.source_url)
    data = json.loads(request_data.content)
    for construction in data['features']:
      current_external_id = construction['properties']['uuid']
      current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
      # no database entry
      if not current_construction:
        current_construction = ConstructionSite()
        current_construction.external_id = current_external_id
        current_construction.created_at = datetime.datetime.now()
        current_construction.source_id = self.id
      # refresh values
      current_constuction = self.save_mapping(construction['properties'], current_construction, self.mapping)
      current_constuction.type = current_constuction.title
      if construction['properties']['strasse_name'] and construction['properties']['lage_von'] and construction['properties']['lage_bis']:
        current_constuction.location_descr = "%s von %s bis %s" % (construction['properties']['strasse_name'], construction['properties']['lage_von'], construction['properties']['lage_bis'])
      elif construction['properties']['strasse_name']:
        current_constuction.location_descr = construction['properties']['strasse_name']
      current_construction.begin = dateutil.parser.parse(construction['properties']['sperrung_anfang']).replace(tzinfo=None)
      current_construction.end = dateutil.parser.parse(construction['properties']['sperrung_ende']).replace(tzinfo=None)
      current_construction.licence_name = self.licence_name
      #current_construction.licence_url = self.licence_url
      current_construction.licence_owner = self.contact_company
      current_construction.lat = construction['geometry']['coordinates'][1]
      current_construction.lon = construction['geometry']['coordinates'][0]
      current_construction.updated_at = datetime.datetime.now()
      # save data
      db.session.add(current_construction)
      db.session.commit()

############
### Köln ###
############

class KoelnStadt(DefaultSource):
  id = 3
  title = u'Stadt Köln'
  url = 'http://offenedaten-koeln.de/dataset/baustellen-k%C3%B6ln'
  source_url = 'http://geoportal1.stadt-koeln.de/ArcGIS/rest/services/WebVerkehr_DataOSM/MapServer/0/query?text=&geometry=&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds=&where=objectid%20is%20not%20null&time=&returnCountOnly=false&returnIdsOnly=false&returnGeometry=true&maxAllowableOffset=&outSR=4326&outFields=%2A&f=json'
  source_metadata_url = 'http://geoportal1.stadt-koeln.de/ArcGIS/rest/services/WebVerkehr_DataOSM/MapServer/0?f=json&pretty=true'
  contact_company = 'Stadt Köln'
  contact_name = u'Stadt Köln'
  contact_mail = 'e-government@stadt-koeln.de'
  licence_name = 'Creative Commons Namensnennung 3.0'
  licence_url = 'http://creativecommons.org/licenses/by/3.0/de/'
  active = True
  mapping = {
    'NAME': 'title',
    'BESCHREIBUNG': 'descr'
  }

  def sync(self):
    # first: get metadata
    meta_types = {}
    request_data = requests.get(self.source_metadata_url)
    data = json.loads(request_data.content)
    for field in data['fields']:
      if field['name'] == 'TYP':
        for meta_type in field['domain']['codedValues']:
          meta_types[meta_type['code']] = meta_type['name']
    
    # second: get construction sites
    request_data = requests.get(self.source_url)
    data = json.loads(request_data.content)
    for construction in data['features']:
      current_external_id = construction['attributes']['OBJECTID']
      current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
      # no database entry
      if not current_construction:
        current_construction = ConstructionSite()
        current_construction.external_id = current_external_id
        current_construction.created_at = datetime.datetime.now()
        current_construction.source_id = self.id
      # refresh values
      current_constuction = self.save_mapping(construction['attributes'], current_construction, self.mapping)
      if construction['attributes']['DATUM_VON']:
        current_construction.begin = datetime.datetime.fromtimestamp(construction['attributes']['DATUM_VON'] / 1000)
      if construction['attributes']['DATUM_BIS']:
        current_construction.end = datetime.datetime.fromtimestamp(construction['attributes']['DATUM_BIS'] / 1000)
      current_construction.external_url = 'http://www.stadt-koeln.de%s' % (construction['attributes']['LINK'])
      current_construction.type = meta_types[construction['attributes']['TYP']]
      current_construction.licence_name = self.licence_name
      current_construction.licence_url = self.licence_url
      current_construction.licence_owner = self.contact_company
      current_construction.lat = construction['geometry']['y']
      current_construction.lon = construction['geometry']['x']
      current_construction.updated_at = datetime.datetime.now()
      # save data
      db.session.add(current_construction)
      db.session.commit()
      
############
### Bonn ###
############

class BonnStadt(DefaultSource):
  id = 3
  title = u'Stadt Bonn'
  url = 'http://offenedaten-koeln.de/dataset/baustellen-k%C3%B6ln'
  source_url = 'http://stadtplan.bonn.de/geojson?Thema=14403&koordsys=25832'
  contact_company = 'Stadt Bonn'
  contact_name = u'Stadt Bonn'
  contact_mail = 'opendata@bonn.de'
  licence_name = 'Datenlizenz Deutschland Namensnennung'
  licence_url = 'https://www.govdata.de/dl-de/by-2-0'
  active = True
  mapping = {
    'bezeichnung': 'title',
    'traeger': 'constructor',
    'massnahme': 'reason',
    'sperrung': 'descr'
  }

  def sync(self):
    request_data = requests.get(self.source_url)
    data = json.loads(unicode(request_data.content, "ISO-8859-1"))
    for construction in data['features']:
      current_external_id = construction['properties']['baustelle_id']
      current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
      # no database entry
      if not current_construction:
        current_construction = ConstructionSite()
        current_construction.external_id = current_external_id
        current_construction.created_at = datetime.datetime.now()
        current_construction.source_id = self.id
      # refresh values
      current_constuction = self.save_mapping(construction['properties'], current_construction, self.mapping)
      current_constuction.begin = datetime.datetime(int(construction['properties']['von'][6:10]), int(construction['properties']['von'][3:5]), int(construction['properties']['von'][0:2]), 0, 0, 0)
      current_constuction.end = datetime.datetime(int(construction['properties']['bis'][6:10]), int(construction['properties']['bis'][3:5]), int(construction['properties']['bis'][0:2]), 23, 59, 59)
      current_construction.location_descr = "%s, %s" % (construction['properties']['adresse'], construction['properties']['stadtbezirk_bez'])
      current_construction.licence_name = self.licence_name
      current_construction.licence_url = self.licence_url
      current_construction.licence_owner = self.contact_company
      position = self.epsg258322wsg84(construction['geometry']['coordinates'][0], construction['geometry']['coordinates'][1])
      current_construction.lat = position['lat']
      current_construction.lon = position['lon']
      current_construction.updated_at = datetime.datetime.now()
      # save data
      db.session.add(current_construction)
      db.session.commit()
      
##############
### Zürich ###
##############

class ZuerichStadt(DefaultSource):
  id = 3
  title = u'Stadt Bonn'
  url = 'https://www.stadt-zuerich.ch/portal/de/index/ogd/daten/tiefbaustelle.html'
  source_url = 'http://data.stadt-zuerich.ch/ogd.4vhCDPd.link'
  contact_company = u'Stadt Zürich'
  contact_name = u'Stadt Zürich'
  contact_mail = 'opendata@zuerich.ch'
  licence_name = 'unbekannt'
  licence_url = ''
  active = True
  mapping = {
    'Name': 'title',
    'Projektbeschrieb': 'descr',
    'Baubereich': 'location_descr'
  }
  
  def sync(self):
    request_data = requests.get(self.source_url)
    data = json.loads(request_data.content)
    for construction in data['features']:
      current_external_id = construction['properties']['Baunummer']
      current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
      # no database entry
      if not current_construction:
        current_construction = ConstructionSite()
        current_construction.external_id = current_external_id
        current_construction.created_at = datetime.datetime.now()
        current_construction.source_id = self.id
      # refresh values
      current_constuction = self.save_mapping(construction['properties'], current_construction, self.mapping)
      current_constuction.begin = datetime.datetime(int(construction['properties']['Baubeginn'][0:4]), int(construction['properties']['Baubeginn'][4:6]), int(construction['properties']['Baubeginn'][6:8]), 0, 0, 0)
      current_constuction.end = datetime.datetime(int(construction['properties']['Bauende'][0:4]), int(construction['properties']['Bauende'][4:6]), int(construction['properties']['Bauende'][6:8]), 23, 59, 59)
      current_construction.licence_name = self.licence_name
      #current_construction.licence_url = self.licence_url
      current_construction.licence_owner = self.contact_company
      if construction['geometry']['type'] == 'MultiPolygon':
        current_construction.lat = construction['geometry']['coordinates'][0][0][0][1]
        current_construction.lon = construction['geometry']['coordinates'][0][0][0][0]
      elif construction['geometry']['type'] == 'Polygon':
        current_construction.lat = construction['geometry']['coordinates'][0][0][1]
        current_construction.lon = construction['geometry']['coordinates'][0][0][0]
      else:
        print "New geometry type found"
      current_construction.area = json.dumps(construction['geometry'])
      current_construction.updated_at = datetime.datetime.now()
      # save data
      db.session.add(current_construction)
      db.session.commit()
  
###############
### Hamburg ###
###############

class HamburgStadt(DefaultSource):
  id = 3
  title = u'Stadt Bonn'
  url = 'http://suche.transparenz.hamburg.de/dataset/baustellen-hamburg'
  source_url = ''
  contact_company = u'SFreie und Hansestadt Hamburg, Behörde für Wirtschaft Verkehr und Innovation'
  contact_name = u'Stadt Hamburg'
  contact_mail = 'opendata@zuerich.ch'
  licence_name = 'Datenlizenz Deutschland Namensnennung 2.0'
  licence_url = 'https://www.govdata.de/dl-de/by-2-0'
  active = True
  mapping = {}
  
  