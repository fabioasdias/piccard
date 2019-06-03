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
from random import sample

import matplotlib.pylab as plt

from tqdm import tqdm

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


# @memory.cache(ignore=['ds'])
def _mapHiers(ds: dataStore, aspects: list, thresholds: list):
    Gs = mapHierarchies(ds, aspects)

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
    cluster_evolution = []

    for g in Gs:
        cl[g] = {}
        for n in Gs[g]:
            cl[g][n[1]] = []

    full_info_aspects = [{'name': ds.getAspectName(a),
                          'year': ds.getAspectYear(a),
                          'geom': ds.getGeometry(a),
                          'cols': ds.getColumns(a),
                          'id': a,
                          'descr': ds.getDescriptions_AsDict(a)}
                         for a in aspects]

    full_info_aspects = sorted(full_info_aspects, key=lambda x: x['year'])

    geoms = sorted(list(Gs.keys()))

    for threshold in thresholds:
        cc2n = {}
        for g in geoms:
            divider = [e[:2]
                       for e in Gs[g].edges(data='level')
                       if (e[2] > threshold)]
            Gs[g].remove_edges_from(divider)
            cc2n[g] = {}
            for cc, nodes in enumerate(nx.connected_components(Gs[g])):
                cc2n[g][cc] = [n[1] for n in nodes]
                for n in nodes:
                    cl[g][n[1]].append(cc)

        M = nx.DiGraph()
        for g1 in geoms:
            for g2 in geoms:
                if (g1 != g2):
                    X = ds.getCrossGeometry(g1, g2)
                    for n in cl[g1]:
                        source = (g1, cl[g1][n][-1])
                        # area = sum([e[2] for e in X.edges(source,data='intersection')])
                        if (source not in M):
                            M.add_node(source)
                        if 'area' not in M.node[source]:
                            M.node[source]['area'] = {}
                        if g2 not in M.node[source]['area']:
                            M.node[source]['area'][g2] = 0

                        for nn in X.neighbors((g1, n)):
                            intersection = X[(g1, n)][nn]['intersection']
                            M.node[source]['area'][g2] += intersection
                            target = (g2, cl[g2][nn[1]][-1])
                            if not target in M:
                                M.add_node(target)
                            if not M.has_edge(source, target):
                                M.add_edge(source, target, area=0)
                            M[source][target]['area'] += intersection

        for e in M.edges():
            if e[1][0] in M.node[e[0]]['area']:
                M[e[0]][e[1]]['area'] /= M.node[e[0]]['area'][e[1][0]]

        #keeps only the highest sucessor for each geometry
        for n in M:
            to_remove=[]
            picks = {}
            for nn in M.successors(n):
                cval = M[n][nn]['area']
                g = nn[0]
                if g not in picks:
                    picks[g]=(nn, cval)
                else:
                    if cval > picks[g][1]:
                        to_remove.append((n,picks[g][0]))
                        picks[g]=(nn, cval)
                    else:
                        to_remove.append((n,nn))
            M.remove_edges_from(to_remove)


        points = {}
        for info in full_info_aspects:
            a = info['id']
            g = info['geom']
            points[a] = {}
            for cc in cc2n[g]:
                points[a][cc] = np.median(
                    [x for x in [ds.getProjection(a, id) for id in cc2n[g][cc]] if (x is not None)])

        
        paths = [[n, ] for n in M if n[0] == full_info_aspects[0]['geom']]
        print('pre',len(paths))
        lines = [[points[full_info_aspects[0]['id']][n[0][1]],] for n in paths]
        done =[]
        dlines=[]
        assert(len(paths)==len(lines))
        for info in full_info_aspects[1:]:
            g = info['geom']
            a = info['id']
            to_add = []
            new_lines=[]
            unused=set([n[1] for n in M if n[0]==g])
            while paths:
                current = paths.pop(0)
                cline = lines.pop(0)
                if current[-1][0]==g: #same geometry:
                    to_add.append(current+[current[-1],])
                    new_lines.append(cline+[points[a][current[-1][1]],])
                    unused.discard(current[-1][1])
                else:
                    options = [n for n in M.successors(current[-1]) if n[0] == g]
                    if not options:
                        done.append(current)
                        dlines.append(cline)
                    for op in options:
                        to_add.append(current+[op, ])
                        new_lines.append(cline+[points[a][op[1]]])
                        unused.discard(op[1])
            #puts in the paths that didn't start at the first aspect
            paths = to_add+[[(g,x),] for x in unused]
            lines = new_lines+[[points[a][x],] for x in unused]

        plt.figure()
        for l in lines:
            plt.plot(l)
        plt.show()

        plt.show()

        exit()


        # for n in M:
        #     MM = nx.subgraph(M,[n,]+list(M.neighbors(n)))
        #     E = list(MM.edges())
        #     W = [2*M[e[0]][e[1]]['area'] for e in E]
        #     if all([x>0.75 for x in W]):
        #         continue

        #     pos = nx.spring_layout(MM)
        #     print('pos done')
        #     nx.draw_networkx_nodes(MM, pos=pos)
        #     nx.draw_networkx_edges(MM, pos=pos, edgelist=E, width=W, edge_color='grey')
        #     nx.draw_networkx_labels(MM, pos=pos)
        #     nx.draw_networkx_edge_labels(MM,pos=pos,edge_labels={e:'{0}'.format(round(MM[e[0]][e[1]]['area'],2)) for e in MM.edges()})
        #     plt.show()

    return({'clustering': cl, 'evolution': cluster_evolution})


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

        thresholds: list = [0.999, 0.75, 0.5]
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
    if (len(sys.argv)) > 2:
        print(".py [conf.json]")
        exit(-1)
    if len(sys.argv)==1:
        confFile='conf.json'        
    else:
        confFile=sys.argv[1]

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
    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)
    cherrypy.server.max_request_body_size = 0  # for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
