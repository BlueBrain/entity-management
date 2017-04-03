#!/usr/bin/env python

from flask import Flask, request, Response
from flask_cors import CORS
from flask_pymongo import PyMongo

from bson import json_util
from bson.objectid import ObjectId

import json

from util import deep_update

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


@app.route('/entities/', methods=['GET'])
def get_entities():
    return json_response(map(convert_id, mongo.db.entities.find(request.args)))


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
    return json_response(map(convert_id, mongo.db.builds.find(request.args)))


@app.route('/builds/<_id>', methods=['GET'])
def get_build(_id):
    return json_response(convert_id(mongo.db.builds.find_one({'_id': ObjectId(_id)})))


@app.route('/build_templates/', methods=['GET'])
def get_build_templates():
    return json_response(map(convert_id, mongo.db.build_templates.find(request.args)))


@app.route('/circuits/<_id>', methods=['GET'])
def get_circuit(_id):
    return json_response(convert_id(mongo.db.circuits.find_one({'_id': ObjectId(_id)}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
