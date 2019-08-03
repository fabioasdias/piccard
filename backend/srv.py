"""Server module for the backend"""
import json
import os
import pickle
import sys
import tempfile
from collections import defaultdict
from itertools import combinations
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
from scipy.spatial.distance import cosine, euclidean
# from scipy.stats import wasserstein_distance,
from sklearn.cluster import KMeans
from tqdm import tqdm

from dataStore import dataStore
from hierarchies import compareHierarchies, mapHierarchies
from upload import gatherInfoJsons, processUploadFolder

cachedir = './cache/'
if not exists(cachedir):
    makedirs(cachedir)
memory = Memory(cachedir, verbose=0)

# same as in clustering.py! - There is probably a better way...
NBINS = 100

DEBUG = False


def _centerMass(V):
    return(np.mean([(i*V[i])/np.sum(V) for i in range(len(V))]))


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


@memory.cache(ignore=['ds'])
# @profile
def _mapHiers(ds: dataStore, aspects: list, nClusters: int = 10, threshold: float = 0.65, bbox: list = None):

    Gs = mapHierarchies(ds, aspects, bbox=bbox)

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

    cl = defaultdict(lambda: defaultdict(dict))
    # -----------------------------------
    # cutting the hierarchies

    for yg in tqdm(Gs):
        y, g = yg

        base_number_ccs = nx.number_connected_components(Gs[yg])
        Gs[yg].remove_edges_from([e[:2]
                                  for e in Gs[yg].edges(data='level')
                                  if e[2] >= threshold])
        current_number_ccs = nx.number_connected_components(Gs[yg])
        while (current_number_ccs-base_number_ccs) < nClusters:
            E = sorted([e for e in Gs[yg].edges(data='level')],
                       key=lambda e: e[2], reverse=True)
            Gs[yg].remove_edges_from(
                E[:nClusters-(base_number_ccs-base_number_ccs)])
            current_number_ccs = nx.number_connected_components(Gs[yg])

        for cc, nodes in enumerate(nx.connected_components(Gs[yg])):
            for n in nodes:
                cl[y][g][n[1]] = cc

        # # # -------------------------------------------
        # # # Merging disconnected similar clusters

        aspects_in_this_year_geom = [a 
                                for a in full_info_aspects 
                                if (a['geom'] == g) and (a['year'] == y)]
        nDims = [ds.getDimension(a['id']) for a in aspects_in_this_year_geom]
        singleVar = [x == 1 for x in nDims]
        # fixes the histogram size for scalar variables
        nDims = [x if x > 1 else NBINS for x in nDims]
        M = np.zeros((current_number_ccs, np.sum(nDims)))
        for i, aspect in enumerate(aspects_in_this_year_geom):
            a = aspect['id']
            y = aspect['year']

            if i == 0:
                start = 0
            else:
                start = sum(nDims[:i])
            finish = start+nDims[i]

            for n in tqdm(cl[y][g], desc=ds.getAspectName(a)):
                vals = ds.getData(a, n)
                cc = cl[y][g][n]
                if (vals is None) or np.any(np.isnan(vals)):
                    continue
                if singleVar[i]:
                    tempH, _ = np.histogram(vals, NBINS, range=(
                        ds.getMinima(a)[0], ds.getMaxima(a)[0]))
                else:
                    tempH = np.array(vals)

                M[cc, start:finish] += tempH

            # normalizing each section
            with np.errstate(divide='ignore', invalid='ignore'):
                M[:, start:finish] = (
                    M[:, start:finish].T / np.sum(M[:, start:finish], axis=1)).T

        M = np.nan_to_num(M)
        km = KMeans(n_clusters=nClusters).fit(M)
        del(M)
        for n in cl[y][g]:
            cl[y][g][n] = int(km.labels_[cl[y][g][n]])

    # ----------------------------------------------------------
    # Match the clusters across the geometries

    for i in tqdm(range(1, len(full_info_aspects)), 'paths'):
        a_from = full_info_aspects[i-1]
        a_to = full_info_aspects[i]
        g_from = a_from['geom']
        y_from = a_from['year']
        g_to = a_to['geom']
        y_to = a_to['year']

        M = nx.DiGraph()
        # let's make sure all clusters are represented
        for cc in set(cl[y_from][g_from].values()):
            M.add_node((g_from, cc))
        for cc in set(cl[y_to][g_to].values()):
            M.add_node((g_to, cc))

        X = ds.getCrossGeometry(a_from['geom'], a_to['geom'])
        for e in X.edges():
            g0 = e[0][0]
            id0 = e[0][1]
            g1 = e[1][0]
            id1 = e[1][1]
            if g0 == g_from:
                if ((y_from not in cl) or (g0 not in cl[y_from]) or (id0 not in cl[y_from][g0]) or
                        (y_to not in cl) or (g1 not in cl[y_to]) or (id1 not in cl[y_to][g1])):
                    continue

                source = (g0, cl[y_from][g_from][id0])
                target = (g1, cl[y_to][g_to][id1])
            else:
                if ((y_from not in cl) or (g1 not in cl[y_from]) or (id1 not in cl[y_from][g1]) or
                        (y_to not in cl) or (g0 not in cl[y_to]) or (id0 not in cl[y_to][g0])):
                    continue

                source = (g1, cl[y_from][g_from][id1])
                target = (g0, cl[y_to][g_to][id0])

            if not M.has_edge(source, target):
                M.add_edge(source, target, count=0)

            M[source][target]['count'] += X[e[0]][e[1]]['intersection']

        if DEBUG:
            pos = nx.spring_layout(M)
            nx.draw_networkx_nodes(M, pos)
            E = M.edges()
            # maxWidth = np.log(max([e[2] for e in M.edges(data='count')]))
            maxWidth = max([e[2] for e in M.edges(data='count')])
            # nx.draw_networkx_edges(M, pos, edgelist=E, width=[
            #                     5*(np.log(M[e[0]][e[1]]['count'])/maxWidth)+0.2 for e in E])
            nx.draw_networkx_edges(M, pos, edgelist=E, width=[
                5*(M[e[0]][e[1]]['count'])/maxWidth+0.1 for e in E])

            nx.draw_networkx_labels(
                M, pos, labels={n: '{0}-{1}'.format(n[0], n[1]) for n in M}, font_color='green')

        # matching the clusters temporally based on how strongly connected they are
        # the temporal part comes from the aspect order used to extract the paths
        to_look = [n for n in M if M.in_degree(n) > 1 or M.out_degree(n) > 1]
        used = {e: False for e in M.edges()}
        while to_look:
            # print(len(to_look), set([M.in_degree(n) for n in M]), set(
                # [M.out_degree(n) for n in M]))
            E = sorted([e for e in M.edges(data='count') if not used[e[:2]]],
                       key=lambda e: e[2]/max([ee[2] for ee in M.out_edges(e[0], data='count')] +
                                              [ee[2] for ee in M.in_edges(e[1], data='count')]), reverse=True)
            if not E:
                break

            m = E[0][0]
            n = E[0][1]
            used[(m, n)] = True
            to_remove = [[n, m], ]  # removes the link back, if it exists
            for p in M.predecessors(n):
                if p != m:
                    to_remove.append([p, n])
            for s in M.successors(m):
                if s != n:
                    to_remove.append([m, s])
            M.remove_edges_from(to_remove)
            to_look = [n
                       for n in M
                       if M.in_degree(n) > 1 or M.out_degree(n) > 1]

        if DEBUG:
            plt.figure()
            nx.draw(M, pos)
            nx.draw_networkx_labels(
                M, pos, labels={n: '{0}-{1}'.format(n[0], n[1]) for n in M}, font_color='green')
            plt.show()

        labels = {}
        maxCC = max(cl[y_from][g_from].values())+1
        for n_from, n_to in M.edges():
            labels[n_to[1]] = n_from[1]
        for i, cc in enumerate(set(cl[y_to][g_to].values())-set(labels.keys())):
            labels[cc] = i+maxCC

        for id_to in cl[y_to][g_to]:
            cl[y_to][g_to][id_to] = labels[cl[y_to][g_to][id_to]]

        # labels = defaultdict(dict)
        # sinks = [n for n in M if len(list(M.out_edges(n))) == 0]
        # used = {n: False for n in M}
        # for i, s in enumerate(sinks):
        #     to_do = [s, ]
        #     while to_do:
        #         n = to_do.pop(0)
        #         if used[n]:
        #             continue
        #         used[n] = True
        #         labels[n[0]][n[1]] = i  # n[i] -> cc
        #         to_do.extend(list(M.predecessors(n)))

        # maxCC = len(sinks)
        # for g in cl:
        #     for n in cl[g]:
        #         cc = labels[g][cl[g][n]]
        #         cl[g][n] = cc
        #         # maxCC = max([maxCC, cl[g][n]])
    # ----------------------------------------------------------------------------
    # computing the relevances for each cluster in each aspect and the histograms
    most_relevant_column = defaultdict(dict)
    aspect_hist = dict()
    cc_hist = defaultdict(dict)

    for aspect in tqdm(full_info_aspects, desc='histograms'):
        a = aspect['id']
        g = aspect['geom']
        y = aspect['year']
        data = defaultdict(list)
        N = ds.getDimension(a)
        for n in tqdm(cl[y][g], desc='reading'):
            vals = ds.getData(a, n, normalized=True)
            if (vals is None) or np.any(np.isnan(vals)):
                continue
            data[cl[y][g][n]].append(vals)

        H = defaultdict(dict)
        for cc in data:
            data[cc] = np.array(data[cc])
            for j in range(data[cc].shape[1]):
                # H[j][cc], _ = np.histogram(np.squeeze(data[cc][:, j]), NBINS, range=(
                #     ds.getMinima(a)[j], ds.getMaxima(a)[j]))
                H[j][cc], _ = np.histogram(np.squeeze(
                    data[cc][:, j]), NBINS, range=(0, 1))
            cc_hist[a][cc] = [H[j][cc] for j in H]

        aspect_hist[a] = [np.squeeze(
            np.sum([cc_hist[a][cc][j] for cc in cc_hist[a]], axis=0)).tolist() for j in H]
        for cc in cc_hist[a]:
            cc_hist[a][cc] = [np.squeeze(x).tolist() for x in cc_hist[a][cc]]

        # if scalar value, just use the median
        if N == 1:
            for cc in data:
                most_relevant_column[cc][a] = np.median(data[cc])
            continue
        else:
            D = defaultdict(dict)
            for j in H:
                for cc in H[j]:
                    D[j][cc] = _centerMass(
                        cc_hist[a][cc][j]) - _centerMass(aspect_hist[a][j])

            for cc in data:
                cur_max = 0
                max_j = -1
                for j in D:
                    current_relevance = D[j][cc]
                    if cur_max < current_relevance:
                        cur_max = current_relevance
                        max_j = j
                # the ccs are consistent across geoms now
                most_relevant_column[cc][a] = max_j

    print('exporting evolution lines')
    evo = []
    for cc in tqdm(most_relevant_column, desc='cc'):
        line = {a: most_relevant_column[cc][a]
                for a in most_relevant_column[cc]}
        line['id'] = cc
        evo.append(line)

    # # ----------------------------------------------------------
    # # filling up the forest - weight == similarity
    # years=sorted(set([a['year'] for a in full_info_aspects]))
    # for n in forest:
    #     forest.node[n]['ideal_x']=n[1]/(maxCC+1)
    #     forest.node[n]['ideal_y']=years.index(n[0])/len(years)

    # for n1, n2 in forest.edges():
    #     if n1[1] == n2[1]:
    #         forest[n1][n2]['weight']=0.5
    #     else:
    #         forest[n1][n2]['weight']=0
    #     vals=[e[2] for e in forest.in_edges(
    #         n1, data='count')]+[e[2] for e in forest.out_edges(n1, data='count')]
    #     if vals:
    #         maxVal=max(vals)
    #         if maxVal > 0:
    #             forest[n1][n2]['weight'] += forest[n1][n2]['count']/(2*maxVal)
    #             continue

    # for y in tqdm(years, desc='forest'):
    #     edges_to_use=list(combinations(
    #         [n for n in forest if (n[0] == y)], 2))

    #     for n1, n2 in edges_to_use:
    #         cc1=n1[1]
    #         cc2=n2[1]
    #         useful_aspects=[a['id']
    #                           for a in full_info_aspects
    #                           if (a['year'] == y) and
    #                           (a['id'] in most_relevant_column[cc1]) and
    #                           (a['id'] in most_relevant_column[cc2])]
    #         if not useful_aspects:  # this cc might not be present in this year
    #             continue
    #         if (not forest.has_edge(n1, n2)) or ('weight' not in forest[n1][n2]):
    #             forest.add_edge(n1,
    #                             n2,
    #                             weight=np.sum([1 for a in useful_aspects
    #                                            if (most_relevant_column[cc1][a] == most_relevant_column[cc2][a])]) / len(useful_aspects))

    # to_remove=[]
    # for e in forest.edges():
    #     # or (geoms[geoms.index(e[0][0])]!=e[1][0]):#non-yearly consecutive geoms #TODO
    #     if np.isclose(forest[e[0]][e[1]]['weight'], 0):
    #         to_remove.append(e)
    # forest.remove_edges_from(to_remove)

    # forest_out=nx.DiGraph()
    # n2i={n: i for i, n in enumerate(forest.nodes())}
    # for n in forest:
    #     i=n2i[n]
    #     forest_out.add_node(i)
    #     forest_out.node[i]['year']=n[0]
    #     forest_out.node[i]['cc']=n[1]
    #     forest_out.node[i]['geoms']=list(forest.node[n]['geoms'])
    #     forest_out.node[i]['ideal_x']=forest.node[n]['ideal_x']
    #     forest_out.node[i]['ideal_y']=forest.node[n]['ideal_y']
    # for n1, n2, w in forest.edges(data='weight'):
    #     forest_out.add_edge(n2i[n1], n2i[n2], weight=w)

    # forest_json=json_graph.node_link_data(forest_out)

    # pos = nx.spring_layout(forest_out)
    # nx.draw_networkx_nodes(forest_out, pos)
    # nx.draw_networkx_labels(forest_out, pos, labels={n: '{0}-{1}'.format(
    #     forest_out.node[n]['year'], forest_out.node[n]['cc']) for n in forest_out})
    # # if forest_out[e[0]][e[1]]['weight']>0.5]
    # E = [e for e in forest_out.edges()]
    # nx.draw_networkx_edges(forest_out, pos, edgelist=E, width=[
    #                        5*forest_out[e[0]][e[1]]['weight'] for e in E])
    # plt.show()

    # with open('forest.json', 'w') as fout:
    #     json.dump(forest_json, fout, indent=4, sort_keys=True)

    maxCC = 0
    for y in cl:
        for g in cl[y]:
            maxCC = max([maxCC, max(cl[y][g].values())])

    return({'clustering': {**(cl[1970]), **(cl[2010]), **(cl[2015])},
            'evolution': evo,
            'hist': {'aspect': aspect_hist, 'cc': cc_hist},
            'aspects': full_info_aspects,
            'forest':  {'nodes': [], 'links': []},  # forest_json,
            'nclusters': maxCC+1})  # 0....9 ->10


