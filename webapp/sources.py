# encoding: utf-8
from models import *
from webapp import app, db
import subprocess
import dateutil.parser
import requests
import json
import datetime
import re
from xml.etree import ElementTree
import csv
import util
from copy import deepcopy

# apt-get install geographiclib-tools proj-bin
# download http://geographiclib.sourceforge.net/1.28/geoid.html

class DefaultSource():
  # transforms from gauss kruger to wgs84 decimal
  def gk2latlon(self, x, y, gk_zone):
    if gk_zone > 1 and gk_zone < 6:
      gk_id = gk_zone * 3
    else:
      return False
    # transform gk -> wgs84 degree
    cmd = "echo %s %s | cs2cs +proj=tmerc +lat_0=0 +lon_0=%s  +k=1.000000 +x_0=2500000 +y_0=0 +ellps=bessel +units=m +no_defs +nadgrids=%s/misc/BETA2007.gsb +to +init=epsg:4326" % (x, y, gk_id, app.config['BASE_DIR'])
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
  
  def epsg258322latlon(self, x, y):
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
  
  def deref_lcl(self, lcl_id):
    with open('%s/misc/%s' % (app.config['BASE_DIR'], app.config['LCL_FILE']), 'rb') as csvfile:
      lcl_file = csv.reader(csvfile, delimiter=';', quotechar="\"")
      first = True
      for lcl_dataset in lcl_file:
        if first:
          first = False
        else:
          if lcl_dataset[0]:
            if int(lcl_dataset[0]) == int(lcl_id):
              if lcl_dataset[28] and lcl_dataset[29]:
                result = {
                  'lat': float(lcl_dataset[29].replace('+', '')) / 100000,
                  'lon': float(lcl_dataset[28].replace('+', '')) / 100000
                }
                return result
    return False
  
  def save_mapping(self, source_data, current_construction, mapping):
    for mapping_from, mapping_to in mapping.iteritems():
      if mapping_from in source_data:
        if source_data[mapping_from]:
          setattr(current_construction, mapping_to, source_data[mapping_from])
    return current_construction
  
  # openssl pkcs12 -in dev.ernestoruge.de.p12 -out package.pem -node
  def sync_mdm(self):
    cmd = "wget -q --certificate misc/%s.crt --private-key misc/%s.key --ca-certificate misc/%s.chain.ca %s -O - | gunzip" % (app.config['MDM_CERT_FILE'], app.config['MDM_CERT_FILE'], app.config['MDM_CERT_FILE'], self.source_url)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = result.communicate()[0]
    data = ElementTree.fromstring(result)
    xml_prefix = '{http://datex2.eu/schema/2/2_0}'
    attrib_prefix = '{http://www.w3.org/2001/XMLSchema-instance}'
    for item in data:
      if item.tag == '%spayloadPublication' % xml_prefix:
        data = item
    for dataset in data:
      if dataset.tag == '%ssituation' % xml_prefix:
        dataset_result = []
        for subdataset in dataset:
          subdataset_result = {}
          if subdataset.tag == '%ssituationRecord' % xml_prefix:
            subdataset_result['descr'] = []
            subdataset_result['external_id'] = subdataset.attrib['id']
            for item in subdataset:
              if item.tag == '%svalidity' % xml_prefix:
                for sub1item in item:
                  if sub1item.tag == '%svalidityTimeSpecification' % xml_prefix:
                    for sub2item in sub1item:
                      if sub2item.tag == '%soverallStartTime' % xml_prefix:
                        subdataset_result['begin'] = dateutil.parser.parse(sub2item.text).replace(tzinfo=None)
                      elif sub2item.tag == '%soverallEndTime' % xml_prefix:
                        subdataset_result['end'] = dateutil.parser.parse(sub2item.text).replace(tzinfo=None)
              elif item.tag == '%sgeneralPublicComment' % xml_prefix:
                for sub1item in item:
                  if sub1item.tag == '%scomment' % xml_prefix:
                    for sub2item in sub1item:
                      if sub2item.tag == '%svalues' % xml_prefix:
                        for sub3item in sub2item:
                          if sub3item.tag == '%svalue' % xml_prefix:
                            subdataset_result['reason'] = sub3item.text
              elif item.tag == '%sgroupOfLocations' % xml_prefix:
                if item.attrib['%stype' % attrib_prefix] == 'Point':
                  for sub1item in item:
                    if sub1item.tag == '%salertCPoint' % xml_prefix:
                      for sub2item in sub1item:
                        if sub2item.tag == '%salertCMethod2PrimaryPointLocation' % xml_prefix:
                          for sub3item in sub2item:
                            if sub3item.tag == '%salertCLocation' % xml_prefix:
                              for sub4item in sub3item:
                                if sub4item.tag == '%salertCLocationName' % xml_prefix:
                                  for sub5item in sub4item:
                                    if sub5item.tag == '%svalues' % xml_prefix:
                                      for sub6item in sub5item:
                                        if sub6item.tag == '%svalue' % xml_prefix:
                                          subdataset_result['location_descr'] = sub6item.text
                                elif sub4item.tag == '%sspecificLocation' % xml_prefix:
                                  if sub4item.text:
                                    result = self.deref_lcl(sub4item.text)
                                    if result:
                                      subdataset_result.update(result)
                                    else:
                                      print "Warning: ID %s unknown" % sub4item.text
                                  else:
                                    print 'Warning: No location given!'
                elif item.attrib['%stype' % attrib_prefix] == 'Linear':
                  subdataset_result['area'] = {}
                  subdataset_result['location_descr'] = {}
                  for sub1item in item:
                    if sub1item.tag == '%ssupplementaryPositionalDescription' % xml_prefix:
                      for sub2item in sub1item:
                        if sub2item.tag == '%saffectedCarriagewayAndLanes' % xml_prefix:
                          for sub3item in sub2item:
                            if sub3item.tag == '%slengthAffected' % xml_prefix:
                              subdataset_result['location_descr']['length'] = int(round(float(sub3item.text)))
                    elif sub1item.tag == '%salertCLinear' % xml_prefix:
                      for sub2item in sub1item:
                        if sub2item.tag == '%salertCMethod2PrimaryPointLocation' % xml_prefix:
                          for sub3item in sub2item:
                            if sub3item.tag == '%salertCLocation' % xml_prefix:
                              for sub4item in sub3item:
                                if sub4item.tag == '%salertCLocationName' % xml_prefix:
                                  for sub5item in sub4item:
                                    if sub5item.tag == '%svalues' % xml_prefix:
                                      for sub6item in sub5item:
                                        if sub6item.tag == '%svalue' % xml_prefix:
                                          subdataset_result['location_descr']['von'] = sub6item.text
                                elif sub4item.tag == '%sspecificLocation' % xml_prefix:
                                  if sub4item.text:
                                    result = self.deref_lcl(sub4item.text)
                                    if result:
                                      subdataset_result.update(result)
                                      subdataset_result['area']['start'] = result
                                    else:
                                      print "Warning: ID %s unknown" % sub4item.text
                                  else:
                                    print 'Warning: No location given!'
                        elif sub2item.tag == '%salertCMethod2SecondaryPointLocation' % xml_prefix:
                          for sub3item in sub2item:
                            if sub3item.tag == '%salertCLocation' % xml_prefix:
                              for sub4item in sub3item:
                                if sub4item.tag == '%salertCLocationName' % xml_prefix:
                                  for sub5item in sub4item:
                                    if sub5item.tag == '%svalues' % xml_prefix:
                                      for sub6item in sub5item:
                                        if sub6item.tag == '%svalue' % xml_prefix:
                                          subdataset_result['location_descr']['bis'] = sub6item.text
                                elif sub4item.tag == '%sspecificLocation' % xml_prefix:
                                  if sub4item.text:
                                    result = self.deref_lcl(sub4item.text)
                                    if result:
                                      subdataset_result['area']['end'] = result
                                    else:
                                      print "Warning: ID %s unknown" % sub4item.text
                                  else:
                                    print 'Warning: No location given!'
                    elif sub1item.tag == '%slinearWithinLinearElement' % xml_prefix:
                      for sub2item in sub1item:
                        if sub2item.tag == '%slinearElement' % xml_prefix:
                          for sub3item in sub2item:
                            if sub3item.tag == '%sroadNumber' % xml_prefix:
                              subdataset_result['street'] = sub3item.text
                  if 'von' in subdataset_result['location_descr'] and 'bis' in subdataset_result['location_descr']:
                    location_string = ''
                    if 'street' in subdataset_result:
                      location_string = '%s ' % subdataset_result['street']
                    location_string += 'von %s bis %s' % (subdataset_result['location_descr']['von'], subdataset_result['location_descr']['bis'])
                    if 'length' in subdataset_result['location_descr']:
                      location_string += u' (Länge: %s m)' % subdataset_result['location_descr']['length']
                    subdataset_result['location_descr'] = location_string
                  else:
                    del subdataset_result['location_descr']
                  if 'start' in subdataset_result['area'] and 'end' in subdataset_result['area']:
                    # We need the route from A to B to get the real construction site position
                    if subdataset_result['area']['start']['lat'] > subdataset_result['area']['end']['lat']:
                      route_n = subdataset_result['area']['start']['lat']
                      route_s = subdataset_result['area']['end']['lat']
                    else:
                      route_n = subdataset_result['area']['end']['lat']
                      route_s = subdataset_result['area']['start']['lat']
                    if subdataset_result['area']['start']['lon'] > subdataset_result['area']['end']['lon']:
                      route_e = subdataset_result['area']['start']['lon']
                      route_w = subdataset_result['area']['end']['lon']
                    else:
                      route_e = subdataset_result['area']['end']['lon']
                      route_w = subdataset_result['area']['start']['lon']
                    route_s -= 0.05
                    route_n += 0.05
                    route_e += 0.05
                    route_w -= 0.05
                    overpass_url = "http://www.overpass-api.de/api/interpreter?data=node(%s,%s,%s,%s);way(bn);way._[\"highway\"=\"motorway\"];(._;>;);out;" % (route_s, route_w, route_n, route_e)
                    overpass_result = requests.get(overpass_url)
                    overpass_data = ElementTree.fromstring(overpass_result.content)
                    node_list = {}
                    way_piece_list = {}
                    for item in overpass_data:
                      if item.tag == 'node':
                        node_list[item.attrib['id']] = [float(item.attrib['lat']), float(item.attrib['lon'])]
                      else:
                        steet_name = ''
                        if item.tag == 'way':
                          current_way = []
                          for subitem in item:
                            if subitem.tag == 'nd':
                              current_way.append(subitem.attrib['ref'])
                            elif subitem.tag == 'tag':
                              if subitem.attrib['k'] == 'ref':
                                steet_name = subitem.attrib['v']
                        # just add when it's the right street name
                        if steet_name.replace(' ', '') == subdataset_result['street']:
                          way_piece_list[item.attrib['id']] = current_way
                    # Chain ways
                    way_list = []
                    if len(way_piece_list):
                      while len(way_piece_list):
                        key = way_piece_list.keys()[0]
                        current_way = way_piece_list[key]
                        del way_piece_list[key]
                        found = True
                        while found:
                          found = False
                          new_way_piece_list = deepcopy(way_piece_list)
                          for key, way_piece in way_piece_list.iteritems():
                            if way_piece[0] == current_way[-1]:
                              current_way = current_way + way_piece[1:]
                              del new_way_piece_list[key]
                              found = True
                            elif way_piece[-1] == current_way[0]:
                              current_way = way_piece[:-1] + current_way
                              del new_way_piece_list[key]
                              found = True
                          way_piece_list = deepcopy(new_way_piece_list)
                        way_list.append(current_way)
                      # Dereference nodes
                      for way_id, way in enumerate(way_list):
                        for position_id, position in enumerate(way):
                          way_list[way_id][position_id] = node_list[position]
                      # Get lowest distance
                      min_distance = 1000000
                      min_position = -1
                      for index, way in enumerate(way_list):
                        tmp_distance = util.distance_earth(subdataset_result['lat'], subdataset_result['lon'], way[0][0], way[0][1])
                        if tmp_distance < min_distance:
                          min_position = index
                          min_distance = tmp_distance
                      # Find start point
                      way_result = way_list[min_position]
                      min_distance = 1000000
                      min_position = -1
                      for index, way_result_point in enumerate(way_result):
                        current_distance = util.distance_earth(subdataset_result['area']['start']['lat'], subdataset_result['area']['start']['lon'], way_result_point[0], way_result_point[1])
                        if current_distance < min_distance:
                          min_distance = current_distance
                          min_position = index
                      way_result = way_result[min_position:]
                      # Find end point
                      min_distance = 1000000
                      min_position = -1
                      for index, way_result_point in enumerate(way_result):
                        current_distance = util.distance_earth(subdataset_result['area']['end']['lat'], subdataset_result['area']['end']['lon'], way_result_point[0], way_result_point[1])
                        if current_distance < min_distance:
                          min_distance = current_distance
                          min_position = index
                      way_result = way_result[:min_position]
                      subdataset_result['area'] = json.dumps({'coordinates': way_result, 'type': 'LineString'})
                    else:
                      print "Warning: bad result at geosearch with %s " % overpass_url
                      print "Debug Info"
                      print overpass_result.content
                      del subdataset_result['area']
                  else:
                    del subdataset_result['area']
                else:
                  print "New GeoType detected"
              elif item.tag == '%soperatorActionExtension' % xml_prefix:
                for sub1item in item:
                  if sub1item.tag == '%soperatorActionExtended' % xml_prefix:
                    for sub2item in sub1item:
                      if sub2item.tag == '%stemporarySpeedLimit' % xml_prefix:
                        subdataset_result['descr'].append('Geschwindigkeitsbegrenzung: %s km/h' % int(round(float(sub2item.text))))
            if subdataset_result['descr']:
              subdataset_result['descr'] = ', '.join(subdataset_result['descr'])
            else:
              del subdataset_result['descr']
            if 'external_id' in subdataset_result and 'lat' in subdataset_result and 'lon' in subdataset_result:
              current_external_id = subdataset_result['external_id']
              current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
              # no database entry
              if not current_construction:
                current_construction = ConstructionSite()
                current_construction.external_id = current_external_id
                current_construction.created_at = datetime.datetime.now()
                current_construction.source_id = self.id
              if 'area' in subdataset_result:
                current_construction.area = subdataset_result['area']
              if 'lat' in subdataset_result:
                current_construction.lat = subdataset_result['lat']
              if 'lon' in subdataset_result:
                current_construction.lon = subdataset_result['lon']
              if 'descr' in subdataset_result:
                current_construction.descr = subdataset_result['descr']
              if 'location_descr' in subdataset_result:
                current_construction.location_descr = subdataset_result['location_descr']
              if 'reason' in subdataset_result:
                current_construction.reason = subdataset_result['reason']
              if 'begin' in subdataset_result:
                current_construction.begin = subdataset_result['begin']
              if 'end' in subdataset_result:
                current_construction.end = subdataset_result['end']
              current_construction.licence_name = self.licence_name
              current_construction.licence_url = self.licence_url
              current_construction.licence_owner = self.contact_company
              current_construction.updated_at = datetime.datetime.now()
              # save data
              db.session.add(current_construction)
              db.session.commit()
  
  
  
