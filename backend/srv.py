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
from scipy.spatial.distance import cosine
from scipy.stats import wasserstein_distance
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
# @profile
def _mapHiers(ds: dataStore, aspects: list, nClusters: int = 10, bbox: list = None):

    Gs = mapHierarchies(ds, aspects, bbox=bbox)

    full_info_aspects = [{'name': ds.getAspectName(a),
                          'year': ds.getAspectYear(a),
                          'geom': ds.getGeometry(a),
                          'cols': ds.getColumns(a),
                          'id': a,
                          'visible': True,
                          'descr': ds.getDescriptions_AsDict(a)}
                         for a in aspects]

    geoms = []
    full_info_aspects = sorted(full_info_aspects, key=lambda x: x['year'])
    geoms = list(set([a['geom'] for a in full_info_aspects]))
    # preparations for the domains in ParallelCoordinates (react-vis)
    for i in range(len(full_info_aspects)):
        full_info_aspects[i]['order'] = i

    cl = defaultdict(dict)
    for g in tqdm(geoms):

        # -----------------------------------
        # cutting the hierarchy

        base_number_ccs = nx.number_connected_components(Gs[g])
        Gs[g].remove_edges_from(
            [e[:2] for e in Gs[g].edges(data='level') if e[2] >= 1])
        current_number_ccs = nx.number_connected_components(Gs[g])
        while (current_number_ccs-base_number_ccs) < nClusters:
            E = sorted([e for e in Gs[g].edges(data='level')],
                       key=lambda e: e[2], reverse=True)
            Gs[g].remove_edges_from(
                E[:nClusters-(base_number_ccs-base_number_ccs)])
            current_number_ccs = nx.number_connected_components(Gs[g])

        for cc, nodes in enumerate(nx.connected_components(Gs[g])):
            for n in nodes:
                cl[g][n[1]] = cc

        # -------------------------------------------
        # Merging disconnected similar clusters

        aspects_in_this_geom = [a for a in full_info_aspects if a['geom'] == g]
        nDims = [ds.getDimension(a['id']) for a in aspects_in_this_geom]
        singleVar = [x == 1 for x in nDims]
        # fixes the histogram size for scalar variables
        nDims = [x if x > 1 else NBINS for x in nDims]
        M = np.zeros((current_number_ccs, np.sum(nDims)))
        for i, aspect in enumerate(aspects_in_this_geom):
            a = aspect['id']

            if i == 0:
                start = 0
            else:
                start = sum(nDims[:i])
            finish = start+nDims[i]

            for n in tqdm(cl[g], desc=ds.getAspectName(a)):
                vals = ds.getData(a, n)
                cc = cl[g][n]
                if (vals is None) or np.any(np.isnan(vals)):
                    continue
                if singleVar[i]:
                    tempH, _ = np.histogram(vals, NBINS, range=(
                        ds.getMinima(a)[0], ds.getMaxima(a)[0]))
                else:
                    tempH = np.array(vals)

                M[cc, start:finish] += tempH

            # normalizing each section
            M[:, start:finish] = (M[:, start:finish].T /
                                  np.sum(M[:, start:finish], axis=1)).T

        M = np.nan_to_num(M)
        km = KMeans(n_clusters=nClusters).fit(M)
        del(M)
        for n in cl[g]:
            cl[g][n] = int(km.labels_[cl[g][n]])

    # ----------------------------------------------------------
    # Match the clusters across the geometries
    all_paths = ds.getPaths([a['id'] for a in full_info_aspects])
    M = nx.DiGraph()
    for p in all_paths:
        j = 0
        while (p[j][0] == -1)and(p[j][1] == -1):  # path didn't start yet
            j += 1

        for i in range(j+1, len(p)):
            n = p[i-1]
            m = p[i]
            if (n[0] not in cl) or (n[1] not in cl[n[0]]) or (m[0] not in cl) or (m[1] not in cl[m[0]]) or (m == n):
                continue

            source = (n[0], cl[n[0]][n[1]])  # (geom, cluster)
            if (source not in M):
                M.add_node(source)

            target = (m[0], cl[m[0]][m[1]])
            if not target in M:
                M.add_node(target)

            if not M.has_edge(source, target):
                M.add_edge(source, target, count=0)
            else:
                M[source][target]['count'] += 1

    # matching the clusters using the major previous contributor
    for n in M:
        predecessors = sorted(M.in_edges(n, data='count'),
                              key=lambda x: x[2], reverse=True)
        if len(predecessors) > 1:
            M.remove_edges_from(predecessors[1:])
    # The sources can still be multi-linked
    for n in M:
        sucessors = sorted(M.out_edges(n, data='count'),
                           key=lambda x: x[2], reverse=True)
        if len(sucessors) > 1:
            M.remove_edges_from(sucessors[1:])

    # Not using sucessors/in_degree because of "what if x -> x' and y->x'??"
    labels = defaultdict(dict)
    sinks = [n for n in M if len(list(M.out_edges(n))) == 0]
    used = {n: False for n in M}
    for i, s in enumerate(sinks):
        to_do = [s, ]
        while to_do:
            n = to_do.pop(0)
            if used[n]:
                continue
            used[n] = True
            labels[n[0]][n[1]] = i
            to_do.extend(list(M.predecessors(n)))

    nCC = 0
    for g in cl:
        for n in cl[g]:
            cl[g][n] = labels[g][cl[g][n]]
            nCC = max([nCC, cl[g][n]])

    # ----------------------------------------------------------------------------

    # cluster_sequences = []
    # for path in all_paths:
    #     cluster_sequences.append(
    #         tuple([(n[0], cl[n[0]][n[1]]) for n in path if n[0] != -1 and n[1] in cl[n[0]]]))

    # print(len(cluster_sequences))
    # cluster_sequences = set(cluster_sequences)
    # print(len(cluster_sequences))

    return({'clustering': cl,
            'evolution': [],
            'hist': {'aspect': [], 'path': []},
            'aspects': full_info_aspects,
            'nclusters': nCC+1})

    paths = [[{'geom': m[0],
               'id': m[1],
               'x': a,
               'y': points[a][m[1]]}, ]
             for m in M if m[0] == g
             if m[1] in points[a]]

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

    # to_use = ['44f0e97d-7037-4e6f-ae71-3ced55d1ad17',
    #           'a2e83ff8-6962-48aa-8740-3c250e8d3a13',
    #           'c29fb848-8836-45df-8ef1-b78e57bf6ccf',
    #           '56158126-6589-4037-b7d3-bc8789d950b4',
    #           'b0d6c9b9-2935-4760-a394-68b791b12a22',
    #           'd36bd0e0-d74d-4355-a967-31c357239646']
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
