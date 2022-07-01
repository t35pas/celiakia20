from datetime import datetime, timedelta
import imp
import os

basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash, send_from_directory, session
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy


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
from forms import LoginForm, NuevaReceta, NuevaPreparacion, NuevoIngrediente, EditarIngrediente, EditarPreparacion, EditarInfoGral



#Aplicacion WEB
def agregarEnReceta(form, idReceta):
        
        ingredienteXreceta = Ingrediente_Por_Receta(
                id_receta = idReceta, 
                id_ingrediente = form.elegirNombreIngrediente.data,
                cantidad = form.cantidad.data
        )
        db.session.add(ingredienteXreceta)
        db.session.commit()
        return ingredienteXreceta
def crearIngrediente(form, idReceta):
        nombreIngrediente = form.nombreIngrediente.data
        cantidad = form.cantidad.data
        unidad = form.unidad.data
        nombreImagen = form.nombreImagen.data
        f = form.imagenIngrediente.data
                        
        filename = secure_filename(nombreImagen)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ingrediente = Ingrediente(
                descripcion = nombreIngrediente,
                id_unidad = unidad,
                fecha_creacion = datetime.now(),
                fecha_modificacion = datetime.now(),
                nombre_imagen = nombreImagen
        )
        db.session.add(ingrediente)
        db.session.commit()
        ingredienteXreceta = Ingrediente_Por_Receta(
                id_receta = idReceta, 
                id_ingrediente = ingrediente.id,
                cantidad = cantidad
        )
        db.session.add(ingredienteXreceta)
        db.session.commit()
        return ingredienteXreceta
def existePaso(form, idReceta):
        paso = Preparacion.query.filter_by(
                        id_receta = idReceta,
                        orden_del_paso = form.ordenPaso.data
        ).first()
        
        return paso
def crearPaso(form, idReceta):
        paso = Preparacion(
                id_receta = idReceta,
                orden_del_paso = form.ordenPaso.data,
                descripcion = form.descripcion.data
        )
        db.session.add(paso)
        db.session.commit()
        return paso
def eliminarReceta(idReceta):
        receta = Receta.query.get(idReceta)
        db.session.delete(receta)
        db.session.commit()
        return True
def eliminarIngrPorReceta(idIxR):
        ingrediente = Ingrediente_Por_Receta.query.get(idIxR)
        db.session.delete(ingrediente)
        db.session.commit()
        return True
def eliminarIngrediente(idIngrediente):
        ingrediente = Ingrediente.query.get(idIngrediente)
        db.session.delete(ingrediente)
        db.session.commit()
        return True
def editarIngPorReceta(ingredienteXreceta, ingrediente, form):
        
        existeIngrediente = Ingrediente.query.filter_by(
                                descripcion = form.nombreIngrediente.data,
                                id_unidad = form.unidad.data
                        ).first()
        if existeIngrediente:
                ingredienteXreceta.id_ingrediente = existeIngrediente.id
                ingredienteXreceta.cantidad = form.cantidad.data
                print(form.imagenIngrediente.data)
                ingrediente.nombre_imagen = form.nombreImagen.data
                f = form.imagenIngrediente.data
                if f:
                        filename = secure_filename(form.nombreImagen.data)
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.session.commit()
                return True
        else:
                ingredienteXreceta.cantidad = form.cantidad.data
                ingrediente.descripcion = form.nombreIngrediente.data
                ingrediente.id_unidad = form.unidad.data
                ingrediente.nombre_imagen = form.nombreImagen.data
                f = form.imagenIngrediente.data
                if f:
                        filename = secure_filename(form.nombreImagen.data)
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))        
                db.session.commit()
                return True
        return False   
        
