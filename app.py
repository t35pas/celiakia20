import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './imagenes'
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
        recetasPorNombre = Receta.query.filter(Receta.titulo.like(nombre)).all()
        return  jsonify([receta.serialize() for receta in recetasPorNombre])

@app.route('/obtener_imagen/<nombre>')
class Obtener_imagen(Resource):
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
            recetas = Receta.query.join(Dificultad, Receta.id_dificultad == Dificultad.id)\
                                    .add_columns(Receta.id, Receta.titulo, Receta.calificacion, Receta.tiempo_preparacion, Receta.nombre_imagen, Dificultad.descripcion)\
                                    .all()
            return render_template('index.html', recetas = recetas)
        else:
            flash("Usuario o contraseña incorrecta, intente nuevamente.")
            return redirect(url_for('Login'))
    else:
        recetas = Receta.query.join(Dificultad, Receta.id_dificultad == Dificultad.id)\
                                 .add_columns(Receta.id, Receta.titulo, Receta.calificacion, Receta.tiempo_preparacion, Receta.nombre_imagen, Dificultad.descripcion)\
                                 .all()
        return render_template('index.html', recetas = recetas)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/receta/nueva', methods = ['POST','GET'])
def Crear_receta():
    unidades = Unidad.query.all()
    if request.method == 'POST':
        nombre = request.form['titulo']
        calificacion = request.form['calificacion']
        tiempo_preparacion = request.form['tiempo_preparacion']
        dificultad = request.form['dificultad']
        nombre_imagen = request.form['nombre_imagen']
        
        if 'archivo' not in request.files:
            flash('No se encontro archivo')
            return redirect(request.url)
        file = request.files['archivo']
        if file.filename == '':
            flash('No Seleccionaste el archivo')
        if file and allowed_file(file.filename):
            filename = nombre_imagen
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        id_dificultad = Dificultad.query.filter_by(descripcion = dificultad).first()

        nueva_receta = Receta(nombre, calificacion, tiempo_preparacion, id_dificultad.id, nombre_imagen)
        
        db.session.add(nueva_receta)
        db.session.commit()
        
        receta = Receta.query.get(nueva_receta.id)
        flash('Genial! La informacion general se guardo en la base de datos, sigue asi!')
        return render_template('ingredientes.html', nueva_receta = receta, unidades = unidades)
    else:
        return render_template('crear_receta.html')

@app.route('/receta/preparacion/<id>', methods = ['POST','GET'])
def Preparacion_nueva(id):
   
    receta = Receta.query.get(id)

    if request.method == 'POST':
        orden = request.form['orden']
        descripcion = request.form['descripcion']

        existe = Preparacion.query.filter_by(orden_del_paso = orden).first()
        
        if existe: 
        
            print('Ya existe ese paso')
            
            preparaciones = Preparacion.query.filter_by(id_receta = id).all()
            flash('Ese paso ya existe')
            return render_template('preparacion.html', nueva_receta = receta, preparaciones = preparaciones)

        else:
        
            preparacion = Preparacion(id, orden, descripcion)
            
            db.session.add(preparacion)
            db.session.commit()

            preparaciones = Preparacion.query.filter_by(id_receta = id).all()
            flash('Paso guardado!')
            return render_template('preparacion.html', nueva_receta = receta, preparaciones = preparaciones)
    else:

        preparaciones = Preparacion.query.filter_by(id_receta = id).all()

        return render_template('preparacion.html', nueva_receta = receta, preparaciones = preparaciones)

