from datetime import datetime, timedelta
import imp
import json
import os
from traceback import print_tb
import numpy

from sqlalchemy import true

basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Response,Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, send_from_directory, session, send_from_directory
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy, Pagination
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './imagenes'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
ROWS_PER_PAGE = 5
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
db = SQLAlchemy(app)
api = Api(app)

bcrypt = Bcrypt(app) #Para encriptar las contrasenas
loginManager = LoginManager(app) #Para manejar las sesiones de los administradores
loginManager.login_view = 'Login'

from models import Dificultad,Favorito,Ingrediente,Ingrediente_Por_Receta,Preparacion,Receta,Unidad,Usuario
from forms import BuscarPorIngrediente, BuscarPorReceta,AgregarIngrediente, LoginForm, NuevaReceta, NuevaPreparacion, EditarPreparacion, EditarInfoGral, EditarIngrediente, SearchForm

from authentication import auth


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

def extension_permitida(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_imagen(nombre, imagen):

        if extension_permitida(imagen.filename):
                nombre, extension = os.path.splitext(imagen.filename)
                nombreImagen = nombre + extension
                print(nombreImagen)
                filename = secure_filename(nombreImagen)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return true 

def selectRandom():
        recetas = Receta.query.all()
        return numpy.random.choice(recetas, 2,False)

def ingredientes_en_receta(ingredientes):
        todas_recetas = Receta.query.all()
        # Lista de tuplas (receta, [descripcion de ingredientes de la receta])
        ingredientes_recetas = [(r.id, [i.ingredientes.descripcion for i in r.ingrediente]) for r in todas_recetas]
        print(ingredientes_recetas)
        recetas_elegidas = []
        en_receta = []

        for ir in ingredientes_recetas:
                en_receta.clear()
                for i in ingredientes:
                        if i in ir[1]:
                                en_receta.append(True)
                        else:
                                en_receta.append(False)
                if all(en_receta): 
                        recetas_elegidas.append(ir[0])
        #Devuelve el id de las recetas que contienen todos los ingredientes
        return  recetas_elegidas

def paginado(lista,pagina,cant_por_pagina):
        # obtener indice inicio e indice fin basado en el numero de pagina
        start = ((pagina - 1) * cant_por_pagina)
        end = start + cant_por_pagina
        # pagina 1 es [0:5], pagina 2 es [5:10]
        items = lista[start:end]
        print(items)
        lista_paginada = Pagination(None, pagina, cant_por_pagina, len(lista), items)
        return lista_paginada

@app.route('/login', methods = ['GET', 'POST'])
def Login():
        if current_user.is_authenticated:
                return redirect(url_for('PaginaInicio'))
        
        form = LoginForm()
        if form.validate_on_submit():
                passw = form.contrasenia.data
                email = form.nombreUsuario.data.strip()

                try:
                        iniciar_sesion = auth.sign_in_with_email_and_password(email,passw)
                        usuario = Usuario.find_by_email(email)
                        login_user(usuario)

                        if usuario.administrador == True:
                                session["administrador"] = True
                                session["fecha"] = formato_fecha(datetime.now())
                                return redirect(url_for('PaginaInicio'))
                        else: 
                                return redirect(url_for('PaginaInicio'))
                except:
                        return flash('Inicio incorrecto')
        return render_template('login.html', form = form)

#El login te redirige a la aplicación de recetas en perfil usuario.
#Por default se carga buscar por nombre de receta
@app.route('/', methods = ['GET', 'POST'])
@app.route('/recetasNombre', methods = ['GET', 'POST'])
@login_required
def PaginaInicio():
        #Cada vez que ingreso a busqueda por receta elimino session de ingredientes
        session.pop('ingredientes_id',None)
        return render_template('index.html', 
                                form = BuscarPorReceta(),
                                random = selectRandom())

#Ver receta por nombre
@app.route('/recetasNombre/buscar' , methods = ['GET', 'POST'])
def RecetasPorNombre():
        form = BuscarPorReceta()
        
        if form.validate_on_submit():
                nombre = form.nombreReceta.data
                #Obtengo el ID de las recetas con nombre "Parecido"
                recetas_id = [i.id for i in Receta.find_like_name(nombre)]
                #Guardo la busqueda para usarla en el template html
                session['busqueda'] = nombre
                #Guardo los ids de las recetas que coinciden con la busqueda
                session['recetas_id'] = recetas_id
                return  redirect(url_for('ResultadoBusqueda'))

#Ver receta por ingrediente
@app.route('/recetasIngrediente/buscar' , methods = ['GET', 'POST'])
@login_required
def RecetasPorIngrediente():
        if 'ingredientes_id' in session:
                #Obtengo de la session los ingredientes agregados a la busqueda
                ingredientes_id = session.get('ingredientes_id')
                listadoIngredientes = [Ingrediente.find_by_id(id) for id in ingredientes_id]

                if listadoIngredientes:
                        #Descripcion de ingredienetes a buscar
                        descr_ingredienetes = [i.descripcion for i in listadoIngredientes] 
                        #Concateno los ingredientes buscados para mostrarlo en el HTML
                        busqueda = ', '.join(descr_ingredienetes)
                        session['busqueda'] = busqueda
                        #Recetas que coinciden con ingredientes seleccionados
                        recetas_id = ingredientes_en_receta(descr_ingredienetes)
                        session['recetas_id'] = recetas_id
                session.pop('ingredientes_id',None)
                return  redirect(url_for('ResultadoBusqueda'))
        else:
                return  redirect(url_for('IngredienteBusqueda'))

#Ver receta por ingrediente
@app.route('/recetasIngrediente' , methods = ['GET', 'POST'])
@login_required
def IngredienteBusqueda():

        form = BuscarPorIngrediente()
        if 'ingredientes_id' in session:
                #Obtengo de la session los ingredientes agregados a la busqueda
                ingredientes_id = session.get('ingredientes_id')
                listadoIngredientes = [Ingrediente.find_by_id(id) for id in ingredientes_id]
                print(listadoIngredientes)
                if form.validate_on_submit():
                        #Recupero del Form la descripcion ingresada
                        nombre = form.nombreIngrediente.data
        
                        if nombre not in [i.descripcion for i in listadoIngredientes]:
                                ingrediente = Ingrediente.find_by_descripcion(nombre)
                                listadoIngredientes.append(ingrediente)
                                session['ingredientes_id'] = [i.id for i in listadoIngredientes]
                                return  redirect(url_for('IngredienteBusqueda'))
                        else:
                                #Error ingrediente ya existe en la busqueda
                                return  redirect(url_for('IngredienteBusqueda'))
                return render_template('busquedaIngrediente.html',
                                        form = form, 
                                        random = selectRandom(),
                                        ingredientes = listadoIngredientes)
        else:
                if form.validate_on_submit():
                        #Recupero del Form la descripcion ingresada
                        nombre = form.nombreIngrediente.data
                        ingrediente = Ingrediente.find_by_descripcion(nombre)

                        session['ingredientes_id'] = [ingrediente.id]
                        return  redirect(url_for('IngredienteBusqueda'))
                return render_template('busquedaIngrediente.html',
                                        form = form,
                                        random = selectRandom())

#Descartar listado de ingredientes actual e ingresar uno nuevo
@app.route('/recetasIngrediente/descartarBusqueda' , methods = ['GET'])
@login_required
def NuevaBusquedaPorIngredientes():
        if 'ingredientes_id' in session:
                session.pop('ingredientes_id',None)
                return redirect(url_for('IngredienteBusqueda'))
        else:
                return redirect(url_for('IngredienteBusqueda'))

#Eliminar un ingrediente del listado actual a buscar
@app.route('/recetasIngrediente/eliminarIngrediente/<desc_ingrediente>' , methods = ['GET'])
@login_required
def EliminarIngredienteBusqueda(desc_ingrediente):
        if 'ingredientes_id' in session:
                #Obtengo de la session los ingredientes agregados a la busqueda
                ingredientes_id = session.get('ingredientes_id')
                listadoIngredientes = Ingrediente.find_by_list_id(ingredientes_id)

                if desc_ingrediente in [i.descripcion for i in listadoIngredientes]:
                        ingrediente = Ingrediente.find_by_descripcion(desc_ingrediente)
                        listadoIngredientes.remove(ingrediente)
                        session['ingredientes_id'] = [i.id for i in listadoIngredientes]

                return redirect(url_for('IngredienteBusqueda'))
        else:
                return redirect(url_for('IngredienteBusqueda'))

#Muestra los resultados tanto de Busqueda por ingredientes como por recetas
@app.route('/resultadoBusqueda' , methods = ['GET', 'POST'])
@login_required
def ResultadoBusqueda():
        # Configuracion de paginado, toma la pagina.
        page = request.args.get('page', 1, type=int)
        recetas_id = session.get('recetas_id')
        recetas_obj = Receta.find_by_list_id(recetas_id)
        recetas = paginado(recetas_obj, page, ROWS_PER_PAGE)
        return  render_template('resultadoBusqueda.html', 
                                 recetas = recetas)


@app.route('/MundoCeliakia', methods = ['GET', 'POST'])
@login_required
def MundoCeliakia():
    return render_template('indexMundoCeliakia.html')

@app.route('/ObtenerImagen/<nombre>')
def ObtenerImagen(nombre):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nombre)

