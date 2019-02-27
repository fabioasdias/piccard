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
from numpy import nan

import cherrypy
import networkx as nx
import tempfile

from hierMWW import hierMWW
from mmg import segmentation
from networkx.readwrite import json_graph
from scipy.spatial.distance import pdist, sqeuclidean, squareform
from sklearn.manifold import TSNE
from dataStore import dataStore
from upload import processUploadFolder, gatherInfoJsons
HBINS=50



def cors():
  if cherrypy.request.method == 'OPTIONS':
    # preflign request 
    # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
    cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
    cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
    cherrypy.response.headers['Access-Control-Allow-Origin']  = '*'
    # tell CherryPy no avoid normal handler
    return True
  else:
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)

def _doStats(V):
    return(np.nanmedian(V,axis=0),np.nanmin(V,axis=0),np.nanmax(V,axis=0),np.percentile(V,25,axis=0),np.percentile(V,75,axis=0))

def _getD(dsconf, X):
    def _parD(x):
        return(squareform(pdist(x, 'cosine')))
    w = dsconf['weights']
    if len(w)==0:
        return(np.atleast_2d([]))
    N = X[0].shape[0]
    D = np.zeros((N,N))
    for i in range(len(dsconf['ivars'])):
        D = D + w[i] * _parD(X[i])
    return(D)


def _createID(dsconf, useOnly=[]):
    ID = 'cache'
    for k in sorted(dsconf.keys()):
        if (not useOnly) or (k in useOnly):
            ID = ID + '-' + '_'.join(['{0}'.format(i) for i in dsconf[k]])
    return(ID)


def _TemporalDifferences(curCountry, dsconf, H, nodes=None):
    ds = curCountry['ds']

    if (nodes is not None):
        if (nodes==[]):
            return([])
        G=H.subgraph(nodes)
    else:
        G=H
    

    states = dict()
    pop = dict()

    indVars={v:i for i,v in enumerate(dsconf['ivars'])}

    for n in G.nodes():
        V=ds.getValue(n,dsconf)
        if (n[0] not in states):
            states[n[0]]=dict()
            pop[n[0]]=0
            
        pop[n[0]]+=ds.getPopulation(n)


        for i in dsconf['ivars']:
            if (i not in states[n[0]]):
                states[n[0]][i]=[]
            states[n[0]][i].append(V[indVars[i]])
            
    smin=dict()
    smax=dict()
    smed=dict()
    sq1=dict()
    sq3=dict()

    for y in states:
        smin[y]=dict()
        smax[y]=dict()
        smed[y]=dict()
        sq1[y]=dict()
        sq3[y]=dict()
        for i in states[y]:
            states[y][i]=np.array(states[y][i])
            smed[y][i], smin[y][i], smax[y][i], sq1[y][i], sq3[y][i]=_doStats(states[y][i])



    ret=[]

    for i in dsconf['ivars']:
        short=ds.getVarShortLabels(i)
        labels=ds.getVarLabels(i)

        ranges=[]
        for j in range(len(smin[y][i])):
            row={'short':short[j],'ord':j,'long':labels[j],'states':dict(),}
            for y in states:
                row['states'][y]=[{'min':smin[y][i][j],
                                   'max':smax[y][i][j],
                                   'Q1' : sq1[y][i][j],
                                   'Q3' : sq3[y][i][j],
                                   'med':smed[y][i][j],
                                   'y' :0,
                                   'x': (sq1[y][i][j]+sq3[y][i][j])/2.0
                                }]
            ranges.append(row)
        ret.append({'name':ds.getVarName(i),'ranges':ranges})
    return({'population':pop, 'paths':ret})


def _computeTrajectories(G, L, curCountry, corr):

    years= curCountry['years']
    paths=curCountry['temporalPaths']

    traj=dict()    


    for lvl in range(len(corr)):
        traj[lvl]=[]
        for p in paths:
            usedYears=[n[0] for n in p]            
            chain=[corr[lvl][L[n]] for n in p if n in L]
            if (len(chain)!=len(p)):
                continue #missing data in one of them

            for i in range(len(traj[lvl])):
                if (chain==traj[lvl][i]['chain']) and (usedYears==traj[lvl][i]['years']):
                    tid=i
                    break
            else:
                tid=len(traj[lvl])
                if (len(set(usedYears))!=len(usedYears)):
                    print(chain,usedYears)
                    input('.')
                traj[lvl].append({'tid':tid, 'chain':chain, 'years':usedYears,'nodes':[], 'numNodes':{y:0 for y in years}})

            
            for n in p:
                traj[lvl][tid]['nodes'].append(G.node[n]['nid'])
                traj[lvl][tid]['numNodes'][n[0]]+=1

        for i in range(len(traj[lvl])):
            traj[lvl][i]['nodes']=sorted(set(traj[lvl][i]['nodes']))
    return(traj)





