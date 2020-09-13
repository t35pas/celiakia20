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

from models import Receta, Preparacion, Dificultad, Unidad, Ingrediente, Ingrediente_Por_Receta, Usuario, Favorito, Administrador

#Ver todas las recetas
@app.route('/receta')
def get_recetas():
    try:
        recetas = Receta.query.all()
        return  jsonify([receta.serialize() for receta in recetas])
    except Exception as e:
	    return(str(e))

#Ver receta particular
@app.route('/receta/<nombre>')
class RecetasPorNombre(Resource):
    def get(self, nombre):
        nombre = "%{}%".format(nombre)
        recetasPorNombre = Receta.query.filter(Receta.nombre.like(nombre)).all()
        return  jsonify([receta.serialize() for receta in recetasPorNombre])

@app.route('/obtener_imagen/<nombre>')
class ObtenerImagen(Resource):
    def get(self, nombre):
        filename = 'imagenes/'+ nombre
        return send_file(filename, mimetype='image/jpg')


#Aplicacion WEB
@app.route('/')
def Login():
        return render_template('login.html')

@app.route('/inicio', methods = ['POST','GET'])
def Index():
    if request.method == 'POST':
        nombre_admin = request.form['nombre_admin']
        password_admin = request.form['password_admin']
        admin_loggeando = Administrador.query.filter_by(nombre=nombre_admin).first()
        if (admin_loggeando.password == password_admin):
            recetas = Receta.query.join(Dificultad, Receta.id_dificultad == Dificultad.id).add_columns(Receta.id, Receta.titulo, Receta.calificacion, Receta.tiempo_preparacion, Receta.nombre_imagen, Dificultad.descripcion).all()
            return render_template('index.html', recetas = recetas)
        else:
            return redirect(url_for('Login'))
    else:
        recetas = Receta.query.join(Dificultad, Receta.id_dificultad == Dificultad.id).add_columns(Receta.id, Receta.titulo, Receta.calificacion, Receta.tiempo_preparacion, Receta.nombre_imagen, Dificultad.descripcion).all()
        return render_template('index.html', recetas = recetas)

@app.route('/receta/nueva')
def Nueva_receta():
        return render_template('crear_receta.html')

@app.route('/crear', methods = ['POST','GET'])
def Crear_receta():
    if request.method == 'POST':
        nombre = request.form['titulo']
        calificacion = request.form['calificacion']
        tiempo_preparacion = request.form['tiempo_preparacion']
        dificultad = request.form['dificultad']
        nombre_imagen = request.form['nombre_imagen']

        id_dificultad = Dificultad.query.filter_by(descripcion = dificultad).first()

        nueva_receta = Receta(nombre, calificacion, tiempo_preparacion, id_dificultad.id, nombre_imagen)
        
        db.session.add(nueva_receta)
        db.session.commit()

        flash('Receta agregada exitosamente!')
        return redirect(url_for('Index'))

@app.route('/editar/<id>')
def obtener_receta(id):
    receta = Receta.query.get(id)
    id_dif = receta.id_dificultad
    dificultad = Dificultad.query.get(id_dif)
    print(dificultad)
    return render_template('editar_receta.html', receta = receta, dificultad = dificultad)

@app.route('/actualizar/<id>', methods = ['POST'])
def actualizar_receta(id):
    if request.method == 'POST':
        nombre = request.form['titulo']
        calificacion = request.form['calificacion']
        tiempo_preparacion = request.form['tiempo_preparacion']
        dificultad = request.form['dificultad']
        nombre_imagen = request.form['nombre_imagen']
        
        id_dificultad = Dificultad.query.filter_by(descripcion=dificultad).first()
        receta_update = Receta.query.get(id)

        receta_update.titulo = nombre
        receta_update.calificacion = calificacion
        receta_update.id_dificultad = id_dificultad.id
        receta_update.tiempo_preparacion = tiempo_preparacion
        receta_update.nombre_imagen = nombre_imagen

        db.session.commit()

        flash('Receta actualizada') 
        return redirect(url_for('Index'))

@app.route('/eliminar/<id>')
def Eliminar_receta(id):
    receta = Receta.query.get(id)
    db.session.delete(receta)
    db.session.commit()
    flash('Receta eliminada correctamente')
    return redirect(url_for('Index'))

if __name__ == '__main__':
     app.run(debug=True)