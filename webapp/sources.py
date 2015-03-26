# encoding: utf-8
from models import *
from webapp import app, db
from lxml import etree, html
from lxml.cssselect import CSSSelector

class MoersEnni():
  id = 1
  region_id = 17
  title = 'Stadt Moers'
  url = 'https://www.enni.de/enni-gruppe/hier-bauen-wir.html'
  source_url = 'https://www.enni.de/enni-gruppe/hier-bauen-wir.html'
  contact_company = 'ENNI'
  contact_name = 'Claus Arndt'
  contact_mail = 'stadt@moers.de'
  
  def sync():
    request_data = requests.get(app.config['SOURCE'][0]['site'])
    doc = html.fromstring(request_data.content)
    table_trs_select = CSSSelector("#c6559 tr")
    table_trs = table_trs_select(doc)
    data = {}
    for table_tr in table_trs:
      if len(table_tr[1]) and table_tr[0][0].text:
        new_construction = ConstructionSite()
        new_construction.position_descr = table_tr[0][0].text
        new_construction.descr = table_tr[2][0].text
        new_construction.constructor = table_tr[3][0].text
        new_construction.created_at = datetime.datetime.now()
        new_construction.updated_at = datetime.datetime.now()
        new_construction.source = 1
        db.session.add(new_construction)
        db.session.commit()

class RostockStadt():
  id = 2
  region_id = 18
  title = 'Stadt Rostock'
  url = 'https://geo.sv.rostock.de/'
  source_url = 'https://geo.sv.rostock.de/download/opendata/baustellen/baustellen.json'
  contact_company = 'Rostock'
  contact_name = 'Stadt Rostock'
  contact_mail = 'stadt@rostock.de'
  active = True

  def sync():
    response = urllib.urlopen(self.source_url)
    data = json.loads(response.read())
    for construction in data["features"]:
      new_construction = ConstructionSite()
      new_construction.position_descr = construction["properties"]["strasse_name"]
      new_construction.descr = construction["properties"]["sperrung_art"] + " - " + construction["properties"]["sperrung_grund"]
      new_construction.constructor = construction["properties"]["gemeinde_name"]
      new_construction.execution = construction["properties"]["durchfuehrung"]
      new_construction.source = 2
      new_construction.lat = construction["geometry"]["coordinates"][1]
      new_construction.lng = construction["geometry"]["coordinates"][0]
      new_construction.begin = construction["properties"]["sperrung_anfang"]
      new_construction.end = construction["properties"]["sperrung_ende"]
      new_construction.created_at = datetime.datetime.now()
      new_construction.updated_at = datetime.datetime.now()
      db.session.add(new_construction)
      db.session.commit()

class AachenStadt():
  id = 3
  region_id = 19
  title = 'Stadt Aachen'
  url = 'http://offenedaten.aachen.de/dataset/baustellen-stadtgebiet-aachen'
  source_url = 'http://www.bsis.regioit.de/geoserver/BSISPROD/wms?service=wfs&version=2.0.0&request=GetFeature&typeNames=BSISPROD:Baustellen_7Tage_Punkte&outputFormat=json'
  contact_company = 'Aachen'
  contact_name = 'Stadt Aachen'
  contact_mail = 'stadt@aachen.de'
  active = True

  def sync():
    response = urllib.urlopen(self.source_url)
    data = json.loads(response.read())
    for construction in data["features"]:
      new_construction = ConstructionSite()
      new_construction.position_descr = construction["properties"]["strasse_name"]
      new_construction.descr = construction["properties"]["sperrung_art"] + " - " + construction["properties"]["sperrung_grund"]
      new_construction.constructor = construction["properties"]["gemeinde_name"]
      new_construction.execution = construction["properties"]["durchfuehrung"]
      new_construction.source = 2
      new_construction.lat = construction["geometry"]["coordinates"][1]
      new_construction.lng = construction["geometry"]["coordinates"][0]
      new_construction.begin = construction["properties"]["sperrung_anfang"]
      new_construction.end = construction["properties"]["sperrung_ende"]
      new_construction.created_at = datetime.datetime.now()
      new_construction.updated_at = datetime.datetime.now()
      db.session.add(new_construction)
      db.session.commit()