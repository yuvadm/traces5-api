import json

from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse
from flask.ext.sqlalchemy import SQLAlchemy

from os import environ

from cors import crossdomain

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'postgres://localhost:5432/traces')

db = SQLAlchemy(app)
api = restful.Api(app)


trace_parser = reqparse.RequestParser()
trace_parser.add_argument('page', type=str)
trace_parser.add_argument('trace', type=str)


class Trace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100))
    trace = db.Column(db.Text())

    def __init__(self, page, trace):
        self.page = page
        self.trace = trace

    def __repr__(self):
        return '{} {}'.format(self.id, self.page)


class Traces(restful.Resource):
    @crossdomain(origin='*')
    def get(self):
        args = trace_parser.parse_args()
        traces = Trace.query
        if 'page' in request.args:
            traces = traces.filter_by(page=request.args['page'])
        traces = traces.order_by(Trace.id.desc()).limit(int(request.args.get('limit', '3')))
        return json.dumps([{
            'page': trace.page,
            'trace': json.loads(trace.trace)
        } for trace in traces])

    @crossdomain(origin='*')
    def post(self):
        args = trace_parser.parse_args()
        trace = Trace(args['page'], args['trace'])
        db.session.add(trace)
        db.session.commit()
        return 'ok', 201

api.add_resource(Traces, '/traces')

if __name__ == '__main__':
    app.run(debug=True)