@app.route('/verReceta/<idReceta>', methods = ['GET', 'POST'])
@login_required
def VerReceta(idReceta):
        receta = Receta.find_by_id(idReceta)
        usuario = current_user.get_id()
        print(receta.favorita)
        if  Favorito.find_by_receta_usuario(receta.id,usuario):
                favorito = True
        else:
                favorito = False
        return render_template('verReceta.html', 
                                receta = receta,
                                favorito = favorito,
                                random = selectRandom())

@app.route('/misFavoritas', methods = ['GET', 'POST'])
@login_required
def MisFavoritas():
        recetas = Favorito.find_favoritas_usuario(current_user.get_id())
        print(recetas)
        return render_template('indexFavoritos.html', 
                                recetas = recetas, 
                                random = selectRandom())

@app.route('/agregarFavorita/<idReceta>', methods = ['GET', 'POST'])
@login_required
def AgregarFavorita(idReceta):
        receta = Receta.find_by_id(idReceta)
        usuario = current_user.get_id()
        
        favorito = Favorito.find_by_receta_usuario(receta.id,usuario)

        if favorito:
                return render_template('verReceta.html', 
                                receta = receta,
                                favorito = True,
                                random = selectRandom())
        else:
                favorito = Favorito(id_receta=receta.id,
                                id_usuario=usuario)
                favorito.save_to_db()
                print("Se agrego a favoritos")
                #AGREGAR ALGUN POP UP MOSTRANDO OK AGREGADO A FAVORITOS O ALGO#
                return render_template('verReceta.html', 
                                        receta = receta,
                                        favorito = True,
                                        random = selectRandom())

