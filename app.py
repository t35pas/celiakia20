from datetime import datetime, timedelta
import imp
import os

from sqlalchemy import true

basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, send_from_directory, session, current_app
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './imagenes'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

db = SQLAlchemy(app)
api = Api(app)

bcrypt = Bcrypt(app) #Para encriptar las contrasenas
loginManager = LoginManager(app) #Para manejar las sesiones de los administradores
loginManager.login_view = 'Login'

from models import Administrador,Dificultad,Favorito,Ingrediente,Ingrediente_Por_Receta,Preparacion,Receta,Unidad,Usuario
from forms import AgregarIngrediente, LoginForm, NuevaReceta, NuevaPreparacion, EditarPreparacion, EditarInfoGral, EditarIngrediente




@app.route('/gen/<passw>', methods = ['GET', 'POST'])
def create_user(passw):
    """Creates user with encrypted password"""
    # Hash the user password
    hashpass = generate_password_hash(
        passw,
        method='pbkdf2:sha256'
    )
    return hashpass



@app.route('/', methods = ['GET', 'POST'])
@app.route('/login', methods = ['GET', 'POST'])
def Login():
        if current_user.is_authenticated:
                return redirect(url_for('Home'))
        form = LoginForm()
        if form.validate_on_submit():
                pasw = form.contrasenia.data
                nombreUsuario = form.nombreUsuario.data
                admin = Administrador.find_by_usuario(nombreUsuario)
                if admin and (admin.contrasenia == pasw) :
                #bcrypt.check_password_hash(admin.contrasenia, pasw):
                        login_user(admin)
                        print(current_user.nombre_usuario)
                        return redirect(url_for('Home'))
                else:
                        flash('Inicio incorrecto')
        return render_template('login2.html', form = form)

@app.route('/inicio', methods = ['GET', 'POST'])
@login_required
def Home():
        return render_template('inicio.html', user = current_user)

def guardar_imagen(nombreImagen, imagen):
        filename = secure_filename(nombreImagen)
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return true 

@app.route('/nuevo/receta', methods = ['GET', 'POST'])
@login_required
def InfoGeneral():
        receta = NuevaReceta()
        receta.dificultad.choices = [(dif.id, dif.descripcion) for dif in Dificultad.query.all()]
      
        if receta.validate_on_submit():
                
                nombreImagen = receta.nombreImagen.data
                imagen = receta.imagenReceta.data
                guardarImagen = guardar_imagen(nombreImagen,imagen)
                
                if guardarImagen:
                
                        nuevaReceta = Receta(
                                        titulo = receta.tituloReceta.data, 
                                        fecha_creacion = datetime.now(),
                                        fecha_modificacion = datetime.now(),
                                        calificacion = 5,
                                        tiempo_preparacion = receta.tiempoPreparacion.data,
                                        nombre_imagen = nombreImagen,
                                        id_dificultad = receta.dificultad.data,
                                        id_administrador = current_user.id 
                                )
                        Receta.save_to_db(nuevaReceta)
                        
                if 'idReceta' in session:
                        session.pop('idReceta', None)
                        session['idReceta'] = nuevaReceta.id
                else:
                        session['idReceta'] = nuevaReceta.id
                return redirect(url_for('IngPorReceta'))
        return render_template('nr_infoGeneral.html', form = receta, user = current_user)

@app.route('/nuevo/ingredientes', methods = ['GET', 'POST'])
@app.route('/nuevo/ingredientes/<idIXR>', methods = ['GET', 'POST'])
@login_required
def IngPorReceta(idIXR=0):
        idReceta = session.get('idReceta')
        print(idReceta)
        if idReceta:
                ingrediente = AgregarIngrediente()
                ingrediente.descripcionIngrediente.choices = [(i.id, i.descripcion) for i in Ingrediente.query.all()]
                ingrediente.unidad.choices = [(u.id, u.descripcion) for u in Unidad.query.all()]
                
                if ingrediente.validate_on_submit():
                        idIngrediente = ingrediente.descripcionIngrediente.data #esto ya me trae el ID del ingrediente
                        cantidad = ingrediente.cantidad.data
                        idUnidad = ingrediente.unidad.data #esto ya me trae el id de la unidad
                        
                        if idIXR == 0: #CREACION DE UN INGREDIENTE EN LA RECETA
                                ingredienteXreceta = Ingrediente_Por_Receta(
                                        id_receta = idReceta, 
                                        id_ingrediente = idIngrediente,
                                        cantidad = cantidad,
                                        id_unidad = idUnidad
                                )
                                Ingrediente_Por_Receta.save_to_db(ingredienteXreceta)       
                                return redirect(url_for('IngPorReceta'))
                        else: #ACTUALIZACION DE UN INGREDIENTE EN LA RECETA
                                ingrXreceta = Ingrediente_Por_Receta.find_by_id(idIXR)
                                Ingrediente_Por_Receta.update_to_db(ingrXreceta,idIngrediente,idUnidad,cantidad)
                                return redirect(url_for('IngPorReceta'))
                else:
                        if idIXR != 0: #GET INGREDIENTE A ACTUALIZAR
                                ingrXreceta = Ingrediente_Por_Receta.find_by_id(idIXR)
                                ingrediente.descripcionIngrediente.data = ingrXreceta.id_ingrediente
                                ingrediente.cantidad.data = ingrXreceta.cantidad
                                ingrediente.unidad.data = ingrXreceta.id_unidad
                                return render_template('nr_ingredientes.html', 
                                                form = ingrediente, 
                                                ingredientesXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta), 
                                                user = current_user,
                                                idIXR = ingrXreceta.id)
                        else:
                                return render_template('nr_ingredientes.html',
                                                form = ingrediente, 
                                                ingredientesXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta), 
                                                user = current_user,
                                                idIXR = 0)
        else:
                print('no esta en session')
                return redirect(url_for('Home'))

