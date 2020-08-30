from app import db

class Receta(db.Model):
    __tablename__ = 'receta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String())
    calificacion = db.Column(db.Integer)
    tiempo_preparacion = db.Column(db.Integer)
    id_dificultad = db.Column(db.Integer, db.ForeignKey('dificultad.id'))
    url_imagen = db.Column(db.String())

    def __init__(self, nombre, calificacion, tiempo_preparacion, id_dificultad, url_imagen):
        self.nombre = nombre
        self.calificacion = calificacion
        self.tiempo_preparacion = tiempo_preparacion
        self.id_dificultad = id_dificultad
        self.url_imagen = url_imagen

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'calificacion': self.calificacion,
            'tiempo_preparacion':self.tiempo_preparacion,
            'id_dificultad':self.id_dificultad,
            'url_imagen':self.url_imagen
}

class Preparacion(db.Model):
    __tablename__ = 'preparacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    orden_del_paso = db.Column(db.Integer)
    descripcion = db.Column(db.String())

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
    descripcion = db.Column(db.String())

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
    descripcion = db.Column(db.String())

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
    descripcion = db.Column(db.String())
    id_unidad = db.Column(db.Integer, db.ForeignKey('unidad.id'))

    def __init__(self, descripcion, id_unidad):
        self.descripcion = descripcion
        self.id_unidad = id_unidad

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'id_unidad': id_unidad
}

class Ingrediente_Por_Receta(db.Model):
    __tablename__ = 'ingrediente_por_receta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'))
    cantidad = db.Column(db.Integer)

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
            'id_ingrediente': id_ingrediente,
            'cantidad': cantidad
}

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String())
    apellido = db.Column(db.String())
    email = db.Column(db.String())

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