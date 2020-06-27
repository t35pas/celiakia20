from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Hola(Resource):
    def get(self, name):
        return {"Hello":name}

api.add_resource(Hola, '/hola/<name>')

if __name__ == '__main__':
     app.run(debug=True)