@app.route('/', methods = ['GET', 'POST'])
@app.route('/login', methods = ['GET', 'POST'])
def Login():
        if current_user.is_authenticated:
                return redirect(url_for('Home'))
        form = LoginForm()
        if form.validate_on_submit():
                admin = Administrador.query.filter_by(nombre_usuario = form.nombreUsuario.data).first()
                if admin and bcrypt.check_password_hash(admin.contrasenia, form.contrasenia.data):
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
@app.route('/nuevaReceta', methods = ['GET', 'POST'])
@login_required
def InfoGeneral():
        form = NuevaReceta()
        form.dificultad.choices = [(dif.id, dif.descripcion) for dif in Dificultad.query.all()]
        if form.validate_on_submit():
                
                nombreImagen = form.nombreImagen.data
                f = form.imagenReceta.data
                filename = secure_filename(nombreImagen)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                nuevaReceta = Receta(
                                titulo = form.tituloReceta.data, 
                                fecha_creacion = datetime.now(),
                                fecha_modificacion = datetime.now(),
                                calificacion = 5,
                                tiempo_preparacion = form.tiempoPreparacion.data,
                                nombre_imagen = nombreImagen,
                                id_dificultad = form.dificultad.data,
                                id_administrador = current_user.id 
                        )
                db.session.add(nuevaReceta)
                db.session.commit()
                
                if 'idReceta' in session:
                        print('Elimino la vieja')
                        print(session['idReceta'])
                        session.pop('idReceta', None)
                        print('Creo la nueva')
                        session['idReceta'] = nuevaReceta.id
                else:
                        session['idReceta'] = nuevaReceta.id
                flash('Genial! La informacion general se guardo en la base de datos, sigue asi!')
                return redirect(url_for('IngPorReceta'))
        return render_template('nr_infoGeneral.html', form = form, user = current_user)
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
@app.route('/ingredientes', methods = ['GET', 'POST'])
@login_required
def IngPorReceta():
        idReceta = session.get('idReceta')
        print(idReceta)
        if idReceta:
                form = NuevoIngrediente()
                form.elegirNombreIngrediente.choices = [(i.id, i.descripcion) for i in Ingrediente.query.all()]
                form.unidad.choices = [(u.id, u.descripcion) for u in Unidad.query.all()]
                if form.validate_on_submit():
                        print(form.nombreImagen.data)
                        if form.nombreImagen.data:
                                creado = crearIngrediente(form, idReceta)
                                print(creado.id)
                                return redirect(url_for('IngPorReceta'))
                        else:
                                agregarEnReceta(form, idReceta)
                                print('Agregado a receta')
                                return redirect(url_for('IngPorReceta'))
                
                ingredientesXreceta = Ingrediente_Por_Receta.query.filter_by(id_receta = idReceta)
                ingredientes = Ingrediente.query.all()
                return render_template('nr_ingredientes.html', 
                                        form = form, 
                                        user = current_user, 
                                        ingredientesXreceta = ingredientesXreceta, 
                                        ingredientes = ingredientes
                                        )
        else:
                print('no esta en session')
                return redirect(url_for('Home'))
@app.route('/ingredientes/editar/<idIxR>', methods = ['GET', 'POST'])
@login_required
def EditarIngPorReceta(idIxR):
        idReceta = session.get('idReceta')
        if idReceta:
                ingredienteXreceta = Ingrediente_Por_Receta.query.get(idIxR)
                ingrediente = Ingrediente.query.get(ingredienteXreceta.id_ingrediente)
                
                form = EditarIngrediente()
                
                if form.validate_on_submit():
                
                        editar = editarIngPorReceta(ingredienteXreceta, ingrediente, form)
                        if editar == True:
                                flash('actualizado ok')
                        else:
                                flash('actualizado no ok')
                        return redirect(url_for('IngPorReceta'))
                
                elif request.method == 'GET':
        
                        form.nombreIngrediente.data = ingrediente.descripcion
                        form.unidad.data = ingrediente.unidad.descripcion
                        form.cantidad.data = ingredienteXreceta.cantidad
                        form.nombreImagen.data = ingrediente.nombre_imagen
                ingredientes = ingredientesXreceta = Ingrediente_Por_Receta.query.filter_by(id_receta = idReceta)
                return render_template('editar_ingredientes.html', 
                                        formE = form, 
                                        user = current_user, 
                                        idIxR = idIxR,
                                        nombreIngrediente = ingrediente.descripcion,
                                        ingredientes = ingredientes
                                )
        else:
                print('no esta en session')
                return redirect(url_for('Home'))