@app.route('/nuevo/preparacion', methods = ['GET', 'POST'])
@app.route('/nuevo/preparacion/<idPrep>', methods = ['GET', 'POST'])
@login_required
def PrepPorReceta(idPrep=0):
        idReceta = session.get('idReceta')
        if idReceta:
                preparacion = NuevaPreparacion()
                
                if preparacion.validate_on_submit():
                        ordenPaso = preparacion.ordenPaso.data
                        descripcionPaso = preparacion.descripcionPaso.data
                        tiempoPaso = preparacion.tiempoPaso.data
                        
                        if idPrep == 0: #CREACION DE UN NUEVO PASO
                                nuevoPaso = Preparacion(
                                        id_receta = idReceta,
                                        orden_del_paso = ordenPaso,
                                        descripcion = descripcionPaso,
                                        tiempo_preparacion=tiempoPaso
                                )
                                Preparacion.save_to_db(nuevoPaso)
                                return redirect(url_for('PrepPorReceta'))

                        else: #ACTUALIZACION DE UN PASO
                                paso = Preparacion.find_by_id(idPrep)
                                Preparacion.update_to_db(paso,ordenPaso,tiempoPaso,descripcionPaso)
                                return redirect(url_for('PrepPorReceta'))                        
                else:
                        if idPrep != 0: #GET PASO A ACTUALIZAR
                                paso = Preparacion.find_by_id(idPrep)
                                print(paso.json())
                                preparacion.ordenPaso.data = paso.orden_del_paso
                                preparacion.descripcionPaso.data = paso.descripcion
                                preparacion.tiempoPaso.data = paso.tiempo_preparacion
                                return render_template('nr_preparacion.html', 
                                                form = preparacion, 
                                                preparacion = Preparacion.find_by_receta(idReceta), 
                                                user = current_user,
                                                idPrep = paso.id)
                        else:
                                return render_template('nr_preparacion.html', 
                                                                form = preparacion, 
                                                                preparacion = Preparacion.find_by_receta(idReceta), 
                                                                user = current_user,
                                                                idPrep=0)

        else: 
                return redirect(url_for('Home'))

@app.route('/receta/<idReceta>', methods = ['GET', 'POST'])
@login_required
def VerReceta(idReceta):
        receta = Receta.query.get(idReceta)
        ingredientes = receta.ingredientes
        preparacion = receta.preparacion
        
        return render_template('ver_receta.html', 
                                user = current_user,
                                receta = receta,
                                ingredientes = ingredientes,
                                preparacion = preparacion)

@app.route('/ingredientes/eliminar/<idIxR>', methods = ['GET', 'POST'])
@login_required
def eliminarIngPorReceta(idIxR):
        idReceta = session.get('idReceta')
        if idReceta:
                ingrediente = Ingrediente_Por_Receta.find_by_id(idIxR)
                Ingrediente_Por_Receta.delete_from_db(ingrediente)
                flash('Ingrediente eliminado correctamente de la receta!')
                return redirect(url_for('IngPorReceta'))
        return redirect(url_for('Home'))

@app.route('/preparacion/eliminar/<idPrep>', methods = ['GET', 'POST'])
@login_required
def EliminarPrepPorReceta(idPrep):
        idReceta = session.get('idReceta')
        
        if idReceta:
                paso = Preparacion.find_by_id(idPrep)
                Preparacion.delete_from_db(paso)
                flash('Paso eliminado correctamente de la receta!')
                return redirect(url_for('PrepPorReceta'))
        return redirect(url_for('Home'))

