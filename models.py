from sqlalchemy.sql import func
from config import db

field_harvest_table = db.Table('field_harvest',
                  db.Column('field_id', db.Integer, db.ForeignKey('field.id'), primary_key=True),
                  db.Column('harvest_id', db.Integer, db.ForeignKey('harvest.id'), primary_key=True)
                  )


class User(db.Model):
    __Tablename__ = "users"		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    admin = db.Column(db.Integer, server_default = "0")
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now()) 
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class Crop(db.Model):
    __Tablename__ = "crops"
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(255), unique = True) 

class Field(db.Model):
    __Tablename__ = "fields"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255))
    size = db.Column(db.Integer)
    field_name = db.Column(db.String(255), unique = True)
    field_that_have_harvest = db.relationship('Harvest', lazy = 'dynamic', secondary = field_harvest_table)

class Harvest(db.Model):
    __Tablename__ = "harvests"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    harvest_yield = db.Column(db.String(255))
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    crop = db.relationship('Crop', foreign_keys=[crop_id], backref="crops_harvest", cascade="all")
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    field = db.relationship('Field', foreign_keys=[field_id], backref="fields_harvest", cascade="all")
    harvest_that_have_field = db.relationship('Field', lazy = 'dynamic', secondary = field_harvest_table)

class Images(db.Model):
    __Tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255))
    year = db.Column(db.Integer)

class Map(db.Model):
    __Tablename__ = "maps"
    id = db.Column(db.Integer, primary_key=True)
    coordinates = db.Column(db.String(255))
    field = db.Column(db.String(255))

