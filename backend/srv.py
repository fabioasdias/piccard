"""Server module for the backend"""
from collections import defaultdict
from itertools import product
import json
from os import makedirs, getcwd
from os.path import exists, join, abspath
import sys
import tempfile

import cherrypy
from joblib import Memory
import matplotlib.pylab as plt
import networkx as nx
import numpy as np
# from clustering import NBINS
import pandas as pd

from dataStore import dataStore
from hierarchies import mapHierarchies
from upload import gatherInfoJsons, processUploadFolder
from scipy.spatial.distance import euclidean

cachedir = './cache/'
if not exists(cachedir):
    makedirs(cachedir)
memory = Memory(cachedir, verbose=20000)

SQR2 = np.sqrt(2.0)
DEBUG = False

# {'_sw': {'lng': -97.36262426260146, 'lat': 24.36091074100848}, '_ne': {'lng': -65.39166177011971, 'lat': 33.61501866716327}}


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


def _convert_name_node(n: tuple, y: int) -> tuple:
    """ (geom,id) -> (year, geom, id)"""
    return((y, n[0], n[1]))


def _convert_name_graph(G: nx.Graph, y: int) -> nx.Graph:
    """ Adds y to the names of the graphs nodes (geom,id) -> (year, geom, id)"""
    ret = nx.Graph()
    for n in G:
        ret.add_node(_convert_name_node(n, y))
    for e in G.edges():
        n1 = _convert_name_node(e[0], y)
        n2 = _convert_name_node(e[1], y)
        ret.add_edge(n1, n2)
        for k in G[e[0]][e[1]].keys():
            ret[n1][n2][k] = G[e[0]][e[1]][k]

    return(ret)


def _convert_cross(X: nx.Graph, y1: int, g1: str, y2: int, g2: str) -> nx.Graph:
    """Converts the names of the nodes of a cross graph. It's more difficult because 
    it contains stuff from two different geoms, so if it matches g1, gets y1, otherwise y2.
    (that way it works even g1==g2)"""
    ret = nx.Graph()
    for n in X:
        if n[0] == g1:
            ret.add_node(_convert_name_node(n, y1))
        else:
            ret.add_node(_convert_name_node(n, y2))

    for e in X.edges():
        if e[0][0] == g1:
            n1 = _convert_name_node(e[0], y1)
            n2 = _convert_name_node(e[1], y2)
        else:
            n1 = _convert_name_node(e[0], y2)
            n2 = _convert_name_node(e[1], y1)
        ret.add_edge(n1, n2)
    return(ret)


