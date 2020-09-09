import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

from models import Receta, Preparacion, Dificultad, Unidad, Ingrediente, Ingrediente_Por_Receta, Usuario, Favorito

@app.route('/hola/<name>')
class Hola(Resource):
    def get(self, name):
        return {"Hello":name}

@app.route('/hola2')
class Hola2(Resource):
    def get(self):
        return {"HOLASA":"HOLASA"}

@app.route('/recetas')
def get_recetas():
    try:
        recetas=Receta.query.all()
        return  jsonify([receta.serialize() for receta in recetas])
    except Exception as e:
	    return(str(e))

@app.route('/recetas/<nombre>')
class RecetasPorNombre(Resource):
    def get(self, nombre):
        nombre = "%{}%".format(nombre)
        recetasPorNombre = Receta.query.filter(Receta.nombre.like(nombre)).all()
        return  jsonify([receta.serialize() for receta in recetasPorNombre])

@app.route('/obtener_imagen/<nombre>')
class ObtenerImagen(Resource):
    def get(self, nombre):
        filename = 'imagenes/'+nombre
        return send_file(filename, mimetype='image/jpg')

@app.route('/')
def Login():
        return render_template('login.html')

@app.route('/crear')
def Crear_receta():
        return render_template('crear_receta.html')

@app.route('/ingresar', methods = ['POST','GET'])
def Ingresar():
    if request.method == 'POST':
        nombre_admin = request.form['nombre_admin']
        password_admin = request.form['password_admin']
    return render_template('index.html')

if __name__ == '__main__':
     app.run(debug=True)