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