def _runAll(webapp, countryID):
    ds = countries[countryID]['ds']
    V = [x['id'] for x in ds.avVars()]
    for i in range(1, len(V) + 1):
        for cv in combinations(V, i):
            webapp.getSegmentation(countryID=countryID, variables=','.join(['{0}'.format(x) for x in cv]))


@cherrypy.expose
class server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def availableCountries(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret = []
        for i, city in enumerate(countries):
            ret.append({'id': i, 
                        'name': city['name'],
                        'kind': city['kind'],
                        'years': city['years'],
                        'layers':city['layers'],
                        })
        return(ret)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getPath(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        countryID=input_json['countryID']

        dsconf = {}
        curCountry = countries[int(countryID)]
        ds = curCountry['ds']
        basegraph = curCountry['basegraph']
        nodes=[curCountry['i2n'][int(x)] for x in input_json['nodes']]

        # if (variables):
        #     ivars = np.array([int(x) for x in variables])
        # else:
        ivars = np.array([x['id'] for x in ds.avVars()])

        rightOrder = np.argsort(ivars)
        dsconf['ivars'] = ivars[rightOrder]

        ret=_TemporalDifferences(curCountry,dsconf,basegraph,nodes)
        return(ret)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip()
    def getSegmentation(self, countryID, variables=None, weights=None):
        """Returns a json containing the segmentation results considering the variables
           The results are composed by the initial set of labels + the merges done at each level"""
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        # cherrypy.request.config.update({'tools.sessions.timeout': 1200})
        ret = dict()

        dsconf = {}
        curCountry = countries[int(countryID)]
        ds = curCountry['ds']
        basegraph = curCountry['basegraph']

        if (variables):
            ivars = np.array([int(x) for x in variables.split(',')])
        else:
            ivars = np.array([x['id'] for x in ds.avVars()])

        rightOrder = np.argsort(ivars)
        dsconf['ivars'] = ivars[rightOrder]

        ret['dsconf']={'vars':dsconf['ivars'].tolist()} #easier to get back later

        if (weights):
            w = np.array([float(x) for x in weights.split(',')])
            w = w[rightOrder]
        else:
            w = np.array([1.0, ] * len(ivars))

        ret['dsconf']={'vars':dsconf['ivars'].tolist(),'w': w.tolist()} #easier to get back later

        dsconf['weights'] = w/np.sum(w)

        cID = _createID(dsconf)
        # cacheName = join(curCountry['cache'], '/{0}.json'.format(cID))
        # if (exists(cacheName)):
        #     with open(cacheName, 'r') as fc:
        #         buff = json.loads(fc.read())
        #     return(buff)

        G = basegraph.copy()

        NaNs = []
        for n in G:
            for tVar in ds.getValue(n, dsconf):
                if ((len(tVar) == 1) and (np.isnan(tVar[0]))) or ((len(tVar) > 1) and (np.sum(tVar) < 0.5)):
                    NaNs.append(n)
                    break
        G.remove_nodes_from(NaNs)


        ret['years'] = curCountry['years']

        print('segmentation')
        t0 = time()
        X, NbI = ds.tabDataList(dsconf, G.nodes())
        D = _getD(dsconf, X)

        baseLabels, corr, clusterNodes = hierMWW(
            D, G, NbI, dsconf, maxClusters=8)
            
        ret['levelCorr'] = corr
        print(time() - t0)

        print('traj')
        t0 = time()        
        ret['traj']= _computeTrajectories(G, baseLabels, curCountry, corr)
        print(time() - t0)
        print('display labels')
        t0 = time()        

        ret['labels'] = {}
        for (y,CTID) in baseLabels:
            if y not in ret['labels']:
                ret['labels'][y]={}
            ret['labels'][y][CTID]=baseLabels[(y,CTID)]
        print(time() - t0)



        print('temporal differences')
        t0 = time()
        tdsconf={**dsconf}
        tdsconf['ivars']=np.array([x['id'] for x in ds.avVars()])
        ret['basepath']=_TemporalDifferences(curCountry, tdsconf, G)
        print(time() - t0)

        print(time() - t0)
        

        print('cluster stats')
        t0 = time()

        Q = dict()
        aspects=set()
        for c in clusterNodes:
            temp = {y:{} for y in curCountry['years']}
            Q[c] = dict()
            for n in clusterNodes[c]:
                y=n[0]
                cData = ds.getValue(n)
                for i, v in enumerate(cData):
                    if (i not in temp[y]):
                        temp[y][i] = []
                    aspects.add(i)
                    temp[y][i].append(v)

            for vi in aspects:
                cTemp=[]
                for y in temp:
                    if (vi in temp[y]):
                        cTemp=cTemp+temp[y][vi]
                cTemp = np.array(cTemp).squeeze()
                q1 = np.atleast_1d(np.percentile(cTemp, q=25, axis=0).squeeze()).tolist()
                q3 = np.atleast_1d(np.percentile(cTemp, q=75, axis=0).squeeze()).tolist()
                med = np.atleast_1d(np.percentile(cTemp, q=50, axis=0).squeeze()).tolist()


                vmin = np.atleast_1d(np.amin(cTemp, axis=0).squeeze()).tolist()
                vmax = np.atleast_1d(np.amax(cTemp, axis=0).squeeze()).tolist()
                q1q3 = (np.array(q3) - np.array(q1))
                H=dict()
                for vv in range(cTemp.shape[1]):
                    hh={}
                    for y in temp:
                        if (vi not in temp[y]):
                            h=np.zeros((HBINS,)).tolist()
                        else:
                            curT=np.array(temp[y][vi])
                            h,_=np.histogram(curT[:,vv],bins=HBINS,range=(0,1))
                            h=h.astype(int).squeeze().tolist()
                        hh[y]=h
                    H[vv]=hh

                Q[c][vi] = {'q1': q1,
                            'q3': q3,
                            'hist':H,
                            'min': vmin,
                            'max': vmax,
                            'med': med,
                            'q1q3': q1q3,
                            'numel': len(clusterNodes[c]),
                            'var': ds.getVarName(vi),
                            'short': ds.getVarShortLabels(vi),
                            'range': ds.getVarLabels(vi)}


        AllOverlaps = dict()
        importances = dict()
        for lvl in range(len(corr)):
            AllOverlaps[lvl] = dict()
            importances[lvl] = dict()
            tClusters = sorted(set(corr[lvl]))
            # plt.figure()
            for c1 in tClusters:
                if (c1 not in importances[lvl]):
                    importances[lvl][c1] = dict()

                for v in Q[c1]:
                    if (len(tClusters) == 1):
                        importances[lvl][c1][v]=[1,]*len(Q[c1][v]['q3']) #nobody to compare
                        continue

                    # it would be faster if c2>c1, but then it would more complicated afterwards. This runs fast enough.
                    for c2 in tClusters:
                        if (c2 == c1):
                            continue
                        if (c1 not in AllOverlaps[lvl]):
                            AllOverlaps[lvl][c1] = dict()
                        if (c2 not in AllOverlaps[lvl][c1]):
                            AllOverlaps[lvl][c1][c2] = dict()
                        if (v not in AllOverlaps[lvl][c1][c2]):
                            AllOverlaps[lvl][c1][c2][v] = (np.min([Q[c1][v]['q3'], Q[c2][v]['q3']], axis=0) - np.max(
                                [Q[c1][v]['q1'], Q[c2][v]['q1']], axis=0)) #/ len(Q[c1][v]['q1'])

                    overlaps = np.max([AllOverlaps[lvl][c1][c2][v]
                                          for c2 in AllOverlaps[lvl][c1]], axis=0)
                    # plt.plot(overlaps)
                    importances[lvl][c1][v] = (-overlaps+1.0)/2.0 #overlap: -1 spread, 0 touch, 1 full overlap
            # plt.show()
            # if len(tClusters) > 1:
            #     D = np.zeros((len(tClusters), len(tClusters)))
            #     C2I = {c: i for i, c in enumerate(tClusters)}
            #     for c1 in tClusters:
            #         for c2 in tClusters:
            #             if c2 <= c1:
            #                 continue
            #             D[C2I[c1]][C2I[c2]] = - np.sum(
            #                 [np.sum(AllOverlaps[lvl][c1][c2][x]) for x in AllOverlaps[lvl][c1][c2]])

            #     D = D + D.T - D.min()
            #     for i in range(D.shape[0]):
            #         D[i, i] = 0.0

        ret['centroid'] = curCountry['centroid']

        ret['patt'] = []
        # impMin = dict()
        # impMax = dict()
        # for lvl in importances:
        #     impMin[lvl] = dict()
        #     impMax[lvl] = dict()
        #     for c in importances[lvl]:
        #         if (c == lastCluster):
        #             continue
        #         flVersion = []
        #         for v in importances[lvl][c]:
        #             flVersion.extend(importances[lvl][c][v])
        #         flVersion = np.array(flVersion)
        #         impMin[lvl][c] = np.amin(flVersion)
        #         impMax[lvl][c] = np.amax(flVersion)

        for c in clusterNodes:
            V = []
            names = []
            for v in Q[c]:
                cVar = []
                for i in range(len(Q[c][v]['q1'])):
                    importance = []
                    for lvl in importances:
                        if c in importances[lvl]:
                            importance.append(importances[lvl][c][v][i])
                                # (importances[lvl][c][v][i] - impMin[lvl][c]) / abs(impMax[lvl][c] - impMin[lvl][c]))
                        else:
                            importance.append(-1.0)
                                #  'y': (Q[c][v]['q1'][i] + Q[c][v]['q3'][i]) / 2.0,
                    cVar.append({'xx': i,
                                 'hist': Q[c][v]['hist'][i],
                                 'y': Q[c][v]['med'][i],
                                 'yMin': Q[c][v]['min'][i],
                                 'yMax': Q[c][v]['max'][i],
                                 'yQ1': Q[c][v]['q1'][i],
                                 'yQ3': Q[c][v]['q3'][i],
                                 'importance': importance,
                                 'x': Q[c][v]['short'][i]
                                 })

                V.append(cVar)
                names.append(Q[c][v]['var'])

            ret['patt'].append({'id': c, 'variables': V, 'names': names})#, 'gmetric': _GeoMetric(basegraph,clusterNodes[c])})

        print(time() - t0)

        print('colours')
        colours = dict()
        used = dict()
        colours[0] = dict()
        for j, c in enumerate(sorted(set(corr[0]))):
            used[c] = j
            colours[0][c] = j
        for level in range(1, len(corr)):
            colours[level] = dict()
            for c in set(corr[level]):
                if (c not in used):
                    newColour = list(
                        set(range(len(corr[0]))) - set([used[x] for x in corr[level] if x != c]))[0]
                    used[c] = newColour
                colours[level][c] = used[c]
        ret['colours'] = colours

        ret['conf'] = [{"var": ds.getVarName(dsconf['ivars'][i]), 'w':w[i]} for i in range(len(dsconf['ivars']))]

        # with open(cacheName, 'w') as fc:
        #     json.dump(ret,fc)
        return(ret)

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
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def upload(self, file):
        myFile=file
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        res={'name':myFile.filename,'ok':True}
        with tempfile.TemporaryDirectory() as tempDir:
            fname=join(tempDir,myFile.filename)
            with open(fname,'wb') as outFile:        
                while True:
                    data = myFile.file.read(8192)
                    if not data:
                        break
                    outFile.write(data)      
            try:
                res.update(processUploadFolder(tempDir, baseconf['upload'],cherrypy.request.remote.ip))
            except:
                raise
                res['ok']=False      
        return(res)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getRegionDetails(self, countryID, displayID):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        displayID = int(displayID)
        countryID = int(countryID)
        curCountry = countries[countryID]
        ret = dict()
        for year in curCountry['years']:
            try:  # not all display id actually exist...
                n = curCountry['nByYearDisplayId'][(year, displayID)]
                ret[year] = curCountry['ds'].getRaw(n) + [{'type': "internal", 'short': [
                    'CTID', ], 'values': [n[1], ], 'name': 'CTID', 'labels': ['name']}, ]
                for i in range(len(ret[year])):
                    for j in range(len(ret[year][i]['values'])):
                        if (np.isnan(ret[year][i]['values'][j])):
                            ret[year][i]['values'][j] = 0
            except:
                pass
        return(ret)


if __name__ == '__main__':
    if (len(sys.argv)) != 2:
        print(".py conf.json")
        exit(-1)

    countries = []
    #freshly uploaded (and unconfigured) data goes here
    baseconf={'upload':'./upload'}
    if (not exists(baseconf['upload'])):
        makedirs(baseconf['upload'])

    with open(sys.argv[1],'r') as fin:
        countriesConfig=json.load(fin)

    for i, v in enumerate(countriesConfig):
        cData = dict()
        cData.update(v)

        baseFolder = v['folder']

        cName = v['name']
        print('\n\n'+cName)

        cData['basegraph'] = nx.read_gpickle(join(baseFolder,'basegraph.gp'))
        
        cData['i2n']={}
        for n in cData['basegraph']:
            cData['i2n'][cData['basegraph'].node[n]['nid']]=n
        cData['years'] = sorted(v['years'])

        # with open(join(baseFolder,'basegraph.gp.tpaths'),'r') as fin:
        #     cData['temporalPaths'] = json.load(fin)
        # for ii,p in enumerate(cData['temporalPaths']):
        #     cData['temporalPaths'][ii]=[tuple(n) for n in p]
        cData['raw']=join(baseFolder,'raw')
        cData['aspects']=join(baseFolder,'aspects')
        if not exists(cData['raw']):
            makedirs(cData['raw'])
        if not exists(cData['aspects']):
            makedirs(cData['aspects'])
        cData['ds'] = dataStore()
        # cData['ds'].loadAndPrep(baseFolder, cData['basegraph'])

        countries.append(cData)
        # webapp.getSegmentation(countryID=i)#,variables='1,3,5,6,7')
        # break

    webapp = server()
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*','application/*']
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.server.max_request_body_size = 0 #for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
