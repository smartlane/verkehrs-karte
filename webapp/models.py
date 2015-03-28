# encoding: utf-8

from sqlalchemy.ext.declarative import declarative_base
from webapp import db

Base = declarative_base()

class ConstructionSite (db.Model):
  __tablename__ = 'construction_site'
  
  id = db.Column(db.Integer(), primary_key=True)
  title = db.Column(db.String(255))
  
  descr = db.Column(db.Text()) # Allg. Beschreibung
  reason = db.Column(db.Text()) # Begründung für Baustelle
  type = db.Column(db.Text()) # Art der Verkehrseinschränkung
  constructor = db.Column(db.Text()) # Bauherr
  execution = db.Column(db.Text()) # Ausführendes Bauunternehmen
  location_descr = db.Column(db.Text()) # Ort
  restriction = db.Column(db.Text()) # Einschränkungen
  
  area = db.Column(db.Text()) # GeoJSON
  
  lat = db.Column(db.Numeric(precision=10,scale=7))
  lon = db.Column(db.Numeric(precision=10,scale=7))
  
  external_id = db.Column(db.String(255)) # Externe ID (innerhalb der Source einzigartig)
  external_url = db.Column(db.Text()) # Externe URL
  
  begin = db.Column(db.DateTime()) # Start der Baumaßnahme
  end = db.Column(db.DateTime()) # Ende der Baumaßnahme
  
  created_at = db.Column(db.DateTime())
  updated_at = db.Column(db.DateTime())
  
  source_id = db.Column(db.Integer()) # Quelle
  
  licence_name = db.Column(db.Text())
  licence_url = db.Column(db.Text())
  licence_owner = db.Column(db.Text())
  
  def __init__(self):
    pass

  def __repr__(self):
    return '<ConstructionSite %r>' % self.id