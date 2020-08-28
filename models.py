from app import db


class Receta(db.Model):
    __tablename__ = 'receta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String())
    calificacion = db.Column(db.Integer)
    tiempoPreparacion = db.Column(db.Integer)

    def __init__(self, nombre, calificacion, tiempoPreparacion, nuevo):
        self.nombre = nombre
        self.calificacion = calificacion
        self.tiempoPreparacion = tiempoPreparacion

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'calificacion': self.calificacion,
            'tiempoPreparacion':self.tiempoPreparacion
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
    idReceta = db.Column(db.String(), db.ForeignKey('receta.id'))
    idUsuario = db.Column(db.String(), db.ForeignKey('usuario.id'))

   def __init__(self, idReceta, idUsuario):
        self.idReceta = idReceta
        self.idUsuario = idUsuario

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'idReceta': self.idReceta,
            'idUsuario': self.idUsuario
}