##############
### Aachen ###
##############

class AachenStadt(DefaultSource):
  id = 1
  title = 'Stadt Aachen'
  url = u'http://offenedaten.aachen.de/dataset/baustellen-stadtgebiet-aachen'
  source_url = u'http://www.bsis.regioit.de/geoserver/BSISPROD/wms?service=wfs&version=2.0.0&request=GetFeature&typeNames=BSISPROD:Baustellen_7Tage_Punkte&outputFormat=json'
  contact_company = u'Geoservice der Stadt Aachen'
  contact_name = u''
  contact_mail = u'offenedaten@mail.aachen.de'
  licence_name = u'Datenlizenz Deutschland – Namensnennung – Version 2.0'
  licence_url = u'https://www.govdata.de/dl-de/by-2-0'
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
  title = u'Stadt Rostock'
  url = u'https://geo.sv.rostock.de/'
  source_url = u'https://geo.sv.rostock.de/download/opendata/baustellen/baustellen.json'
  contact_company = u'Rostock'
  contact_name = u'Geodienste der Stadt Rostock'
  contact_mail = u'geodienste@rostock.de'
  licence_name = u'unbekannt'
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
    request_data = requests.get(self.source_url, verify=True)
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
  url = u'http://offenedaten-koeln.de/dataset/baustellen-k%C3%B6ln'
  source_url = u'http://geoportal1.stadt-koeln.de/ArcGIS/rest/services/WebVerkehr_DataOSM/MapServer/0/query?text=&geometry=&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds=&where=objectid%20is%20not%20null&time=&returnCountOnly=false&returnIdsOnly=false&returnGeometry=true&maxAllowableOffset=&outSR=4326&outFields=%2A&f=json'
  source_metadata_url = u'http://geoportal1.stadt-koeln.de/ArcGIS/rest/services/WebVerkehr_DataOSM/MapServer/0?f=json&pretty=true'
  contact_company = u'Stadt Köln'
  contact_name = u'Stadt Köln'
  contact_mail = u'e-government@stadt-koeln.de'
  licence_name = u'Creative Commons Namensnennung 3.0'
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
  id = 4
  title = u'Stadt Bonn'
  url = u'http://offenedaten-koeln.de/dataset/baustellen-k%C3%B6ln'
  source_url = u'http://stadtplan.bonn.de/geojson?Thema=14403&koordsys=25832'
  contact_company = u'Stadt Bonn'
  contact_name = u'Stadt Bonn'
  contact_mail = u'opendata@bonn.de'
  licence_name = u'Datenlizenz Deutschland Namensnennung'
  licence_url = u'https://www.govdata.de/dl-de/by-1-0'
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
      position = self.epsg258322latlon(construction['geometry']['coordinates'][0], construction['geometry']['coordinates'][1])
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
  id = 5
  title = u'Stadt Bonn'
  url = 'https://www.stadt-zuerich.ch/portal/de/index/ogd/daten/tiefbaustelle.html'
  source_url = 'http://data.stadt-zuerich.ch/ogd.4vhCDPd.link'
  contact_company = u'Stadt Zürich'
  contact_name = u'Stadt Zürich'
  contact_mail = u'opendata@zuerich.ch'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
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
      area = {
        'type': construction['geometry']['type'],
        'coordinates': []
      }
      if area['type'] == 'Polygon':
        for latlon in construction['geometry']['coordinates'][0]:
          area['coordinates'].append([latlon[1], latlon[0]])
      elif area['type'] == 'MultiPolygon':
        for latlonlist in construction['geometry']['coordinates'][0]:
          latlonlist_result = []
          for latlon in latlonlist:
            latlonlist_result.append([latlon[1], latlon[0]])
          area['coordinates'].append(latlonlist_result)
      if len(construction['geometry']['coordinates']) == 1:
        area['type'] = 'Polygon'
        construction['geometry']['coordinates'] = construction['geometry']['coordinates'][0]
      if len(construction['geometry']['coordinates']) == 1:
        construction['geometry']['coordinates'] = construction['geometry']['coordinates'][0]
      current_construction.area = json.dumps(area)
      current_construction.updated_at = datetime.datetime.now()
      # save data
      db.session.add(current_construction)
      db.session.commit()
  
