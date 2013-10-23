from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy

from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'postgres://localhost:5432/traces')

db = SQLAlchemy(app)
api = restful.Api(app)


class Trace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100))
    trace = db.Column(db.Text())

    def __init__(self, page, trace):
        self.page = page
        self.trace = trace

    def __repr__(self):
        return '{} {}'.format(self.id, self.page)


class HelloWorld(restful.Resource):
    def get(self):
        traces = Trace.query.order_by(Trace.id.desc()).limit(3)
        return [{
            'page': trace.page,
            'trace': trace.trace
        } for trace in traces]

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)