@app.route('/ingredientes/eliminar/<idIxR>', methods = ['GET', 'POST'])
@login_required
def eliminarIngPorReceta(idIxR):
        idReceta = session.get('idReceta')
        if idReceta:
                eliminarIngrPorReceta(idIxR)
                flash('Ingrediente eliminado correctamente de la receta!')
                return redirect(url_for('IngPorReceta'))
        return redirect(url_for('Home'))
        
@app.route('/preparacion', methods = ['GET', 'POST'])
@login_required
def PrepPorReceta():
        idReceta = session.get('idReceta')
        print("estoy en preparacion")
        
        if idReceta:
                
                form = NuevaPreparacion()
                preparacion = Preparacion.query.filter_by(id_receta = idReceta)
                
                if form.validate_on_submit() and not existePaso(form, idReceta):
                        
                        paso = crearPaso(form, idReceta)
                        print('Paso creado')
                        print(paso.orden_del_paso)
                        return redirect(url_for('PrepPorReceta'))
                return render_template('nr_preparacion.html', form = form, preparacion = preparacion, user = current_user)
        else: 
                return redirect(url_for('Home'))
@app.route('/preparacion/editar/<idPrep>', methods = ['GET', 'POST'])
@login_required
def EditarPrepPorReceta(idPrep):
        idReceta = session.get('idReceta')
        
        if idReceta:
                
                form = EditarPreparacion()
                paso = Preparacion.query.filter_by(id_receta = idReceta, 
                                                   id = idPrep).first()
                print(paso.descripcion)
                
                if form.validate_on_submit():
                        print('Se valido el formulario')
                        paso.orden_del_paso = form.ordenPaso.data
                        paso.descripcion = form.descripcion.data
                        db.session.commit()
                        print('Paso Actualizado')
                        flash('Paso actualizado ok')
                        
                        return redirect(url_for('PrepPorReceta'))
                
                elif request.method == 'GET':
                        print('Es un GET')
                        form.ordenPaso.data = paso.orden_del_paso
                        form.descripcion.data = paso.descripcion
                preparacion = Preparacion.query.filter_by(id_receta = idReceta)
                
                return render_template('editar_preparacion.html', 
                                        form = form, 
                                        preparacion = preparacion, 
                                        idPrep = idPrep,
                                        user = current_user)
        else: 
                return redirect(url_for('PrepPorReceta'))
@app.route('/preparacion/eliminar/<idPrep>', methods = ['GET', 'POST'])
@login_required
def EliminarPrepPorReceta(idPrep):
        idReceta = session.get('idReceta')
        
        if idReceta:
                paso = Preparacion.query.get(idPrep)
                db.session.delete(paso)
                db.session.commit()
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
        receta = Receta.query.get(idReceta)
        ingrXreceta = Ingrediente_Por_Receta.query.filter_by(id_receta = idReceta)
        preparacion = Preparacion.query.filter_by(id_receta = idReceta)
    
        if preparacion: 
                for paso in preparacion:
                        db.session.delete(paso)
                        db.session.commit()
        
        if ingrXreceta:
                for ingrediente in ingrXreceta:   
                        db.session.delete(ingrediente)
                        db.session.commit()
    
        db.session.delete(receta)
        db.session.commit()
        flash('Eliminaste la receta con exito.')
        return redirect(url_for('Listado'))

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def Logout():
        logout_user()
        return redirect(url_for('Login'))

#Aplicación CeliaKIA Web
@app.route('/index', methods = ['GET', 'POST'])
def paginaInicio(name=None):
    return render_template('index.html', name=name)

@app.route('/indexMundoCeliakia', methods = ['GET', 'POST'])
def paginaMundoCeliakia(name=None):
    return render_template('indexMundoCeliakia.html', name=name)

#Buscar Por Nombre de Receta
@app.route('/buscarPorNombre/<nombre>', methods = ['GET', 'POST'])
def BuscarPorNombre(nombre):
        receta = Receta.query.find_by_name(nombre)
        ingredientes = receta.ingredientes
        preparacion = receta.preparacion
        
        return render_template('ver_receta.html', 
                                receta = receta,
                                ingredientes = ingredientes,
                                preparacion = preparacion)

if __name__ == '__main__':
     app.run(debug=True)
