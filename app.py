from datetime import datetime, timedelta
import imp
import json
import os

from sqlalchemy import true

basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Response,Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, send_from_directory, session, current_app
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
from forms import BuscarPorIngrediente, BuscarPorReceta,AgregarIngrediente, LoginForm, NuevaReceta, NuevaPreparacion, EditarPreparacion, EditarInfoGral, EditarIngrediente, SearchForm




@app.route('/gen/<passw>', methods = ['GET', 'POST'])
def create_user(passw):
    """Creates user with encrypted password"""
    # Hash the user password
    hashpass = generate_password_hash(
        passw,
        method='pbkdf2:sha256'
    )
    return hashpass

def formato_fecha(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} {}, {}".format(month,day, year)

    return messsage

def guardar_imagen(nombreImagen, imagen):
        filename = secure_filename(nombreImagen)
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return true 


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
        return render_template('login.html', form = form)

@app.route('/inicio', methods = ['GET', 'POST'])
@login_required
def Home():        
        return render_template('admin_home.html', 
                                user = current_user,
                                time = formato_fecha(datetime.now()))


@app.route('/recetas', methods = ['GET', 'POST'])
@login_required
def Listado():
        recetas = Receta.query.all()
        return render_template('admin_recetas.html', 
                                recetas = recetas, 
                                user = current_user,
                                time = formato_fecha(datetime.now()))


@app.route('/nuevo/receta', methods = ['GET', 'POST'])
@login_required
def InfoGeneral():
        receta = NuevaReceta()
        receta.dificultad.choices = [(dif.id, dif.descripcion) for dif in Dificultad.query.all()]
        print( "Estoy en info gral")
        if receta.validate_on_submit():
                print("ejecute un post")
                nombreImagen = receta.nombreImagen.data
                imagen = receta.imagenReceta.data
                guardarImagen = guardar_imagen(nombreImagen,imagen)
                
                if guardarImagen:
                
                        nuevaReceta = Receta(
                                        titulo = receta.tituloReceta.data, 
                                        fecha_creacion = datetime.now(),
                                        fecha_modificacion = datetime.now(),
                                        calificacion = 5,
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
                else:
                        return redirect(url_for('InfoGeneral'))
        return render_template('admin_nr_info_gral.html', 
                                form = receta, 
                                user = current_user,
                                time = formato_fecha(datetime.now()))

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

                        if idIXR == '0': #CREACION DE UN INGREDIENTE EN LA RECETA
                                print("es 0")
                                ingredienteXreceta = Ingrediente_Por_Receta(
                                        id_receta = idReceta, 
                                        id_ingrediente = idIngrediente,
                                        cantidad = cantidad,
                                        id_unidad = idUnidad
                                )
                                Ingrediente_Por_Receta.save_to_db(ingredienteXreceta)       
                                return redirect(url_for('IngPorReceta'))
                        elif idIXR != '0': #ACTUALIZACION DE UN INGREDIENTE EN LA RECETA

                                ingrXreceta = Ingrediente_Por_Receta.find_by_id(idIXR)
                                Ingrediente_Por_Receta.update_to_db(ingrXreceta,idIngrediente,idUnidad,cantidad)
                                return redirect(url_for('IngPorReceta'))
                else:
                        if idIXR != '0': #GET INGREDIENTE A ACTUALIZAR
                                ingrXreceta = Ingrediente_Por_Receta.find_by_id(idIXR)
                                if ingrXreceta:
                                        ingrediente.descripcionIngrediente.data = ingrXreceta.id_ingrediente
                                        ingrediente.cantidad.data = ingrXreceta.cantidad
                                        ingrediente.unidad.data = ingrXreceta.id_unidad
                                        return render_template('admin_nr_ingredientes.html', 
                                                                form = ingrediente, 
                                                                ingredientesXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta), 
                                                                user = current_user,
                                                                idIXR = ingrXreceta.id,
                                                                time = formato_fecha(datetime.now()))
                                
                                return render_template('admin_nr_ingredientes.html',
                                                        form = ingrediente, 
                                                        ingredientesXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta), 
                                                        user = current_user,
                                                        idIXR = '0',
                                                        time = formato_fecha(datetime.now()))
                        
                        elif idIXR == '0':
                                return render_template('admin_nr_ingredientes.html',
                                                        form = ingrediente, 
                                                        ingredientesXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta), 
                                                        user = current_user,
                                                        idIXR = '0',
                                                        time = formato_fecha(datetime.now()))
        else:
                print('no esta en session')
                return redirect(url_for('Home'))

