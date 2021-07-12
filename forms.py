from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, RadioField
from wtforms.fields.core import BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from models import Administrador, Ingrediente, Preparacion, Receta, Ingrediente_Por_Receta, Unidad, Dificultad

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

class NuevaReceta(FlaskForm):
    tituloReceta = StringField(
                    'Titulo de la receta', 
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
    imagenReceta = FileField(
                    'Imagen de la receta',
                    validators=[
                        FileRequired(),
                        FileAllowed(['jpg', 'png'])
                    ]
                )
    nombreImagen = StringField(
                    'Nombre de la imagen', 
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=20),
                    ]
                )
    submit = SubmitField('Siguiente')

    def validate_nombreImagen(self, nombreImagen):
        receta = Receta.query.filter_by(nombre_imagen = nombreImagen.data).first()
        if receta:
            raise ValidationError('Ya existe ese nombre de imagen!')
    
    def validate_tituloReceta(self, tituloReceta):
        receta = Receta.query.filter_by(titulo = tituloReceta.data).first()
        if receta:
            raise ValidationError('Ya existe ese Título!')

class EditarInfoGral(FlaskForm):
    
    tituloReceta = StringField(
                    'Titulo de la receta', 
                    id="editarTitulo",
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=50)
                    ]
                )
    tiempoPreparacion = IntegerField(
                    'Tiempo de preparación', 
                    id="editarTiempoPreparacion",
                    validators=[
                        DataRequired()
                    ]
                        )
    dificultad = SelectField(
                    'Dificultad',
                    id="editarDificultad",
                    choices=[(dif.id, dif.descripcion) for dif in Dificultad.query.all()], 
                    coerce=int
                )
    imagenReceta = FileField(
                    'Imagen de la receta',
                    id="editarImagenReceta",
                    validators=[
                        FileAllowed(['jpg', 'png'])
                    ]
                )
    nombreImagen = StringField(
                    'Nombre de la imagen',
                    id="editarNombreImagenReceta", 
                    validators=[
                        DataRequired(), 
                        Length(min=2, max=20),
                    ]
                )
    submit = SubmitField('Actualizar')

class NuevaPreparacion(FlaskForm):
    ordenPaso = IntegerField(
                    'Orden', 
                    validators=[
                        DataRequired()
                    ]
                )
    descripcion = TextAreaField(
                    'Descripción',
                    validators=[
                        DataRequired()
                    ]
                )
    submit = SubmitField('Agregar')

class EditarPreparacion(FlaskForm):
    ordenPaso = IntegerField(
                    'Orden', 
                    id = 'editarOrdenPaso',
                    validators=[
                        DataRequired()
                    ]
                )
    descripcion = TextAreaField(
                    'Descripción',
                    id = 'editarDescripcion',
                    validators=[
                        DataRequired()
                    ]
                )
    submit = SubmitField('Actualizar',
                    id = 'actualizar')

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
    
    def validate_nombreUsuario(self, nombreUsuario):
        administrador = Administrador.query.filter_by(nombre_usuario = nombreUsuario.data).first()
        if administrador:
            raise ValidationError('Ya existe ese nombre de usuario!')
    
    def validate_email(self, email):
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

    def validate_nombreUnidad(self, nombreUnidad):
        unidad = Unidad.query.filter_by(descripcion = nombreUnidad.data).first()
        if unidad:
            raise ValidationError('Ya existe esa unidad!')

class NuevoIngrediente(FlaskForm):

    nombreIngrediente = StringField(
                            'Nombre del ingrediente',
                            id="nombreIngrediente"
                        )
    elegirNombreIngrediente = SelectField(
                            'Nombre del ingrediente',
                            id = 'elegirNombreIngrediente',
                            choices=[],
                            coerce=int
                        )
    unidad = SelectField(
                'Unidad',
                choices=[],
                coerce=int
            )
    cantidad = IntegerField(
                'Cantidad',
                validators=[
                    DataRequired()
                ]
            )
    imagenIngrediente = FileField(
                    'Imagen del Ingrediente',
                    validators=[
                        FileAllowed(['jpg', 'png'])
                    ]
                )
    nombreImagen = StringField(
                    'Nombre de la imagen'
                )
    submit = SubmitField('Agregar')

    def validate_nombreImagen(self, nombreImagen):
        ingrediente = Ingrediente.query.filter_by(nombre_imagen = nombreImagen.data).first()
        if ingrediente:
            raise ValidationError('Ya existe ese nombre de imagen!')
    def validate_nombreIngrediente_unidad(self, nombreIngrediente, unidad):
        ingredientes = Ingrediente.query.filter_by(descripcion = nombreIngrediente.data)
        for ingrediente in ingredientes:
            if ingrediente.unidad == unidad.data:
                raise ValidationError('Ya existe ese ingrediente!')

class EditarIngrediente(FlaskForm):
    nombreIngrediente = StringField(
                        'Nombre del ingrediente',
                        id = 'editarNombreIngrediente',
                        validators=[
                            DataRequired(), 
                            Length(min=2, max=50)
                        ]
                    )
    unidad = SelectField(
                'Unidad',
                id = 'editarUnidad',
                choices=[(u.id, u.descripcion) for u in Unidad.query.all()], 
                coerce=int
            )
    cantidad = IntegerField(
                'Cantidad',
                id = 'editarCantidad',
                validators=[
                    DataRequired()
                ]
            )
    imagenIngrediente = FileField(
                    'Imagen del Ingrediente',
                    id = 'editarImagenIngrediente',
                    validators=[
                        FileAllowed(['jpg', 'png'])
                    ]
                )
    nombreImagen = StringField(
                    'Nombre de la imagen',
                    id = 'editarNombreImagenIng', 
                    validators=[
                        Length(min=2, max=20)
                    ]
                )
    submit = SubmitField('Actualizar')

