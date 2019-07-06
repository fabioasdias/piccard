"""Server module for the backend"""
import json
import os
import pickle
import sys
import tempfile
from itertools import combinations, combinations_with_replacement
from os import makedirs
from os.path import exists, join
from random import sample
from time import time

import cherrypy
import matplotlib.pylab as plt
import networkx as nx
import numpy as np
import pandas as pd
from joblib import Memory
from networkx.readwrite import json_graph
from sklearn.cluster import KMeans
from tqdm import tqdm

from dataStore import dataStore
from hierarchies import compareHierarchies, mapHierarchies
from upload import gatherInfoJsons, processUploadFolder

cachedir = './cache/'
if not exists(cachedir):
    makedirs(cachedir)
memory = Memory(cachedir, verbose=0)

NBINS = 50


def _mergePaths(p1: dict, p2: dict, id: int):
    if len(p1) == 0:
        return({**p2, 'id': id})
    if len(p2) == 0:
        return({**p1, 'id': id})
    k1 = set(p1.keys())
    k2 = set(p2.keys())
    ret = {**{k: p1[k]
              for k in k1.difference(p2)}, **{k: p2[k] for k in k2.difference(p1)}}
    for k in k1.intersection(k2):
        if p1[k] < 0:
            ret[k] = p2[k]
        elif p2[k] < 0:
            ret[k] = p1[k]
        else:
            ret[k] = (p1[k]+p2[k])/2
    return(ret)


def _bbox_create_buffer(bbox: dict) -> list:
    minX = bbox['_sw']['lng']
    minY = bbox['_sw']['lat']
    maxX = bbox['_ne']['lng']
    maxY = bbox['_ne']['lat']

    p1 = np.array([minX, minY])
    p2 = np.array([maxX, maxY])
    p1n = (p1-p2)*1.05+p2  # ~10% a^2+b^2=c^2, so that number gets ^2
    p2n = (p2-p1)*1.05+p1
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