@app.route('/recetas', methods = ['GET', 'POST'])
@login_required
def Listado():
        recetas = Receta.query.all()
        return render_template('listado_recetas.html', recetas = recetas, user = current_user)

@app.route('/recetas/eliminar/<idReceta>', methods = ['GET', 'POST'])
@login_required
def EliminarRecetaListado(idReceta):
        receta = Receta.find_by_id(idReceta)
        ingrXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta)
        preparacion = Preparacion.find_by_receta(idReceta)
    
        if preparacion: 
                for paso in preparacion:
                        Preparacion.delete_from_db(paso)
        
        if ingrXreceta:
                for ingrediente in ingrXreceta:   
                        Ingrediente_Por_Receta.delete_from_bd(ingrediente)
    
        Receta.delete_from_db(receta)
        flash('Eliminaste la receta con exito.')
        return redirect(url_for('Listado'))

#AUN EN PROCESO.. FALTA CORRECCION
@app.route('/receta/editar/<idReceta>/preparacion/<idPrep>', methods = ['GET', 'POST'])
@app.route('/receta/editar/<idReceta>', methods = ['GET', 'POST'])
@app.route('/receta/editar/<idReceta>/ingredientes/<idIxR>', methods = ['GET', 'POST'])
@login_required
def EditarReceta(idReceta, idIxR=0, idPrep=0):
        receta = Receta.query.get(idReceta)
        ingredientes = receta.ingredientes
        preparacion = receta.preparacion
        paso = Preparacion.query.get(idPrep)
        form = EditarInfoGral()
        formP = EditarPreparacion()
        formI = EditarIngrediente()
        if form.validate_on_submit():
                receta.titulo = form.tituloReceta.data
                receta.tiempo_preparacion = form.tiempoPreparacion.data
                receta.id_dificultad = form.dificultad.data
                receta.nombre_imagen = form.nombreImagen.data
                receta.fecha_modificacion = datetime.now()
                f = form.imagenReceta.data
                if f:
                        filename = secure_filename(receta.nombre_imagen)
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.session.commit()
        elif formP.validate_on_submit() and idPrep != 0:
                paso = Preparacion.query.get(idPrep)
                paso.orden_del_paso = form.ordenPaso.data
                paso.descripcion = form.descripcion.data
                db.session.commit()
        elif formI.validate_on_submit() and idIxR != 0:
                ingredienteXreceta = Ingrediente_Por_Receta.query.get(idIxR)
                ingrediente = Ingrediente.query.get(ingredienteXreceta.id_ingrediente)
                editarIngPorReceta(ingredienteXreceta, ingrediente, formI)
        elif request.method == 'GET':
                form.tituloReceta.data = receta.titulo
                form.tiempoPreparacion.data = receta.tiempo_preparacion
                form.dificultad.data = receta.id_dificultad
                form.nombreImagen.data = receta.nombre_imagen
                if idIxR != 0:
                        ingredienteXreceta = Ingrediente_Por_Receta.query.get(idIxR)
                        ingrediente = Ingrediente.query.get(ingredienteXreceta.id_ingrediente)
                        formI.nombreIngrediente.data = ingrediente.descripcion
                        formI.unidad.data = ingrediente.unidad.descripcion
                        formI.cantidad.data = ingredienteXreceta.cantidad
                        formI.nombreImagen.data = ingrediente.nombre_imagen
                if idPrep != 0:
                        paso = Preparacion.query.get(idPrep)
                        formP.ordenPaso.data = paso.orden_del_paso
                        formP.descripcion.data = paso.descripcion
        return render_template('editar_receta.html',
                                form = form, formI = formI, formP = formP,
                                ingredientes = ingredientes, receta = receta, preparacion = preparacion,
                                idPrep = idPrep, idIxR = idIxR, idReceta = idReceta,
                                user = current_user)

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def Logout():
        logout_user()
        return redirect(url_for('Login'))

#Aplicación CeliaKIA Web
recetas = []
@app.route('/index', methods = ['GET', 'POST'])
def paginaInicio():
    recetas = []
    return render_template('index.html')

@app.route('/indexMundoCeliakia', methods = ['GET', 'POST'])
def paginaMundoCeliakia(name=None):
    return render_template('indexMundoCeliakia.html', name=name)

#Buscar Por Nombre de Receta
@app.route('/buscarPorNombre/<nombre>', methods = ['GET', 'POST'])
def BuscarPorNombre(nombre):
    current_app.logger.info('BuscarPorNombre')
    recetas = []
    recetas.append(Receta.query.filter_by(titulo=nombre).first())
    current_app.logger.info('Longitud de recetas '+str(len(recetas)))
    return render_template('index.html', num_recetas=len(recetas))

if __name__ == '__main__':
     app.run(debug=True)
