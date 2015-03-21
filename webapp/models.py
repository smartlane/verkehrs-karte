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
  constructor = db.Column(db.Text()) # Bauherr
  execution = db.Column(db.Text()) # Ausführendes Bauunternehmen
  position_descr = db.Column(db.Text()) # Ausführendes Bauunternehmen
  
  source = db.Column(db.Integer()) # Quelle, definiert in config
  
  area = db.Column(db.Text()) # GeoJSON
  city = db.Column(db.Integer()) # City ID, definiert in config
  
  lat = db.Column(db.Numeric(precision=10,scale=7))
  lng = db.Column(db.Numeric(precision=10,scale=7))
  
  # external_id = db.Column(db.String(255))
  
  begin = db.Column(db.DateTime())
  end = db.Column(db.DateTime())
  
  created_at = db.Column(db.DateTime())
  updated_at = db.Column(db.DateTime())
  
  def __init__(self):
    pass

  def __repr__(self):
    return '<ConstructionSite %r>' % self.id

