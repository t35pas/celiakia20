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


from flask_uploads import UploadSet, IMAGES, configure_uploads

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
ROWS_PER_PAGE = 5
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
db = SQLAlchemy(app)
api = Api(app)
loginManager = LoginManager(app) #Para manejar las sesiones
loginManager.login_view = 'Login'

from models import Dificultad,Favorito,Ingrediente,Ingrediente_Por_Receta,Preparacion,Receta,Unidad,Usuario
from forms import ReseteoContrasenia, CrearUsuario,CrearAdmin,CrearDificultad,CrearUnidad,CrearIngrediente,CambiarImagen,Form_Editar_Ing_Por_Receta,BuscarPorIngrediente, BuscarPorReceta, LoginForm, Form_Ingrediente, Form_InformacionGeneral, Form_Preparacion
from authentication import auth

# CONFIGURACION IMAGENES DE LA APLICACION
UPLOAD_RECETAS = os.path.join('static', 'recetas')
UPLOAD_INGREDIENTES = os.path.join('static', 'ingredientes')
app.config["UPLOADED_IMGRECETAS_DEST"] = UPLOAD_RECETAS
app.config["UPLOADED_IMGINGREDIENTES_DEST"] = UPLOAD_INGREDIENTES
imgrecetas = UploadSet('imgrecetas', IMAGES,
                       app.config["UPLOADED_IMGRECETAS_DEST"])
imgingredientes = UploadSet(
    'imgingredientes', IMAGES, app.config["UPLOADED_IMGINGREDIENTES_DEST"])
configure_uploads(app, imgrecetas)
configure_uploads(app, imgingredientes)


