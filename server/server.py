#!/usr/bin/env python

from flask import Flask, request, Response
from flask_cors import CORS
from flask_pymongo import PyMongo, ASCENDING, DESCENDING

from bson import json_util
from bson.objectid import ObjectId

import json

from util import deep_update, subdict

app = Flask(__name__)
CORS(app)

#app.config['MONGO_HOST'] = 'bbpca015'
#app.config['MONGO_DBNAME'] = 'test'

mongo = PyMongo(app)


def convert_id(doc):
    doc['_id'] = str(doc['_id'])
    return doc


def json_response(data):
    return Response(json_util.dumps(data), mimetype="application/json")


@app.route('/activities/', methods=['POST'])
def post_activity():
    doc = json.loads(request.get_data())
    _id = mongo.db.activities.insert(doc)
    # update input resources 'used_by'
    # update output resources 'created_by'
    return str(_id)


@app.route('/activities/', methods=['GET'])
def get_activities():
    return json_response(map(convert_id, mongo.db.activities.find(request.args)))


@app.route('/activities/<_id>', methods=['GET'])
def get_activity(_id):
    return json_response(convert_id(mongo.db.activities.find_one({'_id': ObjectId(_id)})))


@app.route('/entities/', methods=['POST'])
def post_entity():
    doc = json.loads(request.get_data())
    _id = mongo.db.entities.insert(doc)
    return str(_id)


@app.route('/entities/<_id>', methods=['PUT'])
def put_entity(_id):
    doc = json.loads(request.get_data())
    doc['_id'] = ObjectId(_id)
    _id = mongo.db.entities.insert(doc)
    return str(_id)


@app.route('/entities/', methods=['GET'])
def get_entities():
    return json_response(map(convert_id, mongo.db.entities.find(request.args)))


@app.route('/entities/<_id>', methods=['GET'])
def get_entity(_id):
    return json_response(convert_id(mongo.db.entities.find_one({'_id': ObjectId(_id)})))


@app.route('/circuit_analyses/', methods=['POST'])
def post_circuit_analysis():
    doc = json.loads(request.get_data())
    _id = mongo.db.circuit_analyses.insert(doc)
    return str(_id)


@app.route('/circuit_analyses/<_id>', methods=['PUT'])
def put_circuit_analysis(_id):
    doc = json.loads(request.get_data())
    mongo.db.circuit_analyses.update_one({'id_': ObjectId(_id)}, {'$set': doc})
    return str(_id)


@app.route('/circuit_analyses/', methods=['GET'])
def get_circuit_analyses():
    return json_response(map(convert_id, mongo.db.circuit_analyses.find(request.args)))


@app.route('/circuit_analyses/<_id>', methods=['GET'])
def get_circuit_analysis(_id):
    return json_response(convert_id(mongo.db.circuit_analyses.find_one({'_id': ObjectId(_id)})))


@app.route('/builds/', methods=['POST'])
def post_build():
    doc = json.loads(request.get_data())
    _id = mongo.db.builds.insert(doc)
    return str(_id)


@app.route('/builds/<_id>', methods=['PATCH'])
def patch_build(_id):
    build = mongo.db.builds.find_one({'_id': ObjectId(_id)})
    delta = json.loads(request.get_data())
    deep_update(build, delta)
    mongo.db.builds.update({'_id': ObjectId(_id)}, build)
    return json_response(build)


@app.route('/builds/', methods=['GET'])
def get_builds():
    filter_args = subdict(request.args, ['template', 'status'])
    result = mongo.db.builds.find(filter_args)

    if 'orderby' in request.args:
        field, order = request.args['orderby'].split("+")
        order = {
            'ASC': ASCENDING,
            'DESC': DESCENDING,
        }[order.upper()]
        result = result.sort(field, order)

    return json_response(map(convert_id, result))


@app.route('/builds/<_id>', methods=['GET'])
def get_build(_id):
    return json_response(convert_id(mongo.db.builds.find_one({'_id': ObjectId(_id)})))


@app.route('/build_templates/', methods=['GET'])
def get_build_templates():
    return json_response(map(convert_id, mongo.db.build_templates.find(request.args)))


@app.route('/circuits/', methods=['POST'])
def post_circuit():
    doc = json.loads(request.get_data())
    _id = mongo.db.circuits.insert(doc)
    return str(_id)


@app.route('/circuits/', methods=['GET'])
def get_circuits():
    filter_args = subdict(request.args, ['status'])
    result = mongo.db.circuits.find(filter_args)

    if 'orderby' in request.args:
        field, order = request.args['orderby'].split("+")
        order = {
            'ASC': ASCENDING,
            'DESC': DESCENDING,
        }[order.upper()]
        result = result.sort(field, order)

    return json_response(map(convert_id, result))


@app.route('/circuits/<_id>', methods=['GET'])
def get_circuit(_id):
    return json_response(convert_id(mongo.db.circuits.find_one({'_id': ObjectId(_id)})))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