# @memory.cache(ignore=['ds'])
@profile
def _mapHiers(ds: dataStore, aspects: list, threshold: float = 0.5, nClusters: int = 10, bbox: list = None):
    Gs = mapHierarchies(ds, aspects, bbox=bbox)

    print('got merged')

    cl = {}
    for g in Gs:
        cl[g] = {}

    full_info_aspects = [{'name': ds.getAspectName(a),
                          'year': ds.getAspectYear(a),
                          'geom': ds.getGeometry(a),
                          'cols': ds.getColumns(a),
                          'id': a,
                          'visible': True,
                          'descr': ds.getDescriptions_AsDict(a)}
                         for a in aspects]

    full_info_aspects = sorted(full_info_aspects, key=lambda x: x['year'])
    # preparations for the domains in ParallelCoordinates (react-vis)
    for i in range(len(full_info_aspects)):
        full_info_aspects[i]['order'] = i

    geoms = sorted(list(Gs.keys()))
    cc2n = {}
    for g in geoms:
        Gs[g].remove_edges_from([e[:2] for e in Gs[g].edges(data='level')
                                 if e[2] >= threshold])
        cc2n[g] = {}
        for cc, nodes in enumerate(nx.connected_components(Gs[g])):
            cc2n[g][cc] = [n[1] for n in nodes]
            for n in nodes:
                cl[g][n[1]] = cc

    M = nx.DiGraph()
    for g1 in geoms:
        for g2 in geoms:
            X = ds.getCrossGeometry(g1, g2)
            for n in cl[g1]:
                cc1 = cl[g1][n]
                source = (g1, cc1)
                if (source not in M):
                    M.add_node(source)

                for nn in X.neighbors((g1, n)):
                    # only goes in if the target is inside the bbox
                    if nn[1] in cl[g2]:
                        cc2 = cl[g2][nn[1]]
                        target = (g2, cc2)

                        if not target in M:
                            M.add_node(target)

                        if not M.has_edge(source, target):
                            M.add_edge(source, target, count=0)
                        else:
                            M[source][target]['count'] += 1

    #TODO - keeping only the highest count, for now
    for n in M:
        succ=sorted(M.out_edges(n,data='count'),key=lambda x: x[2],reverse=True)
        if len(succ)>1:
            M.remove_edges_from(succ[1:])

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
            else:
                points[a][cc] = -1

    a = full_info_aspects[0]['id']
    g = full_info_aspects[0]['geom']
    paths = [[{'geom': m[0],
               'id': m[1],
               'x': a,
               'y': points[a][m[1]]}, ]
             for m in M if m[0] == g
             if m[1] in points[a]]

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
                    to_add.append(current+[{
                        'geom': last['geom'],
                        'id':last['id'],
                        'x':a,
                        'y':points[a][last['id']]
                    }, ])
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
    tempPaths = []
    clustersByPath = []
    for i, p in enumerate(paths):
        newPath = {}
        newCluster = {}
        for step in p:
            newPath[step['x']] = step['y']
            newCluster[step['x']] = step['id']
        tempPaths.append(newPath)
        clustersByPath.append(newCluster)

    if len(tempPaths) > nClusters:
        a2i = {A['id']: A['order'] for A in full_info_aspects}
        X = np.zeros((len(tempPaths), len(full_info_aspects)))
        for i, p in enumerate(tempPaths):
            for a in p:
                X[i, a2i[a]] = p[a]
        Y = KMeans(n_clusters=nClusters).fit_predict(X).tolist()
    else:
        Y = [i for i in range(len(tempPaths))]

    for g in cl:
        for n in cl[g]:
            cl[g][n] = set()

    retPaths = [{} for _ in range(nClusters)]
    aspects = [a['id'] for a in full_info_aspects]

    for i, p in enumerate(tempPaths):
        for a in p:
            g = ds.getGeometry(a)
            cc = clustersByPath[i][a]
            # WRONG!!!
            # Get the paths following the CrossGeometry, not just the clusters.
            for n in cc2n[g][cc]:
                cl[g][n].add(Y[i])

        # TODO better paths
        retPaths[Y[i]] = _mergePaths(retPaths[Y[i]], p, Y[i])

        for a in aspects:
            if a not in retPaths[Y[i]]:
                retPaths[Y[i]][a] = -1

    path_hist = {}
    aspect_hist = {}
    # histograms for each aspect/cluster
    for a in aspects:
        N = len(ds.getColumns(a))
        aspect_hist[a] = [np.zeros(NBINS) for _ in range(N)]
        path_hist[a] = [[np.zeros(NBINS) for _ in range(N)]
                        for _ in range(nClusters)]


        vMax = np.empty(N)
        vMax[:] = np.nan

        g = ds.getGeometry(a)
        allVals = [[] for _ in range(nClusters)]
        for n in cl[g]:
            vals = ds.getData(a, n)
            if vals is not None:
                for cc in cl[g][n]:
                    sA = np.sum(vals)
                    if sA > 0:
                        vals = vals/sA
                    allVals[cc].append(vals)

        for cc in range(nClusters):
            vals = np.array(allVals[cc])
            if vals.shape[0] == 0:  # nothing in here (?)
                continue
            for col in range(N):
                tH, _ = np.histogram(np.squeeze(
                    vals[:, col]), bins=NBINS, range=(0, 1))
                aspect_hist[a][col] = aspect_hist[a][col]+tH
                path_hist[a][cc][col] = path_hist[a][cc][col]+tH

        minP = 0
        maxP = 0
        for col in range(N):
            aspect_hist[a][col] = aspect_hist[a][col].tolist()
            for cc in range(nClusters):
                path_hist[a][cc][col] = path_hist[a][cc][col].tolist()
                minP = np.min([minP, np.min(path_hist[a][cc][col])])
                maxP = np.max([maxP, np.max(path_hist[a][cc][col])])

    for g in cl:
        for n in cl[g]:
            if len(cl[g][n]) == 0:
                cl[g][n] = []
            else:
                # TODO order and pass the whole thing
                cl[g][n] = list(cl[g][n])[0]

    return({'clustering': cl,
            'evolution': retPaths,
            'hist': {'aspect': aspect_hist, 'path': path_hist},
            'aspects': full_info_aspects,
            'nclusters': nClusters})


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

        return(_mapHiers(ds, sorted(to_use), nClusters=nc, bbox=bbox))

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

    to_use = ['0019481a-63bf-493d-8e18-a1c6c8ef01cb', '020cbd0c-40e7-47d9-aa70-656036700e9c']#, '24763a5f-bacf-4d98-ad9d-c29a56878da0', '2483230c-ef8a-4a51-b206-e0f35c79a383', '37bf5584-d1e5-42ee-80f6-351f5fd2a484', '3beee586-5670-412c-bbed-98335c9237af', '40510cfd-ccbb-4651-83c1-15bbe3e0d3e2', '4458f9fe-13ca-4d95-8d3f-575525e78887', '49ee87db-7a3e-4256-8f65-15ef59738367', '4ea664be-8e3f-4d0c-a597-1a0c008aaa81', '5a430fae-4a61-4282-ae26-362461b34be0',
            #   '898d8b39-1c8c-4f1c-ac1b-5f408f2cbc0d', '95d2566e-cb0f-4242-98b8-0fc4b203b1e6', 'a5821660-d3fd-4fed-be40-5ac518cd5267', 'acc5e333-f167-4bb9-a061-497ae0d961a2', 'b84181aa-62d4-4621-9e30-c39a38156877', 'b9b3226f-0792-4dfa-b73b-d6311032c222', 'e3bc4825-2e47-4eec-9f63-f085ec79e763', 'e3cbdf8d-ac9d-426a-aabf-e028e17482b9', 'e980de5a-76c2-4d72-b70d-61d41e753409', 'f9689b58-efd6-4394-8d68-b46c47ae711e', 'f9aeec6f-9df7-459a-9aa6-f8a2332f7e37']
    _mapHiers(ds, sorted(to_use))
    exit()

    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)
    cherrypy.server.max_request_body_size = 0  # for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