@cherrypy.expose
class server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip()
    def availableGeometries(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret = []
        for g in available_geometries:
            ret.append({'name': g['name'],
                        'url': g['url'],
                        'source': g['source'],
                        'year': g['year']
                        })
        return(ret)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getRawData(self):
        ret = []
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        sourceGeom = input_json['geom']
        g = geom_by_source[sourceGeom]['name']
        rid = input_json['props'][geom_by_source[sourceGeom]['id_field']]
        used_aspects = input_json['aspects']
        useful_aspects = [a for a in used_aspects if ds.getGeometry(a) == g]
        print(useful_aspects, rid, g)
        for a in useful_aspects:
            entry = {'id': a,
                     'name': ds.getAspectName(a),
                     'vals': {}}
            vals = ds.getData(a, rid)
            for i, c in enumerate(ds.getDescriptions_AsList(a)):
                entry['vals'][c] = vals[i]
            ret.append(entry)
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
            # {'_sw': {'lng': -97.36262426260146, 'lat': 24.36091074100848}, '_ne': {'lng': -65.39166177011971, 'lat': 33.61501866716327}}
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

    geom_by_source = {g['source']: g for g in available_geometries}

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

    # # to_use = ['01484bfd-d853-4bc4-b5d4-7724102491f0',
    # #           '23c57e64-e4d9-4fa8-8511-bf5541290eed',
    # #                        '2876df13-ed66-4361-81c6-1337320b4e22',
    # #                        '289c96f4-6463-4202-86c4-60f257eacdc6',
    # #                        '44f0e97d-7037-4e6f-ae71-3ced55d1ad17',
    # #                        '5412991b-e899-467a-b2eb-cd45ba91d5df',
    # #           '54279024-99f7-4db0-b6ed-c6f7d919ce76',
    # #                        '56158126-6589-4037-b7d3-bc8789d950b4',
    # #                        '597d682f-79ef-4781-b3b1-4ab025b0eb4f',
    # #                        '860eb9d4-260a-4824-b3af-f6b0a37c7168',
    # #                        '9089406c-61d4-40b6-9f72-101767f1e0dd',
    # #           'a_toe83ff8-6962-48aa-8740-3c250e8d3a_from3',
    # #             'a67ec8c4-0794-4862-a_toa4-b5ba9b5401df',
    # #             'b0d6c9b9-2935-4760-a394-68b791b12a_to2',
    # #             'b0f43c86-8bf7-4cdb-a_fromf4-0796f6e7b80a',
    # #             'c29fb848-8836-45df-8ef1-b78e57bf6ccf',
    # #           'd36bd0e0-d74d-4355-a967-31c357239646']

    # to_use = ['a67ec8c4-0794-4862-a2a4-b5ba9b5401df', '2876df13-ed66-4361-81c6-1337320b4e22',
    #           '56158126-6589-4037-b7d3-bc8789d950b4', 'b0f43c86-8bf7-4cdb-a1f4-0796f6e7b80a']
    # _mapHiers(ds, sorted(to_use))
    # exit()

    # input_json=[{"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"TES","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["TEST1"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"TES","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["TEST2"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"T3A","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["T3A","T3B","T3C"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"EYT","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["EYT001","EYT002","EYT003","EYT004","EYT005","EYT006","EYT007","EYT008","EYT009","EYT010","EYT011","EYT012","EYT013","EYT014","EYT015","EYT016","EYT017"]},
    #  {"enabled":True, "year":1990,"geometry":"US_CT_1990","name":"ET6","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["ET6001","ET6002","ET6003","ET6004","ET6005","ET6006","ET6007","ET6008","ET6009","ET6010"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"EUZ","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["EUZ001","EUZ002","EUZ003","EUZ004","EUZ005","EUZ006","EUZ007","EUZ008","EUZ009","EUZ010","EUZ011","EUZ012","EUZ013","EUZ014","EUZ015","EUZ016","EUZ017","EUZ018","EUZ019","EUZ020","EUZ021","EUZ022","EUZ023","EUZ024","EUZ025"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"ET5","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["ET5001","ET5002","ET5003","ET5004","ET5005","ET5006","ET5007","ET5008","ET5009","ET5010","ET5011","ET5012","ET5013","ET5014","ET5015","ET5016","ET5017","ET5018","ET5019","ET5020","ET5021","ET5022","ET5023","ET5024","ET5025","ET5026","ET5027","ET5028","ET5029","ET5030","ET5031","ET5032","ET5033","ET5034","ET5035","ET5036","ET5037","ET5038","ET5039","ET5040","ET5041","ET5042","ET5043","ET5044","ET5045","ET5046","ET5047","ET5048","ET5049","ET5050","ET5051","ET5052","ET5053","ET5054","ET5055","ET5056","ET5057","ET5058","ET5059","ET5060","ET5061","ET5062"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"E3C","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["E3C001","E3C002","E3C003","E3C004","E3C005","E3C006","E3C007","E3C008","E3C009","E3C010","E3C011","E3C012","E3C013","E3C014","E3C015","E3C016","E3C017","E3C018","E3C019","E3C020","E3C021","E3C022","E3C023","E3C024","E3C025","E3C026","E3C027","E3C028","E3C029","E3C030","E3C031","E3C032","E3C033","E3C034","E3C035","E3C036"]},
    #  {"enabled":True,"year":1990,"geometry":"US_CT_1990","name":"ET4","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["ET4001","ET4002","ET4003","ET4004","ET4005","ET4006","ET4007","ET4008","ET4009","ET4010","ET4011","ET4012","ET4013","ET4014","ET4015","ET4016","ET4017","ET4018","ET4019","ET4020","ET4021","ET4022","ET4023","ET4024","ET4025","ET4026","ET4027","ET4028","ET4029","ET4030","ET4031","ET4032","ET4033","ET4034","ET4035","ET4036","ET4037","ET4038","ET4039","ET4040","ET4041","ET4042","ET4043","ET4044","ET4045","ET4046","ET4047","ET4048","ET4049","ET4050","ET4051","ET4052","ET4053","ET4054","ET4055","ET4056","ET4057","ET4058","ET4059","ET4060","ET4061","ET4062","ET4063","ET4064","ET4065","ET4066","ET4067","ET4068","ET4069","ET4070","ET4071","ET4072","ET4073","ET4074","ET4075","ET4076","ET4077","ET4078","ET4079","ET4080","ET4081","ET4082","ET4083","ET4084","ET4085","ET4086","ET4087","ET4088","ET4089","ET4090","ET4091","ET4092","ET4093","ET4094","ET4095","ET4096","ET4097","ET4098","ET4099","ET4100","ET4101","ET4102","ET4103","ET4104","ET4105","ET4106","ET4107","ET4108","ET4109","ET4110","ET4111","ET4112","ET4113","ET4114","ET4115","ET4116","ET4117","ET4118","ET4119","ET4120","ET4121","ET4122","ET4123","ET4124","ET4125","ET4126","ET4127","ET4128","ET4129","ET4130","ET4131","ET4132","ET4133","ET4134","ET4135","ET4136","ET4137","ET4138","ET4139","ET4140","ET4141","ET4142","ET4143","ET4144","ET4145","ET4146","ET4147","ET4148","ET4149","ET4150","ET4151","ET4152","ET4153","ET4154","ET4155","ET4156","ET4157","ET4158","ET4159","ET4160","ET4161","ET4162","ET4163","ET4164","ET4165","ET4166","ET4167","ET4168","ET4169","ET4170","ET4171","ET4172","ET4173","ET4174","ET4175","ET4176","ET4177","ET4178","ET4179","ET4180","ET4181","ET4182","ET4183","ET4184","ET4185","ET4186","ET4187","ET4188","ET4189","ET4190","ET4191","ET4192","ET4193","ET4194","ET4195","ET4196","ET4197","ET4198","ET4199","ET4200","ET4201","ET4202","ET4203","ET4204","ET4205","ET4206","ET4207","ET4208","ET4209","ET4210","ET4211","ET4212","ET4213","ET4214","ET4215","ET4216","ET4217","ET4218","ET4219","ET4220","ET4221","ET4222","ET4223","ET4224","ET4225","ET4226","ET4227","ET4228","ET4229","ET4230","ET4231","ET4232","ET4233","ET4234","ET4235","ET4236","ET4237","ET4238","ET4239","ET4240","ET4241","ET4242","ET4243","ET4244","ET4245","ET4246","ET4247","ET4248","ET4249","ET4250","ET4251","ET4252","ET4253","ET4254","ET4255","ET4256","ET4257","ET4258","ET4259","ET4260","ET4261","ET4262","ET4263","ET4264","ET4265","ET4266","ET4267","ET4268","ET4269","ET4270","ET4271","ET4272","ET4273","ET4274","ET4275","ET4276","ET4277","ET4278","ET4279","ET4280","ET4281","ET4282","ET4283","ET4284","ET4285","ET4286","ET4287","ET4288","ET4289","ET4290","ET4291","ET4292","ET4293","ET4294","ET4295","ET4296","ET4297","ET4298","ET4299","ET4300","ET4301","ET4302","ET4303","ET4304","ET4305","ET4306","ET4307","ET4308","ET4309","ET4310"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"ESA","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["ESA001"]},
    #  {"enabled":False,"year":1990,"geometry":"US_CT_1990","name":"E33","fileID":"f044aef5-6f59-47f5-8832-f6afbcbe2c8f","index":"GISJOIN","columns":["E33001","E33002","E33003","E33004","E33005","E33006","E33007"]},]

    # ds.createAspect(input_json, dirconf['upload'])
    # exit()

    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)
    cherrypy.server.max_request_body_size = 0  # for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
