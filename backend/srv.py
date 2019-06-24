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


from sklearn.cluster import KMeans

from random import sample

import matplotlib.pylab as plt

from tqdm import tqdm

cachedir = './cache/'
if not exists(cachedir):
    makedirs(cachedir)
memory = Memory(cachedir, verbose=0)


def _bbox_create_buffer(bbox: dict) -> list:
    minX = bbox['_sw']['lng']
    minY = bbox['_sw']['lat']
    maxX = bbox['_ne']['lng']
    maxY = bbox['_ne']['lat']

    p1 = np.array([minX, minY])
    p2 = np.array([maxX, maxY])
    p1n = (p1-p2)*1.05+p2  # ~10% a^2+b^2=c^2, so that number gets ^2
    p2n = (p2-p1)*1.05+p1
    # p1n=p1
    # p2n=p2
    return([np.floor(p1n[0]),
            np.floor(p1n[1]),
            np.ceil(p2n[0]),
            np.ceil(p2n[1])])


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
def _mapHiers(ds: dataStore, aspects: list, threshold: float = 0.75, nClusters: int = 10, bbox: list = None):
    Gs = mapHierarchies(ds, aspects, bbox=bbox)

    print('got merged')

    # sim = []
    # for a in ds.aspects():
    #     print('comparing ', a)
    #     g = ds.getGeometry(a)
    #     if g not in Gs:
    #         g = list(Gs.keys())[-1]
    #     d = compareHierarchies(ds, Gs[g], a, g1=g)
    #     sim.append({'id': a,
    #                 'geometry': g,
    #                 'name': ds.getAspectName(a)+' {0}'.format(d),
    #                 'selected': a in aspects,
    #                 'x': d,
    #                 'y': ds.getAspectYear(a)})

    cl = {}
    for g in Gs:
        cl[g] = {}

    full_info_aspects = [{'name': ds.getAspectName(a),
                          'year': ds.getAspectYear(a),
                          'geom': ds.getGeometry(a),
                          'cols': ds.getColumns(a),
                          'id': a,
                          'descr': ds.getDescriptions_AsDict(a)}
                         for a in aspects]

    full_info_aspects = sorted(full_info_aspects, key=lambda x: x['year'])
    # preparations for the domains in ParallelCoordinates (react-vis)
    for i in range(len(full_info_aspects)):
        full_info_aspects[i]['order'] = i
        full_info_aspects[i]['visible'] = True

    geoms = sorted(list(Gs.keys()))

    # for threshold in thresholds:

    cc2n = {}
    for g in geoms:
        Gs[g].remove_edges_from([e[:2] for e in Gs[g].edges(data='level')
                                 if e[2] >= threshold])
        cc2n[g] = {}
        for cc, nodes in enumerate(nx.connected_components(Gs[g])):
            cc2n[g][cc] = [n[1] for n in nodes]
            for n in nodes:
                cl[g][n[1]]=cc


    M = nx.DiGraph()
    for g1 in geoms:
        for g2 in geoms:
            if (g1 != g2):
                X = ds.getCrossGeometry(g1, g2)
                for n in cl[g1]:
                    source = (g1, cl[g1][n])
                    # area = sum([e[2] for e in X.edges(source,data='intersection')])
                    if (source not in M):
                        M.add_node(source)
                    if 'area' not in M.node[source]:
                        M.node[source]['area'] = {}
                    if g2 not in M.node[source]['area']:
                        M.node[source]['area'][g2] = 0

                    for nn in X.neighbors((g1, n)):
                        # only goes in if the target is inside the bbox
                        if nn[1] in cl[g2]:
                            intersection = X[(g1, n)][nn]['intersection']
                            M.node[source]['area'][g2] += intersection
                            target = (g2, cl[g2][nn[1]])
                            if not target in M:
                                M.add_node(target)
                            if not M.has_edge(source, target):
                                M.add_edge(source, target, area=0)
                            M[source][target]['area'] += intersection

    for e in M.edges():
        if e[1][0] in M.node[e[0]]['area']:
            M[e[0]][e[1]]['area'] /= M.node[e[0]]['area'][e[1][0]]

    # keeps only the highest sucessor for each geometry
    for n in M:
        to_remove = []
        picks = {}
        for nn in M.successors(n):
            cval = M[n][nn]['area']
            g = nn[0]
            if g not in picks:
                picks[g] = (nn, cval)
            else:
                if cval > picks[g][1]:
                    to_remove.append((n, picks[g][0]))
                    picks[g] = (nn, cval)
                else:
                    to_remove.append((n, nn))
        M.remove_edges_from(to_remove)

    points = {}
    for info in full_info_aspects:
        a = info['id']
        g = info['geom']
        points[a] = {}
        for cc in cc2n[g]:
            vals = [ds.getProjection(a, id) for id in cc2n[g][cc]]
            vals = [x for x in vals if (x is not None)]
            if vals:
                points[a][cc] = np.nanmedian(vals)

    a = full_info_aspects[0]['id']
    g = full_info_aspects[0]['geom']
    paths = [[{'geom': n[0],
               'id':n[1],
               'x':a,
               'y':points[a][n[1]]}, ]
             for n in M if n[0] == g
             if n[1] in points[a]]

    for info in full_info_aspects[1:]:
        g = info['geom']
        a = info['id']
        to_add = []
        unused = set([n[1] for n in M if n[0] == g])
        while paths:
            current = paths.pop(0)
            last = {**current[-1]}
            if last['geom'] == g:  # same geometry:
                if last['id'] in points[a]:
                    to_add.append(current+[last, ])
                    to_add[-1][-1]['x'] = a
                    to_add[-1][-1]['y'] = points[a][last['id']]
                unused.discard(last['id'])
            else:
                options = [n for n in M.successors(
                    (last['geom'], last['id'])) if n[0] == g]
                if not options:
                    to_add.append(current)
                for op in options:
                    unused.discard(op[1])
                    if op[1] in points[a]:
                        to_add.append(current+[{'geom': g,
                                                'id': op[1],
                                                'x':a,
                                                'y':points[a][op[1]]}, ])
        # puts in the paths that didn't start at the first aspect
        paths = to_add+[[{'geom': g,
                          'id': x,
                          'x': a,
                          'y': points[a][x]}, ] for x in unused if x in points[a]]

    # converts to parallelplots format
    retPaths = []
    for p in paths:
        newPath = {}
        for step in p:
            newPath[step['x']] = step['y']
        retPaths.append(newPath)
    
    a2i={A['id']:A['order'] for A in full_info_aspects}
    X = np.zeros((len(retPaths),len(full_info_aspects)))
    for i,p in enumerate(retPaths):
        for a in p:
            X[i,a2i[a]]=p[a]
    Y = KMeans(n_clusters=nClusters).fit_predict(X)


    return({'clustering': cl, 'evolution': retPaths, 'aspects': full_info_aspects})


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

        if ('bbox' not in input_json):
            bbox = None
        else:
            #{'_sw': {'lng': -97.36262426260146, 'lat': 24.36091074100848}, '_ne': {'lng': -65.39166177011971, 'lat': 33.61501866716327}}
            bbox = _bbox_create_buffer(input_json['bbox'])

        if ('nc' not in input_json):
            nc = 10
        else:
            nc = int(input_json['nc'])

        return(_mapHiers(ds, sorted(to_use), nc, bbox=bbox))

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
    if (len(sys.argv)) > 2:
        print(".py [conf.json]")
        exit(-1)
    if len(sys.argv) == 1:
        confFile = 'conf.json'
    else:
        confFile = sys.argv[1]

    if not exists(confFile):
        print('configuration file not found')
        exit(-1)

    dirconf = {'upload': './upload',  # unconfigured data
               'db': './db',  # geometries/graphs
               'data': './db/data'}  # configured aspects/hierarchies

    for k in dirconf:
        if (not exists(dirconf[k])):
            makedirs(dirconf[k])

    ds = dataStore(dirconf['db'], dirconf['data'])

    with open(confFile, 'r') as fin:
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

    # thresholds: list = [0.999, 0.75, 0.5]
    # to_use = ['14b48d89-0bea-491e-8f3a-cf363845c5a7', '15e7ff9d-1c4f-4acc-9c91-1e046b151af5', '1877f60e-241c-4050-9c79-5b6b44454973', '1d738eff-ad39-49e4-a837-f2596715b8fe', '1e52d9c3-5dde-4765-9b7c-e864e1a93d25', '204f536f-2cac-445c-bd15-040c866fe479', '22f6ce38-2905-4031-86bc-30d9961ac37e', '242b7fda-9589-4dca-8884-f3c878f1af8f', '2b58be95-055d-4552-895b-08b3e7bad170', '2d5a840f-df04-4dcd-9a4c-be1f642a9b0b', '38502f50-3d9f-409f-aad1-a67b2b58cdfb', '4556dd88-5790-4dc6-9577-b1608ce81995', '45e24c40-fccd-4569-8325-b6d310bcbb63', '49968c14-3b78-4018-ad4b-93ca92be7787', '4a37b2fe-529e-4d29-ad9b-9f673f1ac540', '52787af7-a197-42a3-b5bb-b66a9d75170d', '528fd86d-663c-46e8-9cca-b884db6e7ea6', '566cee34-a675-4dab-883c-56dcf43d2692', '57bbb4da-2fa3-4283-acb4-aa19b1220f0c', '5cdca1a8-a666-4b80-8be6-f41b66130f30',
    #           '6096ec62-a36e-42da-b4ad-1f17f02d0401', '723dea41-7e9f-4749-ad7b-a1e017b12893', '73022894-6f58-46d3-bf49-b714d7bb7c31', '973082d5-4f3e-4d79-be6d-f783135b1eba', '9e43d7a8-8af1-4a02-a961-474080aa78b8', 'a61a5b30-4083-43fd-88c0-22d60c8d4295', 'b3114d6c-8480-4181-9fa0-f13981f781f3', 'b614e09d-5d70-4b96-8977-4737c0db6f13', 'b9f254c2-3035-4fae-bf80-de96241f3885', 'ba0b0a20-f757-4521-a5aa-8478311e96e0', 'c5d7e898-2832-472e-8bb5-822c46b8389e', 'cc818a72-420b-486f-a060-283302b5e49b', 'd1701771-1e66-4b0a-825e-71142f9acaa7', 'd1bd3caa-9820-41ee-b68c-2fbe86ec0543', 'd426366b-08c5-4e36-a9fe-a08ee154de90', 'd9633dd9-8079-47b0-af9d-7732157228ae', 'de0e9a71-2ddf-43f7-a149-af2602ddf614', 'e059fe12-15a9-459f-8d65-6d4af41ee7cf', 'f3b9dc44-86d1-493c-a826-220c7919d90c', 'fbba5ff9-9bca-4141-85f8-7de470208e60', 'fd9d6283-cc5f-4b61-a0d4-0e3c61a99bd2']
    # _mapHiers(ds, sorted(to_use), thresholds)
    # exit()

    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)
    cherrypy.server.max_request_body_size = 0  # for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