###############
### Hamburg ###
###############

class HamburgStadt(DefaultSource):
  id = 6
  title = u'Stadt Hamburg'
  url = u'http://suche.transparenz.hamburg.de/dataset/baustellen-hamburg'
  source_url = u'http://geodienste-hamburg.de/HH_WFS_BWVI_opendata?service=WFS&request=GetFeature&VERSION=1.1.0&typename=verkehr_baustellen_prod'
  contact_company = u'Freie und Hansestadt Hamburg, Behörde für Wirtschaft Verkehr und Innovation'
  contact_name = u'Stadt Hamburg'
  contact_mail = u'transparenzportal@kb.hamburg.de'
  licence_name = u'Datenlizenz Deutschland Namensnennung 2.0'
  licence_url = u'https://www.govdata.de/dl-de/by-2-0'
  active = True
  mapping = {}
  
  def sync(self):
    request_data = requests.get(self.source_url)
    data = ElementTree.fromstring(request_data.content)
    for construction in data:
      current_external_id = construction[0].attrib['{http://www.opengis.net/gml}id']
      current_construction = ConstructionSite.query.filter_by(external_id=current_external_id).filter_by(source_id=self.id).first()
      # no database entry
      if not current_construction:
        current_construction = ConstructionSite()
        current_construction.external_id = current_external_id
        current_construction.created_at = datetime.datetime.now()
        current_construction.source_id = self.id
      # refresh values
      location_descr = []
      for item in construction[0]:
        if item.tag == '{http://www.deegree.org/app}strasse':
          location_descr.append(item.text)
        elif item.tag == '{http://www.deegree.org/app}abschnitt_von':
          if item.text:
            location_descr.append('von ' + item.text)
        elif item.tag == '{http://www.deegree.org/app}abschnitt_bis':
          if item.text:
            location_descr.append('bis ' + item.text)
        elif item.tag == '{http://www.deegree.org/app}beginn':
          if item.text:
            date_begin = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', item.text)
            if date_begin:
              current_construction.begin = datetime.datetime(int(date_begin.group(3)), int(date_begin.group(2)), int(date_begin.group(1)), 0, 0, 0)
        elif item.tag == '{http://www.deegree.org/app}ende':
          if item.text:
            date_end = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', item.text)
            if date_end:
              current_construction.end = datetime.datetime(int(date_end.group(3)), int(date_end.group(2)), int(date_end.group(1)), 23, 59, 59)
        elif item.tag == '{http://www.deegree.org/app}art':
          current_construction.descr = item.text
        elif item.tag == '{http://www.deegree.org/app}geom':
          location = self.epsg258322latlon(item[0][0].text.split()[0], item[0][0].text.split()[1])
          current_construction.lat = location['lat']
          current_construction.lon = location['lon']
      current_construction.location_descr = ' '.join(location_descr)
      current_construction.licence_name = self.licence_name
      current_construction.licence_url = self.licence_url
      current_construction.licence_owner = self.contact_company
      current_construction.updated_at = datetime.datetime.now()
      # save data
      db.session.add(current_construction)
      db.session.commit()

