from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2, psycopg2.extras
from psycopg2 import sql, extensions

app = Flask(__name__)

# Connect to PostgreSQL
connection = psycopg2.connect(
    user = "postgres",
    password = "1998",
    host = "localhost",
    port = "5432",
    database = "recetas_db"
)

app.secret_key = 'mysecretkey'

@app.route('/')
def Login():
        return render_template('login.html')

@app.route('/crear')
def Crear_receta():
        return render_template('crear_receta.html')

@app.route('/ingresar', methods = ['POST','GET'])
def Ingresar():
    if request.method == 'POST':
        contras = request.form['pass']
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM password WHERE password = %(passw)s', {"passw": contras})
        data = cursor.fetchall()
        if (len(data) == 0):
            return render_template('login.html')
        else:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM receta')
            data = cursor.fetchall()
            return render_template('index.html', recetas = data)

@app.route('/inicio')
def Index():
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM receta')
            data = cursor.fetchall()
            return render_template('index.html', recetas = data)


@app.route('/agregar', methods = ['POST'])
def agregar_receta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ingredientes = request.form['ingrediente']
        preparacion = request.form['preparacion']
       
        cursor = connection.cursor()
        #Sentencia SQL
        pg_insert = 'INSERT INTO receta (nombre, ingrediente, preparacion) VALUES (%(nombre)s, %(ingredientes)s, %(preparacion)s)'
        #Datos capturados en el formulario HTML a ingresar en la base de datos
        inserted_values = {"nombre":nombre, "ingredientes":ingredientes, "preparacion":preparacion}
        #Ingreso en la base y guardo
        cursor.execute(pg_insert, inserted_values)
        connection.commit()

    flash('Receta agregada exitosamente!')
    return redirect(url_for('Index'))

@app.route('/editar/<nombre>')
def obtener_receta(nombre):
    cursor = connection.cursor()
    sentenciaSQL = 'SELECT * FROM receta WHERE nombre = (%(nombre)s)'
    recetaObtener = {"nombre":nombre}
    cursor.execute(sentenciaSQL, recetaObtener)
    data = cursor.fetchall()
    return render_template('editar_receta.html', receta = data[0])

@app.route('/actualizar/<nombre>', methods = ['POST'])
def actualizar_receta(nombre):
    if request.method == 'POST':
        nombre = request.form['nombre']
        ingredientes = request.form['ingrediente']
        preparacion = request.form['preparacion']

    cursor = connection.cursor()
    sentenciaSQL = 'UPDATE receta SET ingrediente = (%(ingredientes)s), preparacion = (%(preparacion)s) WHERE nombre = (%(nombre)s)'
    recetaActualizar = {"ingredientes":ingredientes, "preparacion":preparacion, "nombre":nombre}
    cursor.execute(sentenciaSQL, recetaActualizar)
    connection.commit()
    flash('Receta actualizada') 
    return redirect(url_for('Index'))

@app.route('/eliminar/<string:nombre>')
def eliminar_receta(nombre):
    cursor = connection.cursor()
    sentenciaSQL = 'DELETE FROM receta WHERE nombre = %(nombre)s'
    recetaEliminar = {"nombre":nombre}
    cursor.execute(sentenciaSQL, recetaEliminar)
    connection.commit()
    flash('Receta eliminada correctamente')
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(debug = True)