@app.route('/receta/ingredientes/<id>', methods = ['POST', 'GET'])
def Ingredientes(id):

    unidades = Unidad.query.all()

    if request.method == 'POST':
        nombre_ing = request.form['nombre_ingrediente']
        unidad_ing = request.form['unidad']
        cantidad_ing = request.form['cantidad']
        
        receta = Receta.query.get(id)
        
        unidad = Unidad.query.filter_by(descripcion_u = unidad_ing).first()

        existe_ingrediente = Ingrediente.query.filter_by(descripcion = nombre_ing, id_unidad = unidad.id).first()

        if existe_ingrediente:
            print('Existe el ingrediente')
            
            existe_ingrediente_receta = Ingrediente_Por_Receta.query.filter_by(id_ingrediente = existe_ingrediente.id, id_receta = id).first()

            if existe_ingrediente_receta:

                print('Ya existe ese ingrediente en la receta!')
                flash('Ya existe ese ingrediente en la receta!')
                ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                                    .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                                    .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                                    .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                                    .add_columns(Unidad.descripcion_u)\
                                    .all()

                return render_template('ingredientes.html', ingredientes = ingredientes_por_receta, nueva_receta = receta, unidades = unidades)
                
            else:

                nuevo_ingrediente_en_receta = Ingrediente_Por_Receta(id, existe_ingrediente.id, cantidad_ing)
                db.session.add(nuevo_ingrediente_en_receta)
                db.session.commit()
                
                ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                                    .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                                    .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                                    .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                                    .add_columns(Unidad.descripcion_u)\
                                    .all()
                flash('Ingrediente agregado en la receta!')
                return render_template('ingredientes.html', ingredientes = ingredientes_por_receta, nueva_receta = receta, unidades = unidades)       

        else:

            print('No existe el ingrediente')
            
            nuevo_ingrediente = Ingrediente(nombre_ing, unidad.id)
            db.session.add(nuevo_ingrediente)
            db.session.commit()
            
            print(nuevo_ingrediente)

            nuevo_ingrediente_en_receta = Ingrediente_Por_Receta(id, nuevo_ingrediente.id, cantidad_ing)
            db.session.add(nuevo_ingrediente_en_receta)
            db.session.commit()

            print(nuevo_ingrediente_en_receta)
            ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                                .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                                .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                                .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                                .add_columns(Unidad.descripcion_u)\
                                .all()
            flash('Ingrediente guardado en la receta!')
            return render_template('ingredientes.html', ingredientes = ingredientes_por_receta, nueva_receta = receta, unidades = unidades)

    else: 
        receta = Receta.query.get(id)

        ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                                .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                                .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                                .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                                .add_columns(Unidad.descripcion_u)\
                                .all()
           
        print(ingredientes_por_receta)
        return render_template('ingredientes.html', ingredientes = ingredientes_por_receta, nueva_receta = receta, unidades = unidades)

@app.route('/receta/eliminar/<id>')
def Eliminar_receta(id):
    receta = Receta.query.get(id)
    ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id).first()
    preparaciones = Preparacion.query.filter_by(id_receta = id).first()
    
    if preparaciones: 
        for preparacion in preparaciones:
            db.session.delete(preparacion)
            db.session.commit()
    
    if ingredientes_por_receta:
        for ingrediente in ingredientes_por_receta:   
            db.session.delete(ingrediente)
            db.session.commit()
    
    db.session.delete(receta)
    db.session.commit()
    flash('Eliminaste la receta con exito.')
    return redirect(url_for('Index'))

@app.route('/administrador',  methods = ['POST', 'GET'])
def Admin():
        if request.method == 'POST':
            nombre_a = request.form['nombre_a']
            vieja_pass = request.form['password_vieja']
            nueva_pass = request.form['password_nueva']

            admin = Administrador.query.filter_by(nombre = nombre_a).first()

            if (vieja_pass == admin.password):
                admin.password = nueva_pass
                db.session.commit()
                flash('Cambiaste la contraseña con exito!')
            else: 
                return redirect(url_for('Admin'))
        else:
            administradores = Administrador.query.all()
            return render_template('administrador.html', administradores = administradores)

@app.route('/receta/<id_receta>/ingrediente/eliminar/<id_ingr>')
def Eliminar_ingrediente(id_receta, id_ingr):
    
    receta = Receta.query.get(id_receta)
    ingrediente = Ingrediente_Por_Receta.query.filter_by(id_receta = id_receta, id_ingrediente = id_ingr).first()
    db.session.delete(ingrediente)    
    db.session.commit()
    ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id_receta)\
                                .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                                .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                                .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                                .add_columns(Unidad.descripcion_u)\
                                .all()
    flash('Eliminaste el ingrediente de la receta.')
    return render_template('ingredientes.html', nueva_receta = receta, ingredientes = ingredientes_por_receta)

