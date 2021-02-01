from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from models import Administrador, Ingrediente, Preparacion, Receta, Ingrediente_Por_Receta

class LoginForm(FlaskForm):
    nombreUsuario = StringField(
                        'Nombre de usuario', 
                        validators=[
                            DataRequired(), 
                            Length(min=2, max=20)
                        ]
                    )
    contrasenia = PasswordField(
                    'Contraseña',
                    validators=[
                        DataRequired()
                    ]
                )
    submit = SubmitField('Ingresar')

    def validacion_nombreUsuario(nombreUsuario):
        administrador = Administrador.query.filter_by(nombre_usuario = nombreUsuario.data).first()
        if administrador:
            raise ValidationError('Ya existe ese nombre de usuario!')

class InformacionGeneral(FlaskForm):
    nombreReceta = StringField(
                    'Nombre de la receta', 
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=50)
                    ]
                )
    tiempoPreparacion = IntegerField(
                            'Tiempo de preparación', 
                            validators=[
                                DataRequired()
                            ]
                        )
    dificultad = SelectField(
                    'Dificultad',
                    choices=[], 
                    coerce=int
                )
    imagenReceta = FileField('Imagen de la receta')
    nombreImagen = StringField(
                    'Nombre de la imagen', 
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=20)
                    ]
                )
    submit = SubmitField('Siguiente')

class IngredientesReceta(FlaskForm):
    nombreIngrediente = StringField(
                            'Nombre del ingrediente', 
                            validators=[
                                DataRequired(), 
                                Length(min=2, max=50)
                            ]
                        )
    cantidad = IntegerField(
                'Cantidad', 
                validators=[
                    DataRequired()
                ]
            )
    unidad = SelectField(
                'Unidad',
                choices=[], 
                coerce=int
            )
    submit = SubmitField('Siguiente')

class PreparacionReceta(FlaskForm):
    ordenPaso = IntegerField(
                    'Orden del paso', 
                    validators=[
                        DataRequired()
                    ]
                )
    descripcion = TextAreaField(
                    'Descripcion',
                    validators=[
                        DataRequired()
                    ]
                )
    submit = SubmitField('Finalizar')

class CambioContraseniaAdmin(FlaskForm):
    nombreUsuario = StringField(
                        'Nombre de usuario', 
                        validators=[
                            DataRequired(), 
                            Length(min=2, max=20)
                        ]
                    )
    contraseniaAntigua = PasswordField(
                            'Antigua contraseña', 
                            validators=[
                                DataRequired()
                            ]
                        )
    contraseniaNueva = PasswordField(
                        'Nueva contraseña', 
                        validators=[
                            DataRequired()
                        ]
                    )
    repetirContraseniaNueva = PasswordField(
                                'Repetir nueva contraseña', 
                                validators=[
                                    DataRequired(),
                                    EqualTo('contraseniaNueva')
                                ]
                            )
    submit = SubmitField('Cambiar contraseña')

class NuevoAdmin(FlaskForm):
    nombreApellido = StringField(
                'Nombre y apellido', 
                validators=[
                    DataRequired(), 
                    Length(min=2, max=100)
                ]
            )
    nombreUsuario = StringField(
                        'Nombre de usuario', 
                        validators=[
                            DataRequired(), 
                            Length(min=2, max=20)
                        ]
                    )
    email = StringField(
                'E-mail', 
                validators=[
                    DataRequired(),
                    Email()
                ]
            )
    contrasenia = PasswordField(
                    'Contraseña', 
                    validators=[
                        DataRequired()
                    ]
                )
    repetirContrasenia = PasswordField(
                            'Repetir contraseña', 
                            validators=[
                                DataRequired(),
                                EqualTo('contraseniaNueva')
                            ]
                        )
    superAdmin = BooleanField('Super Administrador')
    submit = SubmitField('Cambiar contraseña')
    
    def validacion_nombreUsuario(nombreUsuario):
        administrador = Administrador.query.filter_by(nombre_usuario = nombreUsuario.data).first()
        if administrador:
            raise ValidationError('Ya existe ese nombre de usuario!')
    
    def validacion_email(email):
        administrador = Administrador.query.filter_by(email = email.data).first()
        if administrador:
            raise ValidationError('Ese E-mail ya esta registrado!')
        
class NuevaUnidad(FlaskForm):
    nombreUnidad = StringField(
                    'Nombre de la unidad', 
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=50)
                    ]
                )
    submit = SubmitField('Agregar')

class NuevoIngrediente(FlaskForm):
    nombreIngrediente = StringField(
                            'Nombre del ingrediente', 
                            validators=[
                                DataRequired(), 
                                Length(min=2, max=50)
                            ]
                        )
    unidad = SelectField(
                'Unidad',
                choices=[], 
                coerce=int
            )
    imagenIngrediente = FileField('Imagen del ingrediente')
    nombreImagen = StringField(
                    'Nombre de la imagen', 
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=20)
                    ]
                )
    submit = SubmitField('Agregar')