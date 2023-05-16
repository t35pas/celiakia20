from typing import Text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, RadioField
from wtforms.fields.core import BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from models import Dificultad,Favorito,Ingrediente,Ingrediente_Por_Receta,Preparacion,Receta,Unidad,Usuario

class LoginForm(FlaskForm):
    nombreUsuario = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=100)])
    contrasenia = PasswordField('Contrasenia',validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class Form_InformacionGeneral(FlaskForm):
    tituloReceta = StringField('Titulo de la receta', validators=[DataRequired(), Length(min=2, max=50)])
    dificultad = SelectField('Dificultad',choices=[], coerce=int)
    imagenReceta = FileField('Imagen de la receta',validators=[FileAllowed(['jpg', 'png','jpeg'])])
    descripcion = TextAreaField('Descripcion de receta', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Guardar')

class Form_Preparacion(FlaskForm):
    ordenPaso = IntegerField('Orden', validators=[DataRequired()])
    descripcionPaso = TextAreaField('Descripción',validators=[DataRequired()])
    tiempoPaso = IntegerField('Tiempo de preparación del paso', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class Form_Ingrediente(FlaskForm):
    descripcionIngrediente = SelectField('Nombre del ingrediente',id = 'descripcionIngrediente',choices=[],coerce=int)
    unidad = SelectField('Unidad',choices=[],coerce=int)
    cantidad = StringField('Cantidad',validators=[DataRequired()])
    submit = SubmitField('Agregar')

class Form_Editar_Ing_Por_Receta(FlaskForm):
    descripcionIngrediente = StringField('Ingrediente',validators=[DataRequired()])
    unidad = SelectField('Unidad',choices=[],coerce=int)
    cantidad = StringField('Cantidad',validators=[DataRequired()])
    submit = SubmitField('Guardar')

class BuscarPorReceta(FlaskForm):
    nombreReceta = StringField('Busqueda Nombre', validators=[Length(min=2, max=20)])
    submit = SubmitField('Buscar')

class BuscarPorIngrediente(FlaskForm):
    nombreIngrediente = StringField('Busqueda Ingrediente', id='ingrediente_autocomplete', validators=[Length(min=2, max=20)])
    submit = SubmitField('Agregar')

class CambiarImagen(FlaskForm):
    imagenReceta = FileField('Imagen de la receta',validators=[FileAllowed(['jpg', 'png','jpeg'])])
    submit = SubmitField('Guardar')

class CrearIngrediente(FlaskForm):
    descripcionIngrediente = StringField('Nombre del ingrediente', validators=[DataRequired(), Length(min=2, max=50)])
    imagenIngrediente = FileField('Imagen de la receta',validators=[FileAllowed(['jpg', 'png','jpeg'])])
    submit = SubmitField('Agregar')

    def validate_nombreIngrediente(self, nombreIngrediente):
        ingrediente = Ingrediente.query.filter_by(descripcion = nombreIngrediente.data).first()
        if ingrediente:
            raise ValidationError('Ya existe ese ingrediente!')

class CrearUnidad(FlaskForm):
    descripcionUnidad = StringField('Nombre de la unidad', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Agregar')

    def validate_nombreUnidad(self, nombreUnidad):
        unidad = Unidad.query.filter_by(descripcion = nombreUnidad.data).first()
        if unidad:
            raise ValidationError('Ya existe esa unidad!')

class CrearDificultad(FlaskForm):
    descripcionDificultad = StringField('Nombre nivel dificultad', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Agregar')

    def validate_nombreDificultad(self, nombreDificultad):
        dificultad = Dificultad.query.filter_by(descripcion = nombreDificultad.data).first()
        if dificultad:
            raise ValidationError('Ya existe esa unidad!')

class CrearConsejo(FlaskForm):
    tituloConsejo = StringField('Título del consejo', validators=[DataRequired(), Length(min=2, max=50)])
    descripcionConsejo = TextAreaField('Descripcion detallada', validators=[DataRequired()])
    submit = SubmitField('Agregar')

class CrearAdmin(FlaskForm):
    usuario = SelectField('Usuario',choices=[], coerce=int)
    submit = SubmitField('Agregar')

class CrearUsuario(FlaskForm):
    nombreUsuario = StringField('Nombre', validators=[DataRequired('Debes completar este campo'), Length(min=2, max=20)])
    apellidoUsuario = StringField('Apellido', validators=[DataRequired('Debes completar este campo'), Length(min=2, max=20)])
    emailUsuario = StringField('Email', validators=[Email('Ingresa un formato de email válido.')])
    contraseniaUsuario = PasswordField('Contraseña',validators=[DataRequired('Debes completar este campo'), EqualTo('repetirContrasenia','Las contraseñas deben conicidir.')])
    repetirContrasenia = PasswordField('repetirContrasenia',validators=[DataRequired('Debes completar este campo')])
    submit = SubmitField('Agregar')

    def validate_emailUsuario(self, emailUsuario):
        usuario = Usuario.query.filter_by(email = emailUsuario.data).first()
        if usuario:
            raise ValidationError('Ya existe un usuario con ese correo electrónico')

class ReseteoContrasenia(FlaskForm):
    emailUsuario = StringField('Email', validators=[Email('Ingresa un formato de email válido.')])
    submit = SubmitField('Resetear Contraseña')

    def validate_existeEmailUsuario(self, emailUsuario):
        usuario = Usuario.query.filter_by(email = emailUsuario.data).first()
        if not usuario:
            raise ValidationError('No existe un usuario con ese correo electrónico')

class SearchForm(FlaskForm):
    autocomp = StringField('Insert City', id='city_autocomplete')


