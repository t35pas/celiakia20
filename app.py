import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

from models import Receta, Preparacion, Dificultad, Unidad, Ingrediente, Ingrediente_Por_Receta, Usuario, Favorito

class Hola(Resource):
    def get(self, name):
        return {"Hello":name}

class Hola2(Resource):
    def get(self):
        return {"HOLASA":"HOLASA"}

@app.route("/recetas")
def get_recetas():
    try:
        recetas=Receta.query.all()
        return  jsonify([receta.serialize() for receta in recetas])
    except Exception as e:
	    return(str(e))

class RecetasPorNombre(Resource):
    def get(self, nombre):
        nombre = "%{}%".format(nombre)
        recetasPorNombre = Receta.query.filter(Receta.nombre.like(nombre)).all()
        return  jsonify([receta.serialize() for receta in recetasPorNombre])

class ObtenerImagen(Resource):
    def get(self, nombre):
        filename = 'imagenes/'+nombre
        return send_file(filename, mimetype='image/jpg')

api.add_resource(Hola, '/hola/<name>')
api.add_resource(Hola2, '/hola2')
api.add_resource(RecetasPorNombre, '/recetas/<nombre>')
api.add_resource(ObtenerImagen, '/obtener_imagen/<nombre>')

if __name__ == '__main__':
     app.run(debug=True)