from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Preparacion(db.Model):
    __tablename__ = 'preparacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable = False)
    orden_del_paso = db.Column(db.Integer, unique = True, nullable = False)
    descripcion = db.Column(db.String(), nullable = False)
    tiempo_preparacion = db.Column(db.Integer, nullable = False)

    def __init__(self, id_receta, orden_del_paso, descripcion,tiempo_preparacion):
        self.id_receta = id_receta
        self.orden_del_paso = orden_del_paso
        self.descripcion = descripcion
        self.tiempo_preparacion = tiempo_preparacion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def json(self):
        return {
            'id': self.id,
            'id_receta': self.id_receta,
            'orden_del_paso': self.orden_del_paso,
            'tiempo_preparacion':self.tiempo_preparacion,
            'descripcion':self.descripcion
    }

    @classmethod
    def find_by_id(cls, idPreparacion):
        return cls.query.filter_by(id=idPreparacion).first()

    @classmethod
    def find_by_receta(cls, idReceta):
        return cls.query.filter_by(id_receta=idReceta)

    @classmethod
    def find_by_paso_receta(cls, ordenPaso,idReceta):
        return cls.query.filter_by(id_receta = idReceta, orden_del_paso = ordenPaso).first()
        
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()