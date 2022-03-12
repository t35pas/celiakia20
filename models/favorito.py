from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

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
    def find_by_usuario(cls, idUsuario):
        return cls.query.filter_by(id_usaurio=idUsuario).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()