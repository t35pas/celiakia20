from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Receta(db.Model):
    __tablename__ = 'receta'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    titulo = db.Column(db.String(), nullable = False)
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    calificacion = db.Column(db.Integer, default = 0)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')
    id_dificultad = db.Column(db.Integer, db.ForeignKey('dificultad.id'), nullable = False)
    id_administrador = db.Column(db.Integer, db.ForeignKey('administrador.id'), nullable = False)

    def __init__(self, titulo, calificacion, tiempo_preparacion, id_dificultad, nombre_imagen, fecha_modificacion, fecha_creacion, id_administrador):
        self.titulo = titulo
        self.calificacion = calificacion
        self.id_dificultad = id_dificultad
        self.nombre_imagen = nombre_imagen
        self.fecha_modificacion = fecha_modificacion
        self.fecha_creacion = fecha_creacion
        self.id_administrador = id_administrador

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def json(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'calificacion': self.calificacion,
            'id_dificultad':self.id_dificultad,
            'nombre_imagen':self.nombre_imagen,
            'id_administrador':self.id_administrador,
            'fecha_creacion':self.fecha_creacion,
            'fecha_modificacion':self.fecha_modificacion
    }

    @classmethod
    def find_by_id(cls, idReceta):
        return cls.query.filter_by(id=idReceta).first()

    @classmethod
    def find_by_name(cls, nombre):
        return cls.query.filter_by(titulo=nombre).first()

    @classmethod
    def find_by_file(cls, nombreImagen):
        return cls.query.filter_by(nombre_imagen=nombreImagen).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

