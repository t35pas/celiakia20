from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

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