@memory.cache(ignore=['ds', ])
def _mapHiers(ds: dataStore, aspects: list, nClusters: int = 10, bbox: list = None):

    Gs = mapHierarchies(ds, aspects, bbox=bbox)

    right_order = sorted(Gs.keys())
    G = nx.Graph()
    lastGeom = None
    lastY = 0
    for y, g in right_order:
        print('\n\nadding ', y, g)
        nG = _convert_name_graph(Gs[(y, g)], y)
        G = nx.compose(G, nG)
        print('E,V', len(G), len(G.edges()))
        if lastGeom is None:
            lastGeom = g
            lastY = y
            continue

        print(list(G)[0], list(nG)[0])
        X = _convert_cross(ds.getCrossGeometry(
            lastGeom, g), y, g, lastY, lastGeom)

        values_added = 0
        zero_neighbors = 0
        not_contained = 0
        for n1, n2 in X.edges():

            if (n1 in G) and (n2 in G):

                # minT = 2
                # maxT = -1
                neighbouring_connections = []
                for nn1 in G.neighbors(n1):
                    if (nn1[:2] != n1[:2]):
                        continue
                    for nn2 in G.neighbors(n2):
                        if (nn2[:2] != n2[:2]):
                            continue
                        if X.has_edge(nn1, nn2):
                            neighbouring_connections.append([nn1, nn2])

                if len(neighbouring_connections) == 0:
                    zero_neighbors += 1
                    continue

                values = []
                for nn1, nn2 in neighbouring_connections:
                    values.append(
                        euclidean(G[n1][nn1]['hist'], G[n2][nn2]['hist'])/SQR2)
                G.add_edge(n1, n2, level=np.max(values))
                values_added += 1
            else:
                not_contained += 1
        print('E,V', len(G), len(G.edges()))
        print('values added', values_added, zero_neighbors, not_contained)
        print('last', lastY, lastGeom, 'current', y, g)
        lastGeom = g
        lastY = y

    del(Gs)

    full_info_aspects = [{'name': ds.getAspectName(a),
                          'year': ds.getAspectYear(a),
                          'geom': ds.getGeometry(a),
                          'cols': ds.getColumns(a),
                          'id': a,
                          'visible': True,
                          'descr': ds.getDescriptions_AsDict(a)}
                         for a in aspects]

    full_info_aspects = sorted(full_info_aspects, key=lambda x: x['year'])

    for i in range(len(full_info_aspects)):
        full_info_aspects[i]['order'] = i

    # -----------------------------------
    # cutting the hierarchy

    base_number_ccs = nx.number_connected_components(G)
    current_number_ccs = base_number_ccs

    vals = [e[2] for e in G.edges(data='level')]
    s = np.std(vals)
    m = np.mean(vals)
    T = m #+ s
    print('Threshold ', T, m, s, np.max(vals), np.min(vals))
    # plt.hist(vals)
    # plt.show()

    G.remove_edges_from([e[:2] for e in G.edges(data='level') if e[2] >= T])
    print('end #CC', nx.number_connected_components(G))
    E = sorted([e for e in G.edges(data='level')],
               key=lambda e: e[2], reverse=True)
    while (current_number_ccs-base_number_ccs) < nClusters:
        cutoff = nClusters-(base_number_ccs-base_number_ccs)
        G.remove_edges_from(E[:cutoff])
        E = E[cutoff:]
        current_number_ccs = nx.number_connected_components(G)
        print('current #CC', current_number_ccs, len(G.edges()))
    print('final #CC', current_number_ccs)

    cl = defaultdict(lambda: defaultdict(dict))
    for cc, nodes in enumerate(nx.connected_components(G)):
        for n in nodes:
            cl[n[0]][n[1]][n[2]] = cc

    # ----------------------------------------------------------------------------
    # # computing the relevances for each cluster in each aspect and the histograms
    # most_relevant_column = defaultdict(dict)
    # aspect_hist = dict()
    # cc_hist = defaultdict(dict)

    # for aspect in tqdm(full_info_aspects, desc='histograms'):
    #     a = aspect['id']
    #     g = aspect['geom']
    #     y = aspect['year']
    #     data = defaultdict(list)
    #     N = ds.getDimension(a)
    #     for n in tqdm(cl[y][g], desc='reading'):
    #         vals = ds.getData(a, n, normalized=True)
    #         if (vals is None) or np.any(np.isnan(vals)):
    #             continue
    #         data[cl[y][g][n]].append(vals)

    #     H = defaultdict(dict)
    #     for cc in data:
    #         data[cc] = np.array(data[cc])
    #         for j in range(data[cc].shape[1]):
    #             # H[j][cc], _ = np.histogram(np.squeeze(data[cc][:, j]), NBINS, range=(
    #             #     ds.getMinima(a)[j], ds.getMaxima(a)[j]))
    #             H[j][cc], _ = np.histogram(np.squeeze(
    #                 data[cc][:, j]), NBINS, range=(0, 1))
    #         cc_hist[a][cc] = [H[j][cc] for j in H]

    #     aspect_hist[a] = [np.squeeze(
    #         np.sum([cc_hist[a][cc][j] for cc in cc_hist[a]], axis=0)).tolist() for j in H]
    #     for cc in cc_hist[a]:
    #         cc_hist[a][cc] = [np.squeeze(x).tolist() for x in cc_hist[a][cc]]

    #     # if scalar value, just use the median
    #     if N == 1:
    #         for cc in data:
    #             most_relevant_column[cc][a] = np.median(data[cc])
    #         continue
    #     else:
    #         D = defaultdict(dict)
    #         for j in H:
    #             for cc in H[j]:
    #                 D[j][cc] = _centerMass(
    #                     cc_hist[a][cc][j]) - _centerMass(aspect_hist[a][j])

    #         for cc in data:
    #             cur_max = 0
    #             max_j = -1
    #             for j in D:
    #                 current_relevance = D[j][cc]
    #                 if cur_max < current_relevance:
    #                     cur_max = current_relevance
    #                     max_j = j
    #             # the ccs are consistent across geoms now
    #             most_relevant_column[cc][a] = max_j

    # print('exporting evolution lines')
    # evo = []
    # for cc in tqdm(most_relevant_column, desc='cc'):
    #     line = {a: most_relevant_column[cc][a]
    #             for a in most_relevant_column[cc]}
    #     line['id'] = cc
    #     evo.append(line)

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

    # print(cl.keys())

    return({'clustering': dict(cl),
            'evolution': [],  # evo,
            # 'hist': {'aspect': aspect_hist, 'cc': cc_hist},
            'hist': {'aspect': {}, 'cc': {}},
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
            bbox = _bbox_create_buffer(input_json['bbox'])

        bbox = [-88.0, 41.0, -87.0, 43.0]

        if ('nc' not in input_json):
            nc = 10
        else:
            nc = int(input_json['nc'])
        if to_use:
            res = _mapHiers(ds, sorted(to_use), nClusters=nc, bbox=bbox)
            print(res['nclusters'])
            return(res)
        else:
            return({})

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
            fname = join(str(tempDir), myFile.filename)
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
            'tools.staticdir.root': abspath(getcwd()),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*', 'application/*']
        },
        # '/public': {
        #     'tools.staticdir.on': True,
        #     'tools.staticdir.dir': './public'
        # }
    }

    # to_use = ['0db8b31e-2d85-4eb2-bfb2-e35abe730365', '35361c33-22ca-4911-8d33-8e4a0d4f2cce',
    #           '65cc1fd1-67b4-44cf-b627-b2639bce1f72', '9534ca6d-202e-4a20-a135-b0dd4f007378',
    #           'ec000dbe-958c-48d3-af62-78ccc8bf4152', '22bcd574-f533-4aec-8d7a-e2bdd3e86556',
    #           '3e5477cd-9369-4e08-b398-b385c2ffb0e2', ]
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
