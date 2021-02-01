from enum import unique
from app import db
from datetime import datetime
from sqlalchemy.orm import defaultload, relationship


class Receta(db.Model):
    __tablename__ = 'receta'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    titulo = db.Column(db.String(), nullable = False)
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    calificacion = db.Column(db.Integer, default = 0)
    tiempo_preparacion = db.Column(db.Integer, unique = True, nullable = False)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')
    id_dificultad = db.Column(db.Integer, db.ForeignKey('dificultad.id'), nullable = False)
    id_administrador = db.Column(db.Integer, db.ForeignKey('administrador.id'), nullable = False)
    ingredientes = relationship('Ingrediente_Por_Receta', backref = 'receta')
    preparacion = relationship('Preparacion', backref = 'receta')
    favorita = relationship('Favorito', backref = 'receta')

    def __init__(self, titulo, calificacion, tiempo_preparacion, id_dificultad, nombre_imagen, fecha_modificacion, fecha_creacion, id_administrador):
        self.titulo = titulo
        self.calificacion = calificacion
        self.tiempo_preparacion = tiempo_preparacion
        self.id_dificultad = id_dificultad
        self.nombre_imagen = nombre_imagen
        self.fecha_modificacion = fecha_modificacion
        self.fecha_creacion = fecha_creacion
        self.id_administrador = id_administrador

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'calificacion': self.calificacion,
            'tiempo_preparacion':self.tiempo_preparacion,
            'id_dificultad':self.id_dificultad,
            'nombre_imagen':self.nombre_imagen,
            'id_administrador':self.id_administrador,
            'fecha_creacion':self.fecha_creacion,
            'fecha_modificacion':self.fecha_modificacion
}

class Preparacion(db.Model):
    __tablename__ = 'preparacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable = False)
    orden_del_paso = db.Column(db.Integer, unique = True, nullable = False)
    descripcion = db.Column(db.String(), nullable = False)

    def __init__(self, id_receta, orden_del_paso, descripcion):
        self.id_receta = id_receta
        self.orden_del_paso = orden_del_paso
        self.descripcion = descripcion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'id_receta': self.id_receta,
            'orden_del_paso': self.orden_del_paso,
            'descripcion':self.descripcion
}

class Dificultad(db.Model):
    __tablename__ = 'dificultad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(30), unique = True, nullable = False)
    recetas = relationship('Receta', backref = 'difcultad')

    def __init__(self, descripcion):
        self.descripcion = descripcion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
}

class Unidad(db.Model):
    __tablename__ = 'unidad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(30), unique = True, nullable = False)
    ingredientes = relationship('Ingrediente', backref = 'unidad')

    def __init__(self, descripcion):
        self.descripcion = descripcion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
}

class Ingrediente(db.Model):
    __tablename__ = 'ingrediente'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(), nullable = False)
    id_unidad = db.Column(db.Integer, db.ForeignKey('unidad.id'), nullable = False)
    por_receta = relationship('Ingrediente_Por_Receta', backref = 'ingredientes')
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')

    def __init__(self, descripcion, id_unidad, fecha_creacion, fecha_modificacion, nombre_imagen):
        self.descripcion = descripcion
        self.id_unidad = id_unidad
        self.nombre_imagen = nombre_imagen
        self.fecha_modificacion = fecha_modificacion
        self.fecha_creacion = fecha_creacion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion_ing': self.descripcion_ing,
            'id_unidad': self.id_unidad,
            'fecha_creacion':self.fecha_creacion,
            'fecha_modificacion':self.fecha_modificacion,
            'nombre_imagen':self.nombre_imagen
}

class Ingrediente_Por_Receta(db.Model):
    __tablename__ = 'ingrediente_por_receta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable = False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable = False)
    cantidad = db.Column(db.Integer, nullable = False)

    def __init__(self, id_receta, id_ingrediente, cantidad):
        self.id_receta = id_receta
        self.id_ingrediente = id_ingrediente
        self.cantidad = cantidad

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'id_receta': self.id_receta,
            'id_ingrediente': self.id_ingrediente,
            'cantidad': self.cantidad
}

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String())
    apellido = db.Column(db.String())
    email = db.Column(db.String())
    favoritos = relationship('Favorito', backref = 'usuario')
    

    def __init__(self, nombre, apellido, email):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email':self.email
}

class Favorito(db.Model):
    __tablename__ = 'favorito'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __init__(self, id_receta, id_usuario):
        self.id_receta = id_receta
        self.id_usuario = id_usuario

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'id_receta': self.id_receta,
            'id_usuario': self.id_usuario
}

class Administrador(db.Model):
    __tablename__ = 'administrador'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(), unique = True, nullable = False)
    contrasenia = db.Column(db.String(), nullable = False)
    email = db.Column(db.String(), unique = True, nullable = False)
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')
    recetas = relationship('Receta', backref = 'autor', lazy = True)

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