from enum import unique
from app import db, loginManager
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_login import UserMixin


@loginManager.user_loader
def load_User(id_user):
    return Usuario.query.get(int(id_user))

class Dificultad(db.Model):
    __tablename__ = 'dificultad'
    __table_args__ = {'extend_existing': True} 


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(30), unique = True, nullable = False)
    recetas = relationship('Receta', backref = 'dificultad')
    

    def __init__(self, descripcion):
        self.descripcion = descripcion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
    }

    @classmethod
    def find_by_id(cls, idDif):
        return cls.query.filter_by(id=idDif).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Favorito(db.Model):
    __tablename__ = 'favorito'
    __table_args__ = {'extend_existing': True} 


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __init__(self, id_receta, id_usuario):
        self.id_receta = id_receta
        self.id_usuario = id_usuario

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def json(self):
        return {
            'id': self.id,
            'id_receta': self.id_receta,
            'id_usuario': self.id_usuario
    }

    @classmethod
    def find_by_id(cls, idFav):
        return cls.query.filter_by(id=idFav).first()

    @classmethod
    def find_by_receta(cls, idReceta):
        return cls.query.filter_by(id_receta=idReceta).first()

    @classmethod
    def find_by_receta_usuario(cls, idReceta, idUsuario):
        return cls.query.filter((cls.id_receta==idReceta) & (cls.id_usuario==idUsuario)).first()


    @classmethod
    def find_favoritas_usuario(cls, idUsuario):
        favoritos = cls.query.filter_by(id_usuario=idUsuario).all()
        recetas = []
        for favorito in favoritos:
            recetas.append(Receta.find_by_id(favorito.id_receta))
        return recetas

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Ingrediente_Por_Receta(db.Model):
    __tablename__ = 'ingrediente_por_receta'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable = False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable = False)
    id_unidad = db.Column(db.Integer, db.ForeignKey('unidad.id'), nullable = False)
    cantidad = db.Column(db.String, nullable = False)
    

    def __init__(self, id_receta, id_ingrediente, id_unidad, cantidad):
        self.id_receta = id_receta
        self.id_ingrediente = id_ingrediente
        self.id_unidad = id_unidad
        self.cantidad = cantidad

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def json(self):
        return {
            'id': self.id,
            'id_receta': self.id_receta,
            'id_ingrediente': self.id_ingrediente,
            'id_unidad':self.id_unidad,
            'cantidad': self.cantidad
    }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_receta(cls, idReceta):
        return cls.query.filter_by(id_receta=idReceta).all()
    
    @classmethod
    def any_ingrediente_receta(cls,idIngrediente,idReceta):
        for ixr in cls.find_by_receta(idReceta):    
            if idIngrediente == ixr.id_ingrediente:
                return True
        return False

    def update_to_db(self,ingrediente,unidad,cantidad):
        self.id_ingrediente = ingrediente
        self.id_unidad = unidad
        self.cantidad = cantidad
        db.session.commit()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Ingrediente(db.Model):
    __tablename__ = 'ingrediente'
    __table_args__ = {'extend_existing': True} 

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

    @classmethod
    def find_by_list_id(cls, ingredientes_id):
        return [cls.find_by_id(id) for id in ingredientes_id]

    @classmethod
    def find_by_descripcion(cls, ingrediente_descripcion):
        return cls.query.filter_by(descripcion = ingrediente_descripcion).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Preparacion(db.Model):
    __tablename__ = 'preparacion'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable = False)
    orden_del_paso = db.Column(db.Integer, nullable = False)
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
        return cls.query.filter_by(id_receta=idReceta).all()

    @classmethod
    def find_by_paso_receta(cls, ordenPaso,idReceta):
        return cls.query.filter_by(id_receta = idReceta, orden_del_paso = ordenPaso).first()

    def update_to_db(self,orden,tiempo,descripcion):
        self.orden_del_paso = orden
        self.descripcion = descripcion
        self.tiempo_preparacion = tiempo
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()        

