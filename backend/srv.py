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

from clustering import ComputeClustering
from networkx.readwrite import json_graph
from upload import processUploadFolder, gatherInfoJsons, create_aspect_from_upload
from hierarchies import mapHierarchies, compareHierarchies
import pandas as pd
from dataStore import dataStore
from joblib import Memory

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


cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)

@memory.cache(ignore=['ds'])
def _getDistances(ds:dict, aspects:list):
    return(ds.getDistances(aspects))


@cherrypy.expose
class server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def availableCountries(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret = []
        for kind in countries:
            c = countries[kind]
            ret.append({'name':  c['name'],
                        'kind':  c['kind'],
                        'geometries': c['geometries']
                        })
        return(ret)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getAspectProjection(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        ds= countries[input_json['countryID']]['ds']
        if ('aspects' not in input_json) or (not input_json['aspects']):
            to_use=ds.aspects()
        else:
            to_use=input_json['aspects']
        return(_getDistances(ds,sorted(to_use)))
        # return(ds.getDistances(to_use))


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def createAspects(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        aspects = create_aspect_from_upload(
            input_json, baseconf['upload'], countries)

        for aspect in aspects:
            country = countries[aspect['country']]
            ds = country['ds']

            G = country['graphs'][aspect['geometry']].copy()

            ncols = len(ds.getColumns(aspect['id']))

            for n in G.nodes():
                vals = ds.getData(aspect['id'],n[1])
                if vals is not None:
                    G.node[n]['data'] = np.array(vals)
                else:
                    G.node[n]['data'] = np.empty((ncols,))
                    G.node[n]['data'][:] = np.nan
            print(aspect['name'])
            G = ComputeClustering(G, 'data')
            print('Done ')
            nx.write_gpickle(G, join(country['data'], aspect['id']+'.gp'))

        for country in countries:
            countries[country]['ds']._update_distances()

        return(aspects)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def mapHierarchies(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        ds= countries[input_json['countryID']]['ds']
        if ('aspects' not in input_json) or (not input_json['aspects']):
            to_use=ds.aspects()
        else:
            to_use=input_json['aspects']

        print(to_use)
        return(mapHierarchies(ds,sorted(to_use)))

    @cherrypy.expose
    def index(self):
        return("It works!")

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def getUploadedData(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        return(gatherInfoJsons(baseconf['upload']))

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getAspects(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        countryID = input_json['countryID']
        return(gatherInfoJsons(countries[countryID]['data']))

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
                    tempDir, baseconf['upload'], cherrypy.request.remote.ip))
            except:
                # raise
                res['ok'] = False
        return(res)


if __name__ == '__main__':
    if (len(sys.argv)) != 2:
        print(".py conf.json")
        exit(-1)

    countries = {}
    # freshly uploaded (and unconfigured) data goes here
    baseconf = {'upload': './upload'}
    if (not exists(baseconf['upload'])):
        makedirs(baseconf['upload'])

    with open(sys.argv[1], 'r') as fin:
        countriesConfig = json.load(fin)

    for i, v in enumerate(countriesConfig):
        cData = dict()
        cData.update(v)

        baseFolder = v['folder']

        cName = v['name']
        print('\n\n'+cName)

        cData['graphs'] = {}
        for geom in v['geometries']:
            cData['graphs'][geom['name']] = nx.read_gpickle(
                join(baseFolder, geom['name']+'.gp'))

        cData['data'] = join(baseFolder, 'data')
        if not exists(cData['data']):
            makedirs(cData['data'])
        cData['ds'] = dataStore(baseFolder)
        countries[cData['kind']] = cData


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
    cherrypy.server.max_request_body_size = 0  # for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
