"""Server module for the backend"""
import json
import os
import pickle
import sys
from itertools import combinations, combinations_with_replacement
from os import makedirs
from os.path import exists, join
from time import time

import numpy as np

import cherrypy
import networkx as nx
import tempfile

from networkx.readwrite import json_graph
from upload import processUploadFolder, gatherInfoJsons
from hierarchies import mapHierarchies, compareHierarchies
import pandas as pd
from dataStore import dataStore
from joblib import Memory

from sklearn.manifold import MDS, TSNE


cachedir = './cache/'
if not exists(cachedir):
    makedirs(cachedir)
memory = Memory(cachedir, verbose=0)


def cors():
    if cherrypy.request.method == 'OPTIONS':
        # preflign request
        # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        # tell CherryPy no avoid normal handler
        return True
    else:
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'


@memory.cache(ignore=['ds'])
def _mapHiers(ds: dataStore, aspects: list, thresholds: list):
    Gs = mapHierarchies(ds, aspects)

    print('got merged')

    sim = []
    for a in ds.aspects():
        print('comparing ', a)
        g = ds.getGeometry(a)
        if g not in Gs:
            g = list(Gs.keys())[-1]
        d = compareHierarchies(ds, Gs[g], a, g1=g)
        sim.append({'id': a,
                    'geometry': g,
                    'name': ds.getAspectName(a)+' {0}'.format(d),
                    'selected': a in aspects,
                    'x': d,
                    'y': ds.getAspectYear(a)})

    cl = {}
    for g in Gs:
        cl[g] = {}
        for n in Gs[g]:
            cl[g][n[1]] = []

    for threshold in thresholds:
        for g in Gs:
            Gs[g].remove_edges_from(
                [e[:2] for e in Gs[g].edges(data='level') if (e[2] > threshold)])
            for cc, nodes in enumerate(nx.connected_components(Gs[g])):
                for n in nodes:
                    cl[g][n[1]].append(cc)

    return({'clustering': cl, 'similarity': sim})


@cherrypy.expose
class server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip()
    def availableGeometries(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret = []
        for g in available_geometries:
            ret.append({'name':  g['name'],
                        'url': g['url'],
                        'source': g['source'],
                        'year': g['year']
                        })
        return(ret)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip()
    def availableAspects(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        return(ds.aspects())

    # @cherrypy.expose
    # @cherrypy.config(**{'tools.cors.on': True})
    # @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    # @cherrypy.tools.gzip()
    # def getAspectProjection(self):
    #     cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    #     input_json = cherrypy.request.json
    #     if ('aspects' not in input_json) or (len(input_json['aspects']) <= 1):
    #         to_use = ds.aspects()
    #     else:
    #         to_use = input_json['aspects']
    #     return(_getDistances(ds, sorted(to_use)))

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def createAspects(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        return(ds.createAspect(input_json, dirconf['upload']))

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def mapHierarchies(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        if ('aspects' not in input_json) or (not input_json['aspects']):
            to_use = ds.aspects()
        else:
            to_use = input_json['aspects']

        thresholds: list = [0.9, 0.75, 0.5]
        # thresholds: _lists_ of cutting points for the normalized hierarchies.
        return(_mapHiers(ds, sorted(to_use), thresholds))

        # print('\n\n - map - \n\n')
        # print(input_json)
        # print(to_use)

    @cherrypy.expose
    def index(self):
        return("It works!")

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def getUploadedData(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        return(gatherInfoJsons(dirconf['upload']))

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def upload(self, file):
        myFile = file
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        res = {'name': myFile.filename, 'ok': True}
        with tempfile.TemporaryDirectory() as tempDir:
            fname = join(tempDir, myFile.filename)
            with open(fname, 'wb') as outFile:
                while True:
                    data = myFile.file.read(8192)
                    if not data:
                        break
                    outFile.write(data)
            try:
                res.update(processUploadFolder(
                    tempDir, dirconf['upload'], cherrypy.request.remote.ip))
            except:
                # raise
                res['ok'] = False
        return(res)


if __name__ == '__main__':
    if (len(sys.argv)) != 2:
        print(".py conf.json")
        exit(-1)

    dirconf = {'upload': './upload',  # unconfigured data
               'db': './db',  # geometries/graphs
               'data': './db/data'}  # configured aspects/hierarchies

    for k in dirconf:
        if (not exists(dirconf[k])):
            makedirs(dirconf[k])

    ds = dataStore(dirconf['db'], dirconf['data'])

    with open(sys.argv[1], 'r') as fin:
        available_geometries = json.load(fin)

    for g in available_geometries:
        g['graph'] = nx.read_gpickle(join(dirconf['db'], g['name']+'.gp'))

    webapp = server()
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*', 'application/*']
        },
        # '/public': {
        #     'tools.staticdir.on': True,
        #     'tools.staticdir.dir': './public'
        # }
    }
    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)
    cherrypy.server.max_request_body_size = 0  # for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