class Receta(db.Model):
    __tablename__ = 'receta'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    titulo = db.Column(db.String(), nullable = False)
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default = datetime.utcnow)
    nombre_imagen = db.Column(db.String(), nullable = False, default = 'sin_imagen')
    descripcion = db.Column(db.Text(), nullable = False)
    id_dificultad = db.Column(db.Integer, db.ForeignKey('dificultad.id'), nullable = False)
    id_autor = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable = False)
    preparacion = relationship('Preparacion', backref = 'receta')
    ingrediente = relationship('Ingrediente_Por_Receta', backref = 'receta')
    favorita = relationship('Favorito', backref = 'receta')
    

    def __init__(self, titulo, id_dificultad, descripcion, nombre_imagen, fecha_modificacion, fecha_creacion, id_autor):
        self.titulo = titulo
        self.id_dificultad = id_dificultad
        self.descripcion = descripcion
        self.nombre_imagen = nombre_imagen
        self.fecha_modificacion = fecha_modificacion
        self.fecha_creacion = fecha_creacion
        self.id_autor = id_autor

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def json(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'id_dificultad':self.id_dificultad,
            'descripcion':self.descripcion,
            'nombre_imagen':self.nombre_imagen,
            'id_autor':self.id_autor,
            'fecha_creacion':self.fecha_creacion,
            'fecha_modificacion':self.fecha_modificacion
    }

    @classmethod
    def find_by_id(cls, idReceta):
        return cls.query.filter_by(id=idReceta).first()

    @classmethod
    def find_by_list_id(cls, recetas_id):
        return [cls.find_by_id(id) for id in recetas_id]

    @classmethod
    def find_by_name(cls, nombre):
        return cls.query.filter_by(titulo=nombre).first()

    @classmethod
    def find_like_name(cls, nombre):
        nombre = "%{}%".format(nombre)
        return cls.query.filter(cls.titulo.ilike(nombre)).all()

    @classmethod
    def find_by_file(cls, nombreImagen):
        return cls.query.filter_by(nombre_imagen=nombreImagen).first()

    def tiempoPreparacion(cls, idReceta):
        receta = cls.query.get(idReceta)
        tiempoPreparacion = 0
        for paso in receta.preparacion:
            tiempoPreparacion = tiempoPreparacion + paso.tiempo_preparacion
        return tiempoPreparacion

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Unidad(db.Model):
    __tablename__ = 'unidad'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(30), unique = True, nullable = False)
    ingredientes = relationship('Ingrediente_Por_Receta', backref = 'unidad')

    def __init__(self, descripcion):
        self.descripcion = descripcion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
    }

    @classmethod
    def find_by_id(cls, idUnidad):
        return cls.query.filter_by(id=idUnidad).first()

    @classmethod
    def find_by_descripcion(cls, unidad_descripcion):
        return cls.query.filter_by(descripcion=unidad_descripcion).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Usuario(db.Model, UserMixin):

    __tablename__ = 'usuario'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String())
    apellido = db.Column(db.String())
    email = db.Column(db.String())
    id_token = db.Column(db.String())
    favoritos = relationship('Favorito', backref = 'usuario')
    administrador = db.Column(db.Boolean())
    recetas = relationship('Receta', backref = 'receta_autor', lazy = True)
    
    
    def __init__(self, nombre, apellido, email, id_token):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.id_token = id_token

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email':self.email,
            'id_token':self.id_token
    }

    @classmethod
    def find_by_id(cls, idUsuario):
        return cls.query.filter_by(id=idUsuario).first()

    @classmethod
    def find_by_email(cls, mail):
        return cls.query.filter_by(email=mail).first()

    @classmethod
    def find_admin(cls):
        return cls.query.filter_by(administrador=True).all()

    @classmethod
    def find_users(cls):
        return cls.query.filter((cls.administrador==False) | (cls.administrador == None)).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

