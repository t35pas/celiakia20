from typing import Text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, RadioField
from wtforms.fields.core import BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from models import Dificultad,Favorito,Ingrediente,Ingrediente_Por_Receta,Preparacion,Receta,Unidad,Usuario

class LoginForm(FlaskForm):
    nombreUsuario = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=20)])
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
    tiempoPaso = IntegerField('Tiempo aprox del paso', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class Form_Ingrediente(FlaskForm):
    descripcionIngrediente = SelectField('Nombre del ingrediente',id = 'descripcionIngrediente',choices=[],coerce=int)
    unidad = SelectField('Unidad',choices=[],coerce=int)
    cantidad = IntegerField('Cantidad',validators=[DataRequired()])
    submit = SubmitField('Agregar')

class Form_Editar_Ing_Por_Receta(FlaskForm):
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

        
class NuevaUnidad(FlaskForm):
    nombreUnidad = StringField('Nombre de la unidad', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Agregar')

    def validate_nombreUnidad(self, nombreUnidad):
        unidad = Unidad.query.filter_by(descripcion = nombreUnidad.data).first()
        if unidad:
            raise ValidationError('Ya existe esa unidad!')

class SearchForm(FlaskForm):
    autocomp = StringField('Insert City', id='city_autocomplete')