@app.route('/receta/<id_receta>/preparacion/eliminar/<id_prep>')
def Eliminar_paso(id_receta, id_prep):

    receta = Receta.query.get(id_receta)
    preparacion = Preparacion.query.get(id_prep)
    preparaciones = Preparacion.query.filter_by(id_receta = id_receta)
    db.session.delete(preparacion)
    db.session.commit()
    flash('Eliminaste el paso de la receta.')
    return render_template('preparacion.html', nueva_receta = receta, preparaciones = preparaciones)

@app.route('/actualizar/<id>', methods = ['POST','GET'])
def Actualizar_receta(id):
    
    receta = Receta.query.get(id)
    dificultad = Dificultad.query.get(receta.id_dificultad)
    preparaciones = Preparacion.query.filter_by(id_receta = id).all()
    ingredientes = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                        .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                        .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                        .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                        .add_columns(Unidad.descripcion_u)\
                        .all()
    
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
        flash('Informacion actualizada exitosamente!')
        return render_template('editar_receta.html', receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)

    else:

        return render_template('editar_receta.html', receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)

@app.route('/receta/actualizar/preparacion/<id>', methods = ['POST', 'GET'])
def Actualizar_preparacion(id):

    receta = Receta.query.get(id)
    dificultad = Dificultad.query.get(receta.id_dificultad)
    preparaciones = Preparacion.query.filter_by(id_receta = id).all()
    ingredientes = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                        .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                        .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                        .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                        .add_columns(Unidad.descripcion_u)\
                        .all()
   
    if request.method == 'POST':

        for preparacion in preparaciones:
            
            name = 'orden' + str(preparacion.id)
            description = 'descripcion' + str(preparacion.id)
            
            orden = request.form[name]
            descripcion = request.form[description]

            preparacion.orden_del_paso = orden
            preparacion.descripcion = descripcion
       
            db.session.commit()
        flash('Informacion actualizada exitosamente!')            
        return render_template('editar_receta.html', receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)
    else:
       
        return render_template('editar_receta.html', receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)

@app.route('/receta/actualizar/ingredientes/<id>', methods = ['POST', 'GET'])
def Actualizar_ingrediente(id):

    receta = Receta.query.get(id)
    dificultad = Dificultad.query.get(receta.id_dificultad)
    ingredientes_por_receta = Ingrediente_Por_Receta.query.filter_by(id_receta = id).all()
    preparaciones = Preparacion.query.filter_by(id_receta = id).all()
    if request.method == 'POST':

        for ingrediente_por_receta in ingredientes_por_receta:
            
            name = 'cantidad' + str(ingrediente_por_receta.id_ingrediente)
            cantidad_ing = request.form[name]

            ingrediente_por_receta.cantidad = cantidad_ing
            db.session.commit()

        ingredientes = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                        .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                        .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                        .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                        .add_columns(Unidad.descripcion_u)\
                        .all()
        flash('Informacion actualizada exitosamente!')
        return render_template('editar_receta.html', receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)
        
    else:
        ingredientes = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                        .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                        .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                        .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                        .add_columns(Unidad.descripcion_u)\
                        .all()
       
        return render_template('editar_receta.html', receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)

@app.route('/receta/ver/<id>', methods = ['POST', 'GET'])
def Ver_receta(id):

    receta = Receta.query.get(id)
    dificultad = Dificultad.query.get(receta.id_dificultad)
    preparaciones = Preparacion.query.filter_by(id_receta = id).all()
    
    ingredientes = Ingrediente_Por_Receta.query.filter_by(id_receta = id)\
                        .join(Ingrediente, Ingrediente_Por_Receta.id_ingrediente == Ingrediente.id)\
                        .add_columns(Ingrediente_Por_Receta.id_receta, Ingrediente_Por_Receta.cantidad, Ingrediente.id, Ingrediente.descripcion, Ingrediente.id_unidad)\
                        .join(Unidad, Ingrediente.id_unidad == Unidad.id)\
                        .add_columns(Unidad.descripcion_u)\
                        .all()
       
    return render_template('ver_receta.html', nueva_receta = receta, dificultad = dificultad, ingredientes = ingredientes, preparaciones = preparaciones)

if __name__ == '__main__':
     app.run(debug=True)