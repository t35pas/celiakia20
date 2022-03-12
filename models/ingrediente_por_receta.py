from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Ingrediente_Por_Receta(db.Model):
    __tablename__ = 'ingrediente_por_receta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable = False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable = False)
    id_unidad = db.Column(db.Integer, db.ForeignKey('unidad.id'), nullable = False)
    cantidad = db.Column(db.Integer, nullable = False)
    

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
        return cls.query.filter_by(id_receta=id).first()

    @classmethod
    def find_by_receta(cls, idReceta):
        return cls.query.filter_by(id_receta=idReceta).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()