@app.route('/eliminarFavorita/<idReceta>', methods = ['GET', 'POST'])
@login_required
def EliminarFavorita(idReceta):
        receta = Receta.find_by_id(idReceta)
        usuario = current_user.get_id()
        
        favorito = Favorito.find_by_receta_usuario(receta.id,usuario)

        if favorito:
                Favorito.delete_from_db(favorito)
                print("Se elimino de favoritos")
                #AGREGAR ALGUN POP UP MOSTRANDO OK ELIMINADO DE FAVORITOS O ALGO#
                return render_template('verReceta.html', 
                                receta = receta,
                                favorito = False,
                                random = selectRandom())
        else:
                return render_template('verReceta.html', 
                                        receta = receta,
                                        favorito = False,
                                        random = selectRandom())


@app.route('/_autocomplete', methods=['GET'])
@login_required
def autocomplete():
        IngredientesExistentes = [i.descripcion for i in Ingrediente.query.all()]
        return Response(json.dumps(IngredientesExistentes), mimetype='application/json')





######### ADMINISTRADOR #########

@app.route('/inicioAdmin', methods = ['GET', 'POST'])
@login_required
def IndexAdmin():        
        return render_template('admin_home.html')

@app.route('/recetas', methods = ['GET', 'POST'])
@login_required
def Listado():
        recetas = Receta.query.all()
        return render_template('admin_recetas.html',
                                recetas = recetas)

@app.route('/nuevo/receta', methods = ['GET', 'POST'])
@login_required
def InfoGeneral():
        receta = NuevaReceta()
        receta.dificultad.choices = [(dif.id, dif.descripcion) for dif in Dificultad.query.all()]
        print( "Estoy en info gral")
        if receta.validate_on_submit():
                print("Quiero crear una receta")

                if receta.imagenReceta: 
                        nombreImagen = "rec_" + receta.tituloReceta.data.replace(' ', '').lower()
                        imagen = receta.imagenReceta.data

                        guardar_imagen(nombreImagen,imagen)

                        nuevaReceta = Receta(
                                                titulo = receta.tituloReceta.data, 
                                                fecha_creacion = datetime.now(),
                                                fecha_modificacion = datetime.now(),
                                                nombre_imagen = nombreImagen,
                                                id_dificultad = receta.dificultad.data,
                                                id_autor = current_user.id,
                                                descripcion = receta.descripcion.data
                                        )

                        Receta.save_to_db(nuevaReceta)

                        session['nuevaReceta_id'] = nuevaReceta.id

                        return redirect(url_for('IngPorReceta'))

        return render_template('admin_nr_info_gral.html', 
                                form = receta)


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
        session.pop('Administrador',None)
        return redirect(url_for('Login'))






if __name__ == '__main__':
     app.run(debug=True)
