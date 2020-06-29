import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

from models import Book

class Hola(Resource):
    def get(self, name):
        return {"Hello":name}

class Hola2(Resource):
    def get(self):
        return {"HOLASA":"HOLASA"}

api.add_resource(Hola, '/hola/<name>')
api.add_resource(Hola2, '/hola2')


if __name__ == '__main__':
     app.run(debug=True)