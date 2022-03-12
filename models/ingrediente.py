from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Ingrediente(db.Model):
    __tablename__ = 'ingrediente'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(), nullable = False)
    por_receta = relationship('Ingrediente_Por_Receta', backref = 'ingredientes')
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')

    def __init__(self, descripcion, fecha_creacion, fecha_modificacion, nombre_imagen):
        self.descripcion = descripcion
        self.nombre_imagen = nombre_imagen
        self.fecha_modificacion = fecha_modificacion
        self.fecha_creacion = fecha_creacion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion_ing': self.descripcion,
            'fecha_creacion':self.fecha_creacion,
            'fecha_modificacion':self.fecha_modificacion,
            'nombre_imagen':self.nombre_imagen
    }


    @classmethod
    def find_by_id(cls, idIngrediente):
        return cls.query.filter_by(id=idIngrediente).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()