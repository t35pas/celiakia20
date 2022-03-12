from app import db, loginManager
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_login import UserMixin

@loginManager.user_loader
def load_Admin(id_admin):
    return Administrador.query.get(int(id_admin))

class Administrador(db.Model, UserMixin):
    __tablename__ = 'administrador'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(), unique = True, nullable = False)
    contrasenia = db.Column(db.String(), nullable = False)
    email = db.Column(db.String(), unique = True, nullable = False)
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')

    def __init__(self, nombre_usuario, contrasenia, email, fecha_creacion, fecha_modificacion, nombre_imagen):
        self.nombre_usuario = nombre_usuario
        self.contrasenia = contrasenia
        self.email = email
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion
        self.nombre_imagen = nombre_imagen

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'contrasenia': self.contrasenia,
            'email': self.email,
            'fecha_creacion':self.fecha_creacion,
            'fecha_modificacion':self.fecha_modificacion,
            'nombre_imagen':self.nombre_imagen
    }

    @classmethod
    def find_by_id(cls, idAdmin):
        return cls.query.filter_by(id=idAdmin).first()

    @classmethod
    def find_by_usuario(cls, nombreUsuario):
        return cls.query.filter_by(nombre_usuario=nombreUsuario).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()