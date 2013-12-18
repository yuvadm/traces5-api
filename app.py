import json

from flask import Flask, request
from flask.ext import restful
from flask.ext.cache import Cache
from flask.ext.restful import reqparse
from flask.ext.sqlalchemy import SQLAlchemy

from os import environ

from cors import crossdomain

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'postgres://localhost:5432/traces')

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': environ.get('REDISCLOUD_URL', 'redis://localhost')
})
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

@cache.memoize(timeout=60*2)
def _get_page_traces(page=None, limit=3):
    print 'hit'
    traces = Trace.query
    if page:
        traces = traces.filter_by(page=page)
    traces = traces.order_by(Trace.id.desc()).limit(limit)
    return json.dumps([{
        'page': trace.page,
        'trace': json.loads(trace.trace)
    } for trace in traces])


class Traces(restful.Resource):
    @crossdomain(origin='*')
    def get(self):
        args = trace_parser.parse_args()
        page = request.args.get('page')
        limit = int(request.args.get('limit', '3'))
        return _get_page_traces(page, limit)

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