@app.route('/nuevo/preparacion', methods = ['GET', 'POST']) 
@app.route('/nuevo/preparacion/<idPrep>', methods = ['GET', 'POST'])
@login_required
def PrepPorReceta(idPrep='0'):
        idReceta = session.get('idReceta')
        if idReceta:
                preparacion = NuevaPreparacion()
                print(preparacion.errors)
                if preparacion.validate_on_submit():
                        print("Valide y voy a tomar los datos")
                        ordenPaso = preparacion.ordenPaso.data
                        descripcionPaso = preparacion.descripcionPaso.data
                        tiempoPaso = preparacion.tiempoPaso.data
                        
                        if idPrep == '0': #CREACION DE UN NUEVO PASO
                                print("es cero")
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
                        if idPrep != '0': #GET PASO A ACTUALIZAR
                                paso = Preparacion.find_by_id(idPrep)
                                if paso:
                                        print(paso.json())
                                        preparacion.ordenPaso.data = paso.orden_del_paso
                                        preparacion.descripcionPaso.data = paso.descripcion
                                        preparacion.tiempoPaso.data = paso.tiempo_preparacion
                                        return render_template('admin_nr_preparacion.html', 
                                                                form = preparacion, 
                                                                preparacion = Preparacion.find_by_receta(idReceta), 
                                                                user = current_user,
                                                                idPrep = paso.id,
                                                                time = formato_fecha(datetime.now()))

                                return render_template('admin_nr_preparacion.html', 
                                                        form = preparacion, 
                                                        preparacion = Preparacion.find_by_receta(idReceta), 
                                                        user = current_user,
                                                        idPrep='0',
                                                        time = formato_fecha(datetime.now()))

                        else:
                                return render_template('admin_nr_preparacion.html', 
                                                        form = preparacion, 
                                                        preparacion = Preparacion.find_by_receta(idReceta), 
                                                        user = current_user,
                                                        idPrep='0',
                                                        time = formato_fecha(datetime.now()))

        else: 
                return redirect(url_for('Home'))

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

@app.route('/cancelar', methods = ['GET'])
@login_required
def Cancelar():
        idReceta = session.get('idReceta')
        
        if idReceta:
                receta = Receta.find_by_id(idReceta)
                ingrXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta)
                preparacion = Preparacion.find_by_receta(idReceta)
                print(ingrXreceta)
                print(preparacion)
                if preparacion: 
                        for paso in preparacion:
                                Preparacion.delete_from_db(paso)
                
                if ingrXreceta:
                        for ingrediente in ingrXreceta:   
                                Ingrediente_Por_Receta.delete_from_db(ingrediente)
                Receta.delete_from_db(receta)
                session.pop('idReceta', None)
        return redirect(url_for('Listado'))

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
                        Ingrediente_Por_Receta.delete_from_db(ingrediente)
    
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
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def paginaInicio():
        recetas = []
        return render_template('index.html', form=BuscarPorReceta())

@app.route('/indexMundoCeliakia', methods = ['GET', 'POST'])
def paginaMundoCeliakia(name=None):
    return render_template('indexMundoCeliakia.html', name=name)

@app.route('/favoritos', methods = ['GET', 'POST'])
def paginaFavoritos(name=None):
    return render_template('indexFavoritos.html', name=name)

#Buscar Por Nombre de Receta
@app.route('/buscarPorNombre/<string:nombre>', methods = ['GET', 'POST'])
def BuscarPorNombre(nombre):
    current_app.logger.info('BuscarPorNombre')
    recetas = []
    recetas.append(Receta.query.filter_by(titulo=nombre).first())
    current_app.logger.info('Longitud de recetas '+str(len(recetas)))
    return render_template('indexRecetas.html', num_recetas=len(recetas))


