from app import db

class Receta(db.Model):
    __tablename__ = 'receta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String())
    calificacion = db.Column(db.Integer)
    tiempoPreparacion = db.Column(db.Integer)
    nuevo = db.Column(db.Integer)

    def __init__(self, nombre, calificacion, tiempoPreparacion, nuevo):
        self.nombre = nombre
        self.calificacion = calificacion
        self.tiempoPreparacion = tiempoPreparacion
        self.nuevo = nuevo

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'calificacion': self.calificacion,
            'tiempoPreparacion':self.tiempoPreparacion,
            'nuevo':self.nuevo
}