#################
### NRW (MDM) ###
#################

class NordrheinwestfalenMdm(DefaultSource):
  id = 7
  title = u'Nordrhein-Westfalen (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645005/clientPullService?subscriptionID=2645005'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class BadenwuerttembergMdm(DefaultSource):
  id = 8
  title = u'Baden-Württemberg (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2644004/clientPullService?subscriptionID=2644004'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class BayernMdm(DefaultSource):
  id = 9
  title = u'Bayern (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2644005/clientPullService?subscriptionID=2644005'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class BrandenburgMdm(DefaultSource):
  id = 10
  title = u'Brandenburg (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2644006/clientPullService?subscriptionID=2644006'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class BremenMdm(DefaultSource):
  id = 11
  title = u'Bremen (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2644007/clientPullService?subscriptionID=2644007'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class HamburgMdm(DefaultSource):
  id = 12
  title = u'Hamburg (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645002/clientPullService?subscriptionID=2645002'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class HessenMdm(DefaultSource):
  id = 13
  title = u'Hessen (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645003/clientPullService?subscriptionID=2645003'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class MecklenburgvorpommernMdm(DefaultSource):
  id = 14
  title = u'Mecklenburg-Vorpommern (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645004/clientPullService?subscriptionID=2645004'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class SachsenMdm(DefaultSource):
  id = 15
  title = u'Sachsen (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645006/clientPullService?subscriptionID=2645006'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class SachsenanhaltMdm(DefaultSource):
  id = 16
  title = u'Sachsen-Anhalt (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645007/clientPullService?subscriptionID=2645007'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class ThueringenMdm(DefaultSource):
  id = 17
  title = u'Thüringen (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2645008/clientPullService?subscriptionID=2645008'
  contact_company = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_name = u'Baustelleninformationssystem des Bundes und der Länder'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class SaarlandMdm(DefaultSource):
  id = 18
  title = u'Saarland (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2649000/clientPullService?subscriptionID=2649000'
  contact_company = u'Landesbetrieb für Straßenbau Saarland (LfS)'
  contact_name = u'Landesbetrieb für Straßenbau Saarland (LfS)'
  contact_mail = u'-'
  licence_name = u'gemeinfrei (CC-0)'
  licence_url = u'https://creativecommons.org/publicdomain/zero/1.0/'
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class RheinlandpfalzMdm(DefaultSource):
  id = 19
  title = u'Rheinland-Pfalz (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2647000/clientPullService?subscriptionID=2647000'
  contact_company = u'Landesbetrieb Mobilität Rheinland-Pfalz'
  contact_name = u'Landesbetrieb Mobilität Rheinland-Pfalz'
  contact_mail = u'-'
  licence_name = u'unbekannt'
  licence_url = u''
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class SchleswigholsteinMdm(DefaultSource):
  id = 20
  title = u'Schlewsig-Holstein (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2648000/clientPullService?subscriptionID=2648000'
  contact_company = u'Landesbetrieb Straßenbau und Verkehr Schleswig-Holstein'
  contact_name = u'Landesbetrieb Straßenbau und Verkehr Schleswig-Holstein'
  contact_mail = u'-'
  licence_name = u'unbekannt'
  licence_url = u''
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()

class NiedersachsenMdm(DefaultSource):
  id = 21
  title = u'Niedersachsen (MDM)'
  url = u'http://www.mdm-portal.de/'
  source_url = u'https://service.mac.mdm-portal.de/BASt-MDM-Interface/srv/2655000/clientPullService?subscriptionID=2655000'
  contact_company = u'Landesbetrieb Straßenbau und Verkehr Schleswig-Holstein'
  contact_name = u'Niedersächsische Landesbehörde für Straßenbau und Verkehr'
  contact_mail = u'-'
  licence_name = u'unbekannt'
  licence_url = u''
  active = True
  mapping = {}
  
  def sync(self):
    self.sync_mdm()