#Ver receta por nombre
@app.route('/recetasNombre' , methods = ['GET', 'POST'])
@app.route('/recetasNombre/<nombre>' , methods = ['GET', 'POST'])
def RecetasPorNombre(nombre=None):
        form = BuscarPorReceta()
        if form.validate_on_submit():
                nombre = form.nombreReceta.data
                recetasPorNombre = Receta.find_like_name(nombre)
                if 'nombreReceta' in session:
                        session.pop('nombreReceta', None)
                        session['nombreReceta'] = nombre
                else:
                        session['nombreReceta'] = nombre
                return  render_template('resultadoBusqueda.html', recetas=recetasPorNombre, nombre = nombre)
        elif request.method == 'GET':
                nombre=session.get('nombreReceta')
                recetasPorNombre = Receta.find_like_name(nombre)
                return  render_template('resultadoBusqueda.html', recetas=recetasPorNombre, nombre = nombre)
        elif request.method == 'GET' and nombre == None:
                return  redirect(url_for('paginaInicio'))

#Ver receta por ingrediente
ingredienteBusqueda = []
@app.route('/recetasIngrediente/agregar' , methods = ['GET', 'POST'])
def AgregarIngredienteBusqueda():
        form = BuscarPorIngrediente()
        if form.validate_on_submit() and len(ingredienteBusqueda) <= 5:
                nombre = form.nombreIngrediente.data
                ingrediente = Ingrediente.find_by_descripcion(nombre)
                if ingrediente.descripcion not in [i.descripcion for i in ingredienteBusqueda]:
                        ingredienteBusqueda.append(ingrediente)
                
                return  render_template('busquedaIngrediente.html', 
                                        form = form,
                                        ingredientes = ingredienteBusqueda)
        elif request.method == 'GET' :
                ingredienteBusqueda.clear()
                return  render_template('busquedaIngrediente.html', 
                                        form = form)

@app.route('/recetasIngrediente/eliminar/<ingrediente>/<ingredienteBusqueda>' , methods = ['GET'])
def EliminarIngredienteBusqueda(ingrediente,ingredienteBusqueda):
        if ingrediente.descripcion in [i.descripcion for i in ingredienteBusqueda]:
                ingredienteBusqueda.remove(ingrediente)
                return  render_template('busquedaIngrediente.html', 
                                        form = BuscarPorIngrediente(),
                                        ingredientes = ingredienteBusqueda)
@app.route('/recetasIngrediente' , methods = ['GET', 'POST'])
def RecetasPorIngrediente():
        if len(ingredienteBusqueda) > 0:
                nombre = []
                for i in ingredienteBusqueda:
                        nombre.append(i.descripcion)
                nombreBusqueda = ', '.join(nombre)
                recetas = Ingrediente_Por_Receta.find_recetas_by_ingredientes([i.id for i in ingredienteBusqueda])

                return  render_template('resultadoBusqueda.html', recetas=recetas, nombre = nombreBusqueda)

@app.route('/ObtenerImagen/<nombre>')
def ObtenerImagen(nombre):
        filename = '/app/static/'+ nombre
        return send_file(filename, mimetype='image/jpg')

@app.route('/verReceta/<idReceta>', methods = ['GET', 'POST'])
def VerReceta(idReceta):
        receta = Receta.find_by_id(idReceta)
        nombre = session.get('nombreReceta')
        return render_template('verReceta.html', 
                                receta = receta,
                                busqueda = nombre)

@app.route('/verFavorito', methods = ['GET', 'POST'])
def VerFavoritos():
        recetas = Favorito.find_favoritas_usuario(current_user.get_id())
        return render_template('indexFavoritos.html', recetas = recetas)


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
        IngredientesExistentes = [i.descripcion for i in Ingrediente.query.all()]
        return Response(json.dumps(IngredientesExistentes), mimetype='application/json')

if __name__ == '__main__':
     app.run(debug=True)