def formato_fecha(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio",
              "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} {}, {}".format(month, day, year)

    return messsage


def extension_permitida(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def guardar_imagen(imagen, nombre, type):
    if extension_permitida(imagen.filename):
        _, extension = os.path.splitext(imagen.filename)
        print("La extension de mi imagen es:", extension)
        nombreImagen = nombre + extension
        print("Nombre imagen con la extension", nombreImagen)
        filename = secure_filename(nombreImagen)
        if type == 'R':
            imgrecetas.save(imagen, None, filename)
        elif type == 'I':
            imgingredientes.save(imagen, None, filename)
    return filename


def renombrar_imagen(nombreActual, nombreNuevo, type):

    if type == 'R':
        imgActual = os.path.join(
            app.config["UPLOADED_IMGRECETAS_DEST"], nombreActual)
        _, extension = os.path.splitext(nombreActual)
        nombreImagen = nombreNuevo + extension
        imgNueva = os.path.join(
            app.config["UPLOADED_IMGRECETAS_DEST"], nombreImagen)
    elif type == 'I':
        imgActual = os.path.join(
            app.config["UPLOADED_IMGINGREDIENTES_DEST"], nombreActual)
        _, extension = os.path.splitext(nombreActual)
        nombreImagen = nombreNuevo + extension
        imgNueva = os.path.join(
            app.config["UPLOADED_IMGINGREDIENTES_DEST"], nombreImagen)

    os.rename(imgActual, imgNueva)

    return nombreImagen


def selectRandom():
    recetas = Receta.query.all()
    return numpy.random.choice(recetas, 2, False)


def ingredientes_en_receta(ingredientes):
    todas_recetas = Receta.query.all()
    # Lista de tuplas (receta, [descripcion de ingredientes de la receta])
    ingredientes_recetas = [
        (r.id, [i.ingredientes.descripcion for i in r.ingrediente]) for r in todas_recetas]
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
    # Devuelve el id de las recetas que contienen todos los ingredientes
    return recetas_elegidas


def paginado(lista, pagina, cant_por_pagina):
    # obtener indice inicio e indice fin basado en el numero de pagina
    start = ((pagina - 1) * cant_por_pagina)
    end = start + cant_por_pagina
    # pagina 1 es [0:5], pagina 2 es [5:10]
    items = lista[start:end]
    print(items)
    lista_paginada = Pagination(
        None, pagina, cant_por_pagina, len(lista), items)
    return lista_paginada

##############################################################################
##                            LOG IN - LOG OUT                              ##
##############################################################################


@app.route('/login', methods=['GET', 'POST'])
def Login():
    if current_user.is_authenticated:
        return redirect(url_for('PaginaInicio'))

    form = LoginForm()
    if form.validate_on_submit():
        passw = form.contrasenia.data
        email = form.nombreUsuario.data.strip()

        try:
            iniciar_sesion = auth.sign_in_with_email_and_password(email, passw)
            usuario = Usuario.find_by_email(email)
            login_user(usuario)

            if usuario.administrador == True:
                session["administrador"] = True
                session["fecha"] = formato_fecha(datetime.now())
                return redirect(url_for('PaginaInicio'))
            else:
                return redirect(url_for('PaginaInicio'))
        except:
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/crearCuenta', methods=['GET', 'POST'])
def CrearCuenta():
    if current_user.is_authenticated:
        return redirect(url_for('PaginaInicio'))

    form = CrearUsuario()

    if form.validate_on_submit():
        nombre = form.nombreUsuario.data
        apellido = form.apellidoUsuario.data
        passw = form.contraseniaUsuario.data
        email = form.emailUsuario.data.strip()

        try:
            usuario = auth.create_user_with_email_and_password(email, passw)            
            nuevoUsuario = Usuario(nombre=nombre,
                                    apellido=apellido,
                                    email=email,
                                    id_token= usuario['idToken']
                                    )
            Usuario.save_to_db(nuevoUsuario)
            
            print(nuevoUsuario.id)

            if Usuario.find_by_id(nuevoUsuario.id):
                flash('La cuenta se creó exitosamente. Escribe tu email y contraseña para ingresar.')
                return redirect(url_for('Login'))
            else: 
                auth.delete_user_account(usuario['idToken'])
                flash('Hubo un error con tu cuenta, revisa nuevamente los datos ingresados.')
                return redirect(url_for('CrearCuenta'))    
        except:
            flash('Hubo un error con tu cuenta, revisa nuevamente los datos ingresados.')
            return redirect(url_for('CrearCuenta'))
        
    return render_template('crearCuenta.html', form=form)

@app.route('/reseteoContrasenia', methods=['GET', 'POST'])
def ResetearContrasenia():
    if current_user.is_authenticated:
        return redirect(url_for('PaginaInicio'))

    form = ReseteoContrasenia()

    if form.validate_on_submit():
        email = form.emailUsuario.data.strip()
        try:
            usuario = auth.send_password_reset_email(email)
            flash('Te enviamos un email a la cuenta de correo para que puedas resetear tu contraseña.')
            return redirect(url_for('Login'))
        except:
            flash('El correo ingresado no pertenece a una cuenta existente.')
            return redirect(url_for('ResetearContrasenia'))
    return render_template('resetearContrasenia.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def Logout():
    session.pop('Administrador', None)
    logout_user()
    return redirect(url_for('Login'))


##############################################################################
##                            INICIO APP USUARIO                            ##
##############################################################################

# El login te redirige a la aplicación de recetas en perfil usuario.
# Por default se carga buscar por nombre de receta
@app.route('/', methods=['GET', 'POST'])
@app.route('/recetasNombre', methods=['GET', 'POST'])
def PaginaInicio():

    if current_user.is_authenticated:
        # Cada vez que ingreso a busqueda por receta elimino session de ingredientes
        session.pop('ingredientes_id', None)
        if Receta.query.all():
            return render_template('index.html',
                                form=BuscarPorReceta(),
                                random=selectRandom())
        else:
            return render_template('index.html',
                                form=BuscarPorReceta())
    else:
        return redirect(url_for('Login'))

#Mundo de la celiakia
@app.route('/sobreNosotros', methods=['GET', 'POST'])
def SobreNosotros():
    return render_template('sobreNosotros.html',
                           random=selectRandom())
#Mundo de la celiakia
@app.route('/MundoCeliaKIA/<idPagina>', methods=['GET', 'POST'])
def MundoCeliakia(idPagina):
    if idPagina == '1':
        return render_template('mundoCeliakia/indexMundoCeliakia_1.html',
                           random=selectRandom())
    elif idPagina == '2':
        return render_template('mundoCeliakia/indexMundoCeliakia_2.html',
                           random=selectRandom())
    elif idPagina == '3':
        return render_template('mundoCeliakia/indexMundoCeliakia_3.html',
                           random=selectRandom())
    elif idPagina == '4':
        return render_template('mundoCeliakia/indexMundoCeliakia_4.html',
                           random=selectRandom())

#Mundo de la celiakia
@app.route('/MundoCeliaKIA/articulos/<idArticulo>', methods=['GET', 'POST'])
def MundoCeliakiaArticulo(idArticulo):
    if idArticulo == '1':
        return render_template('mundoCeliakia/enfermedadCeliaca.html',
                           random=selectRandom())
    elif idArticulo == '2':
        return render_template('mundoCeliakia/sintomas.html',
                           random=selectRandom())
    elif idArticulo == '3':
        return render_template('mundoCeliakia/diagnostico.html',
                           random=selectRandom())
    elif idArticulo == '4':
        return render_template('mundoCeliakia/dietaGlutenFree.html',
                           random=selectRandom())
    elif idArticulo == '5':
        return render_template('mundoCeliakia/contaminacionCruzada.html',
                           random=selectRandom())
    elif idArticulo == '6':
        return render_template('mundoCeliakia/ordenRefrigerador.html',
                           random=selectRandom())
    elif idArticulo == '7':
        return render_template('mundoCeliakia/comerFueraDeCasa.html',
                           random=selectRandom())
    elif idArticulo == '8':
        return render_template('mundoCeliakia/familiarCeliaco.html',
                           random=selectRandom())
    else:
        return render_template('mundoCeliakia/indexMundoCeliakia_1.html',
                           random=selectRandom())


# Ver receta por nombre

@app.route('/recetasNombre/buscar', methods=['GET', 'POST'])
def RecetasPorNombre():
    form = BuscarPorReceta()

    if form.validate_on_submit():
        nombre = form.nombreReceta.data
        # Obtengo el ID de las recetas con nombre "Parecido"
        recetas_id = [i.id for i in Receta.find_like_name(nombre)]
        # Guardo la busqueda para usarla en el template html
        session['busqueda'] = nombre
        # Guardo los ids de las recetas que coinciden con la busqueda
        session['recetas_id'] = recetas_id
        return redirect(url_for('ResultadoBusqueda'))

# Ver receta por ingrediente


@app.route('/recetasIngrediente/buscar', methods=['GET', 'POST'])
@login_required
def RecetasPorIngrediente():
    if 'ingredientes_id' in session:
        # Obtengo de la session los ingredientes agregados a la busqueda
        ingredientes_id = session.get('ingredientes_id')
        listadoIngredientes = [Ingrediente.find_by_id(
            id) for id in ingredientes_id]

        if listadoIngredientes:
            # Descripcion de ingredienetes a buscar
            descr_ingredienetes = [i.descripcion for i in listadoIngredientes]
            # Concateno los ingredientes buscados para mostrarlo en el HTML
            busqueda = ', '.join(descr_ingredienetes)
            session['busqueda'] = busqueda
            # Recetas que coinciden con ingredientes seleccionados
            recetas_id = ingredientes_en_receta(descr_ingredienetes)
            session['recetas_id'] = recetas_id
        session.pop('ingredientes_id', None)
        return redirect(url_for('ResultadoBusqueda'))
    else:
        return redirect(url_for('IngredienteBusqueda'))

# Ver receta por ingrediente


@app.route('/recetasIngrediente', methods=['GET', 'POST'])
@login_required
def IngredienteBusqueda():

    form = BuscarPorIngrediente()
    if 'ingredientes_id' in session:
        # Obtengo de la session los ingredientes agregados a la busqueda
        ingredientes_id = session.get('ingredientes_id')
        listadoIngredientes = [Ingrediente.find_by_id(
            id) for id in ingredientes_id]
        print(listadoIngredientes)
        if form.validate_on_submit():
            # Recupero del Form la descripcion ingresada
            nombre = form.nombreIngrediente.data

            if nombre not in [i.descripcion for i in listadoIngredientes]:
                ingrediente = Ingrediente.find_by_descripcion(nombre)
                listadoIngredientes.append(ingrediente)
                session['ingredientes_id'] = [
                    i.id for i in listadoIngredientes]
                return redirect(url_for('IngredienteBusqueda'))
            else:
                # Error ingrediente ya existe en la busqueda
                return redirect(url_for('IngredienteBusqueda'))
        return render_template('busquedaIngrediente.html',
                               form=form,
                               random=selectRandom(),
                               ingredientes=listadoIngredientes)
    else:
        if form.validate_on_submit():
            # Recupero del Form la descripcion ingresada
            nombre = form.nombreIngrediente.data
            ingrediente = Ingrediente.find_by_descripcion(nombre)

            session['ingredientes_id'] = [ingrediente.id]
            return redirect(url_for('IngredienteBusqueda'))
        return render_template('busquedaIngrediente.html',
                               form=form,
                               random=selectRandom())

# Descartar listado de ingredientes actual e ingresar uno nuevo


@app.route('/recetasIngrediente/descartarBusqueda', methods=['GET'])
@login_required
def NuevaBusquedaPorIngredientes():
    if 'ingredientes_id' in session:
        session.pop('ingredientes_id', None)
        return redirect(url_for('IngredienteBusqueda'))
    else:
        return redirect(url_for('IngredienteBusqueda'))

# Eliminar un ingrediente del listado actual a buscar


@app.route('/recetasIngrediente/eliminarIngrediente/<desc_ingrediente>', methods=['GET'])
@login_required
def EliminarIngredienteBusqueda(desc_ingrediente):
    if 'ingredientes_id' in session:
        # Obtengo de la session los ingredientes agregados a la busqueda
        ingredientes_id = session.get('ingredientes_id')
        listadoIngredientes = Ingrediente.find_by_list_id(ingredientes_id)

        if desc_ingrediente in [i.descripcion for i in listadoIngredientes]:
            ingrediente = Ingrediente.find_by_descripcion(desc_ingrediente)
            listadoIngredientes.remove(ingrediente)
            session['ingredientes_id'] = [i.id for i in listadoIngredientes]

        return redirect(url_for('IngredienteBusqueda'))
    else:
        return redirect(url_for('IngredienteBusqueda'))

# Muestra los resultados tanto de Busqueda por ingredientes como por recetas


@app.route('/resultadoBusqueda', methods=['GET', 'POST'])
@login_required
def ResultadoBusqueda():
    # Configuracion de paginado, toma la pagina.
    page = request.args.get('page', 1, type=int)
    recetas_id = session.get('recetas_id')
    recetas_obj = Receta.find_by_list_id(recetas_id)
    recetas = paginado(recetas_obj, page, ROWS_PER_PAGE)
    return render_template('resultadoBusqueda.html',
                           recetas=recetas)


@app.route('/Receta/Imagen/<nombre>')
def ImagenReceta(nombre):
    return send_from_directory(app.config["UPLOADED_IMGRECETAS_DEST"], nombre)


@app.route('/Ingrediente/Imagen/<nombre>')
def ImagenIngrediente(nombre):
    return send_from_directory(app.config["UPLOADED_IMGINGREDIENTES_DEST"], nombre)


@app.route('/verReceta/<idReceta>', methods=['GET', 'POST'])
@login_required
def VerReceta(idReceta):
    receta = Receta.find_by_id(idReceta)
    usuario = current_user.get_id()
    print(receta.favorita)
    if Favorito.find_by_receta_usuario(receta.id, usuario):
        favorito = True
    else:
        favorito = False
    return render_template('verReceta.html',
                           receta=receta,
                           favorito=favorito,
                           random=selectRandom())


@app.route('/misFavoritas', methods=['GET', 'POST'])
@login_required
def MisFavoritas():
    recetas = Favorito.find_favoritas_usuario(current_user.get_id())
    print(recetas)
    return render_template('indexFavoritos.html',
                           recetas=recetas,
                           random=selectRandom())


@app.route('/agregarFavorita/<idReceta>', methods=['GET', 'POST'])
@login_required
def AgregarFavorita(idReceta):
    receta = Receta.find_by_id(idReceta)
    usuario = current_user.get_id()

    favorito = Favorito.find_by_receta_usuario(receta.id, usuario)

    if favorito:
        return render_template('verReceta.html',
                               receta=receta,
                               favorito=True,
                               random=selectRandom())
    else:
        favorito = Favorito(id_receta=receta.id,
                            id_usuario=usuario)
        favorito.save_to_db()
        print("Se agrego a favoritos")
        # AGREGAR ALGUN POP UP MOSTRANDO OK AGREGADO A FAVORITOS O ALGO#
        return render_template('verReceta.html',
                               receta=receta,
                               favorito=True,
                               random=selectRandom())


@app.route('/eliminarFavorita/<idReceta>', methods=['GET', 'POST'])
@login_required
def EliminarFavorita(idReceta):
    receta = Receta.find_by_id(idReceta)
    usuario = current_user.get_id()

    favorito = Favorito.find_by_receta_usuario(receta.id, usuario)

    if favorito:
        Favorito.delete_from_db(favorito)
        print("Se elimino de favoritos")
        # AGREGAR ALGUN POP UP MOSTRANDO OK ELIMINADO DE FAVORITOS O ALGO#
        return render_template('verReceta.html',
                               receta=receta,
                               favorito=False,
                               random=selectRandom())
    else:
        return render_template('verReceta.html',
                               receta=receta,
                               favorito=False,
                               random=selectRandom())


@app.route('/_autocomplete', methods=['GET'])
@login_required
def autocomplete():
    IngredientesExistentes = [i.descripcion for i in Ingrediente.query.all()]
    return Response(json.dumps(IngredientesExistentes), mimetype='application/json')


##############################################################################
##                            INICIO APP ADMIN                              ##
##############################################################################

@app.route('/admin/inicio', methods=['GET', 'POST'])
@login_required
def PaginaInicioAdmin():
    return render_template('administrador/pagina_inicio_admin.html')


@app.route('/admin/recetas', methods=['GET', 'POST'])
@login_required
def Listado():
    recetas = Receta.query.all()
    if 'creando' in session:
        session.pop('creando', None)
    return render_template('administrador/listado_recetas.html',
                           recetas=recetas)

##############################################################################
##                              ABM RECETAS                                 ##
##############################################################################

# Para comenzar la creacion de la receta, primero se arma informacion basica


@app.route('/admin/receta/crear/informacionGeneral', methods=['GET', 'POST'])
@login_required
def InfoGeneral():

    receta = Form_InformacionGeneral()
    receta.dificultad.choices = [(dif.id, dif.descripcion)
                                 for dif in Dificultad.query.all()]

    if receta.validate_on_submit():

        if receta.imagenReceta:
            nombreImagen = "rec_" + \
                receta.tituloReceta.data.replace(' ', '').lower()
            imagen = receta.imagenReceta.data
            imagenReceta = guardar_imagen(imagen, nombreImagen, 'R')

            if imagenReceta:
                # si la imagen fue cargada con éxito
                nuevaReceta = Receta(
                    titulo=receta.tituloReceta.data,
                    fecha_creacion=datetime.now(),
                    fecha_modificacion=datetime.now(),
                    nombre_imagen=imagenReceta,
                    id_dificultad=receta.dificultad.data,
                    id_autor=current_user.id,
                    descripcion=receta.descripcion.data
                )
                # Guardamos en db
                Receta.save_to_db(nuevaReceta)

                session['creando'] = True

                return redirect(url_for('IngPorReceta', idReceta=nuevaReceta.id))

            else:
                return redirect(url_for('InfoGeneral'))

    return render_template('administrador/crear_info_gral.html',
                           form=receta)

# Agregar Ingrediente a la receta


@app.route('/admin/receta/<idReceta>/crear/ingredientes', methods=['GET', 'POST'])
@login_required
def IngPorReceta(idReceta):

    ingrediente = Form_Ingrediente()
    ingrediente.descripcionIngrediente.choices = [
        (i.id, i.descripcion) for i in Ingrediente.query.all()]
    ingrediente.unidad.choices = [(u.id, u.descripcion)
                                  for u in Unidad.query.all()]

    if ingrediente.validate_on_submit():

        idIngrediente = ingrediente.descripcionIngrediente.data
        cantidad = ingrediente.cantidad.data
        idUnidad = ingrediente.unidad.data

        if Ingrediente_Por_Receta.any_ingrediente_receta(idIngrediente, idReceta):
            # Flash ya existe ingrediente en la receta
            return redirect(url_for('IngPorReceta'))
        else:
            # Avanzamos con la creacion de un ingrediente en la receta
            ingredienteXreceta = Ingrediente_Por_Receta(
                id_receta=idReceta,
                id_ingrediente=idIngrediente,
                cantidad=cantidad,
                id_unidad=idUnidad
            )
            Ingrediente_Por_Receta.save_to_db(ingredienteXreceta)

        if 'creando' in session:
            return redirect(url_for('IngPorReceta', idReceta=idReceta))
        else:
            return redirect(url_for('EditarIngPorReceta', idReceta=idReceta))
    else:
        receta = Receta.find_by_id(idReceta)
        return render_template('administrador/crear_ing_por_receta.html',
                               form=ingrediente,
                               receta=receta)

# Editar ingrediente recientemente agregado a la receta


@app.route('/admin/receta/editar/ingrediente/<idIxr>', methods=['GET', 'POST'])
@login_required
def EditarIngDeReceta(idIxr):
    # Inicializacion
    ingrediente = Form_Editar_Ing_Por_Receta()
    ingrediente.descripcionIngrediente.choices = [
        (i.id, i.descripcion) for i in Ingrediente.query.all()]
    ingrediente.unidad.choices = [(u.id, u.descripcion)
                                  for u in Unidad.query.all()]

    # Encuentra el ingrediente que se quiere editar
    ingXreceta = Ingrediente_Por_Receta.find_by_id(idIxr)

    # Si se valida OK
    if ingrediente.validate_on_submit():

        ingXreceta.cantidad = ingrediente.cantidad.data
        ingXreceta.id_unidad = ingrediente.unidad.data

        db.session.commit()

        if 'creando' in session:
            return redirect(url_for('IngPorReceta', idReceta=ingXreceta.id_receta))
        else:
            return redirect(url_for('EditarIngPorReceta', idReceta=ingXreceta.id_receta))
    else:
        ingrediente.descripcionIngrediente.data = ingXreceta.ingredientes.descripcion
        ingrediente.cantidad.data = ingXreceta.cantidad
        ingrediente.unidad.data = ingXreceta.id_unidad

        # Receta del ingrediente a modificar
        receta = Receta.find_by_id(ingXreceta.id_receta)

        return render_template('administrador/editar_ing_de_receta.html',
                               form=ingrediente,
                               receta=receta,
                               ixr=ingXreceta)

# Eliminar Ingrediente por receta


@app.route('/admin/receta/ingrediente/eliminar/<idIxr>', methods=['GET', 'POST'])
@login_required
def EliminarIngPorReceta(idIxr):
    ingrediente = Ingrediente_Por_Receta.find_by_id(idIxr)
    Ingrediente_Por_Receta.delete_from_db(ingrediente)
    flash('El Ingrediente se ha eliminado correctamente de la receta.')
    return redirect(url_for('IngPorReceta'))

# Crear paso


@app.route('/admin/receta/<idReceta>/crear/preparacion', methods=['GET', 'POST'])
@login_required
def PrepPorReceta(idReceta):
    # Inicializacion
    preparacion = Form_Preparacion()

    # Si el POST se valida ok
    if preparacion.validate_on_submit():

        ordenPaso = preparacion.ordenPaso.data
        descripcionPaso = preparacion.descripcionPaso.data
        tiempoPaso = preparacion.tiempoPaso.data

        # Validar que el paso no exista en la receta
        if Preparacion.find_by_paso_receta(ordenPaso, idReceta):
            return redirect(url_for(PrepPorReceta))
        else:
            # Si el paso no existe en mi receta:
            nuevoPaso = Preparacion(
                id_receta=idReceta,
                orden_del_paso=ordenPaso,
                descripcion=descripcionPaso,
                tiempo_preparacion=tiempoPaso
            )
            Preparacion.save_to_db(nuevoPaso)

            if 'creando' in session:
                return redirect(url_for('PrepPorReceta', idReceta=idReceta))
            else:
                return redirect(url_for('EditarPrepPorReceta', idReceta=idReceta))

    else:
        receta = Receta.find_by_id(idReceta)
        return render_template('administrador/crear_preparacion.html',
                               form=preparacion,
                               receta=receta)

# Editar paso recientemente creado


@app.route('/admin/receta/editar/paso/<idPaso>', methods=['GET', 'POST'])
@login_required
def EditarPasoReceta(idPaso):
    # Inicializacion
    preparacion = Form_Preparacion()
    # Encontrar paso que se quiere editar
    paso = Preparacion.find_by_id(idPaso)
    idReceta = paso.id_receta

    # Si POST valida ok
    if preparacion.validate_on_submit():

        paso.descripcion = preparacion.descripcionPaso.data
        paso.tiempo_preparacion = preparacion.tiempoPaso.data

        db.session.commit()
        if 'creando' in session:
            return redirect(url_for('PrepPorReceta', idReceta=idReceta))
        else:
            return redirect(url_for('EditarPrepPorReceta', idReceta=idReceta))

    else:
        receta = Receta.find_by_id(idReceta)

        preparacion.ordenPaso.data = paso.orden_del_paso
        preparacion.descripcionPaso.data = paso.descripcion
        preparacion.tiempoPaso.data = paso.tiempo_preparacion

        return render_template('administrador/editar_paso_receta.html',
                               form=preparacion,
                               paso=paso,
                               receta=receta)

# Eliminar paso de receta


@app.route('/admin/receta/preparacion/eliminar/<idPaso>', methods=['GET', 'POST'])
@login_required
def EliminarPrepPorReceta(idPaso):
    paso = Preparacion.find_by_id(idPaso)
    Preparacion.delete_from_db(paso)
    flash('El paso se ha eliminado correctamente de la receta.')
    return redirect(url_for('PrepPorReceta'))

# Eliminar receta completa


@app.route('/admin/receta/<idReceta>/eliminar', methods=['GET'])
@login_required
def EliminarReceta(idReceta):
    receta = Receta.find_by_id(idReceta)

    if receta.preparacion:
        for paso in receta.preparacion:
            Preparacion.delete_from_db(paso)

    if receta.ingrediente:
        for ingrediente in receta.ingrediente:
            Ingrediente_Por_Receta.delete_from_db(ingrediente)

    Receta.delete_from_db(receta)
    return redirect(url_for('Listado'))

# Editar Receta


@app.route('/admin/receta/editar/<idReceta>', methods=['GET'])
@login_required
def EditarReceta(idReceta):
    receta = Receta.find_by_id(idReceta)
    return render_template('administrador/editar_receta.html', receta=receta)

# Editar imagen de la receta


@app.route('/admin/receta/editar/imagen/<idReceta>', methods=['GET', 'POST'])
@login_required
def EditarImagenReceta(idReceta):
    cambiarImagen = CambiarImagen()
    receta = Receta.find_by_id(idReceta)

    if cambiarImagen.validate_on_submit():
        # Elimino el archivo anterior
        os.remove(os.path.join(
            app.config["UPLOADED_IMGRECETAS_DEST"], receta.nombre_imagen))
        # Cargo el nuevo archivo
        imagen = cambiarImagen.imagenReceta.data
        # Obtengo el nombre de la imagen basado en el titulo de la receta
        nombreImagen = "rec_" + receta.titulo.replace(' ', '').lower()
        # Nueva imagen, puede variar la extension por eso vuelvo a guardarlo en la BD
        nombreImagen = guardar_imagen(imagen, nombreImagen, 'R')
        receta.nombre_imagen = nombreImagen
        db.session.commit()
        return redirect(url_for('EditarReceta', idReceta=idReceta))

    return render_template('administrador/editar_imagen_receta.html',
                           form=cambiarImagen,
                           receta=receta)

# Editar Informacion general


@app.route('/admin/receta/editar/informacionGeneral/<idReceta>', methods=['GET', 'POST'])
@login_required
def EditarInfoGeneral(idReceta):
    infoGeneral = Form_InformacionGeneral()
    receta = Receta.find_by_id(idReceta)
    infoGeneral.dificultad.choices = [
        (dif.id, dif.descripcion) for dif in Dificultad.query.all()]

    if infoGeneral.validate_on_submit():

        nombreImagen = "rec_" + \
            infoGeneral.tituloReceta.data.replace(' ', '').lower()

        if receta.titulo != infoGeneral.tituloReceta.data:

            # Tengo que renombrar el archivo primero
            nombreImagenNuevo = renombrar_imagen(
                receta.nombre_imagen, nombreImagen, 'R')
            receta.titulo = infoGeneral.tituloReceta.data,
            receta.nombre_imagen = nombreImagenNuevo,
            db.session.commit()

        receta.fecha_modificacion = datetime.now(),
        receta.id_dificultad = infoGeneral.dificultad.data,
        receta.descripcion = infoGeneral.descripcion.data

        db.session.commit()

        return redirect(url_for('EditarReceta', idReceta=idReceta))
    else:
        infoGeneral.tituloReceta.data = receta.titulo
        infoGeneral.dificultad.data = receta.id_dificultad
        infoGeneral.descripcion.data = receta.descripcion
        return render_template('administrador/editar_info_gral.html',
                               form=infoGeneral,
                               receta=receta)

# Editar Ing por receta


@app.route('/admin/receta/editar/ingredientes/<idReceta>', methods=['GET', 'POST'])
@login_required
def EditarIngPorReceta(idReceta):
    receta = Receta.find_by_id(idReceta)
    ingredientesXreceta = Ingrediente_Por_Receta.find_by_receta(idReceta)
    return render_template('administrador/editar_listado_ing_receta.html',
                           receta=receta,
                           ingredientesXreceta=ingredientesXreceta)

# Editar preparacion por receta


@app.route('/admin/receta/editar/preparacion/<idReceta>', methods=['GET', 'POST'])
@login_required
def EditarPrepPorReceta(idReceta):
    receta = Receta.find_by_id(idReceta)
    preparacion = Preparacion.find_by_receta(idReceta)
    return render_template('administrador/editar_preparacion_receta.html',
                           receta=receta,
                           preparacion=preparacion)


@app.route('/admin/receta/<idReceta>/ver', methods=['GET', 'POST'])
@login_required
def VerRecetaAdmin(idReceta):
    receta = Receta.find_by_id(idReceta)
    return render_template('administrador/ver_receta.html',
                           receta=receta)


##############################################################################
##                             ABM INGREDIENTES                             ##
##############################################################################

@app.route('/admin/ingredientes/ABM', methods=['GET', 'POST'])
@login_required
def ListadoIngredientes():
    form = CrearIngrediente()

    if form.validate_on_submit():

        descripcion = form.descripcionIngrediente.data
        imagen = form.imagenIngrediente.data

        if imagen:
            nombreImagen = "ing_" + descripcion.replace(' ', '').lower()
            imagenIngrediente = guardar_imagen(imagen, nombreImagen, 'I')

            if imagenIngrediente:
                # si la imagen fue cargada con éxito
                nuevoIngrediente = Ingrediente(
                    descripcion=descripcion,
                    fecha_creacion=datetime.now(),
                    fecha_modificacion=datetime.now(),
                    nombre_imagen=imagenIngrediente,
                )
                # Guardamos en db
                Ingrediente.save_to_db(nuevoIngrediente)

                return redirect(url_for('ListadoIngredientes'))

            else:
                # No se guardo ok la imagen
                return redirect(url_for('ListadoIngredientes'))
        else:
            # No se cargo imagen
            return redirect(url_for('ListadoIngredientes'))
    else:
        ingredientes = Ingrediente.query.all()
        return render_template('administrador/listado_ingredientes.html',
                               ingredientes=ingredientes,
                               form=form)

@app.route('/admin/ingrediente/eliminar/<idIng>', methods=['GET', 'POST'])
@login_required
def EliminarIngrediente(idIng):
    ingrediente = Ingrediente.find_by_id(idIng)
    if ingrediente.por_receta:
        for ixr in ingrediente.por_receta:
            Ingrediente_Por_Receta.delete_from_db(ixr)  
    Ingrediente.delete_from_db(ingrediente)
    flash('El ingrediente se ha eliminado correctamente.')
    return redirect(url_for('ListadoIngredientes'))
    
@app.route('/admin/ingrediente/ver/<idIng>', methods=['GET', 'POST'])
@login_required
def VerIngrediente(idIng):
        ingrediente = Ingrediente.find_by_id(idIng)
        return render_template('administrador/ver_ingrediente.html',
                               ingrediente=ingrediente)

##############################################################################
##                               ABM UNIDADES                               ##
##############################################################################


@app.route('/admin/unidades', methods=['GET', 'POST'])
@login_required
def ListadoUnidades():
    form = CrearUnidad()

    if form.validate_on_submit():

        descripcion = form.descripcionUnidad.data

        nuevaUnidad = Unidad(descripcion=descripcion)
        # Guardamos en db
        Unidad.save_to_db(nuevaUnidad)

        return redirect(url_for('ListadoUnidades'))

    else:
        unidades = Unidad.query.all()
        return render_template('administrador/listado_unidades.html',
                               unidades=unidades,
                               form=form)


@app.route('/admin/unidad/eliminar/<idUni>', methods=['GET', 'POST'])
@login_required
def EliminarUnidad(idUni):

    unidad = Unidad.find_by_id(idUni)

    if unidad.ingredientes:
        return redirect(url_for('ListadoUnidades'))
    else:
        Unidad.delete_from_db(unidad)
        # flash('Unidad eliminada correctamente de la receta!')
        return redirect(url_for('ListadoUnidades'))

##############################################################################
##                               ABM DIFICULTAD                             ##
##############################################################################


@app.route('/admin/dificultad', methods=['GET', 'POST'])
@login_required
def ListadoNivelDificultad():
    form = CrearDificultad()

    if form.validate_on_submit():

        descripcion = form.descripcionDificultad.data

        nuevaDificultad = Dificultad(descripcion=descripcion)
        # Guardamos en db
        Dificultad.save_to_db(nuevaDificultad)

        return redirect(url_for('ListadoNivelDificultad'))

    else:
        dificultad = Dificultad.query.all()
        return render_template('administrador/listado_nivel_dificultad.html',
                               dificultades=dificultad,
                               form=form)


@app.route('/admin/dificultad/eliminar/<idDif>', methods=['GET', 'POST'])
@login_required
def EliminarDificultad(idDif):
    dificultad = Dificultad.find_by_id(idDif)
    if dificultad.recetas:
        # Esta asociado a una receta, no lo puedo eliminar
        return redirect(url_for('ListadoNivelDificultad'))
    else:
        Dificultad.delete_from_db(dificultad)
        # flash('Nivel de dificultad eliminado correctamente de la receta!')
        return redirect(url_for('ListadoNivelDificultad'))



##############################################################################
##                               ABM ADMINISTRADORES                        ##
##############################################################################


@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def ListadoAdmin():
    form = CrearAdmin()
    form.usuario.choices = [(i.id, i.email) for i in Usuario.find_users()]
    users = [(i.id, i.email,i.administrador) for i in Usuario.find_users()]
    print(users)

    if form.validate_on_submit():

        nombreUsuario = form.usuario.data

        usuario = Usuario.find_by_id(nombreUsuario)

        usuario.administrador = True
        db.session.commit()

        return redirect(url_for('ListadoAdmin'))

    else:
        administradores = Usuario.find_admin()
        return render_template('administrador/listado_administradores.html',
                               administradores=administradores,
                               form=form)


@app.route('/admin/usuarios/<idAdmin>/eliminar', methods=['GET', 'POST'])
@login_required
def EliminarAdmin(idAdmin):
    usuario = Usuario.find_by_id(idAdmin)
    usuario.administrador = False
    db.session.commit()

    return redirect(url_for('ListadoAdmin'))


if __name__ == '__main__':
    app.run(debug=True)
