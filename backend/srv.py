"""Server module for the backend"""
import json
import os
import pickle
import sys
from itertools import combinations, combinations_with_replacement
from os import makedirs
from os.path import exists
from time import time

import numpy as np
from numpy import nan

import cherrypy
import networkx as nx
from dataStore import dataStore
from hierMWW import hierMWW
from mmg import segmentation
from networkx.readwrite import json_graph
from scipy.spatial.distance import pdist, sqeuclidean, squareform
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors

# import matplotlib.pylab as plt


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


#from scipy.stats import wasserstein_distance, entropy


def _doStats(V):
    return(np.nanmedian(V,axis=0),np.nanmin(V,axis=0),np.nanmax(V,axis=0),np.percentile(V,25,axis=0),np.percentile(V,75,axis=0))

def _parD(x):
    return(squareform(pdist(x, 'cosine')))
    # dt=np.zeros((x.shape[0],x.shape[0]))
    # for i in range(x.shape[0]):
    #     for j in range(i+1,x.shape[0]):
    #         # dt[i,j]=entropy(x[i,:],x[j,:])
    #         dt[i,j]=wasserstein_distance(x[i,:],x[j,:])
    # return(dt+dt.T)

def _GeoMetric(G,nodes):

    nodesByYear=dict()
    for n in nodes:
        if (n[0]) not in nodesByYear:
            nodesByYear[n[0]]=[]
        nodesByYear[n[0]].append(n)

    allNodesByYear=dict()
    for n in G.nodes:
        if (n[0]) not in allNodesByYear:
            allNodesByYear[n[0]]=[]
        allNodesByYear[n[0]].append(n)
    

    TG=dict()
    for year in nodesByYear:
        TG[year]=nx.subgraph(G,allNodesByYear[year])

    t0=time()
    res=[]
    for year in nodesByYear:
        for i in range(len(nodesByYear[year])):
            n1=nodesByYear[year][i]
            thisnode=[]
            for j in range(i+1,len(nodesByYear[year])):
                n2=nodesByYear[year][j]
                try:
                    if (all([x in nodesByYear[year] for x in nx.shortest_path(TG[year],n1,n2)])):
                        thisnode.append(1)
                    else:
                        thisnode.append(0)
                except:
                    pass

            if (len(thisnode)!=0):
                res.append(sum(thisnode)/len(thisnode))
    print(time()-t0)
    return(sum(res)/len(res))

            



def _getD(curCity, dsconf, X):
    w = dsconf['weights']
    p = dict()
    todo = []
    N = X[0].shape[0]
    D = np.zeros((N,N))
    for i, ivar in enumerate(dsconf['ivars']):
        D = D + w[i] * _parD(X[i])
    return(D)


def _createID(dsconf, useOnly=[]):
    ID = 'cache'
    for k in sorted(dsconf.keys()):
        if (not useOnly) or (k in useOnly):
            ID = ID + '-' + '_'.join(['{0}'.format(i) for i in dsconf[k]])
    return(ID)


def _skKNN(X, curCity, dsconf, k=3):
    cData, nByID = curCity['ds'].tabData(dsconf, X.nodes())
    neigh = NearestNeighbors(k)
    if (len(cData.shape) == 1):
        cData = (cData - cData.min()) / (cData.max() - cData.min())
    neigh.fit(np.atleast_2d(cData))

    A = np.nonzero(neigh.kneighbors_graph())
    for i in range(A[0].shape[0]):
        X.add_edge(nByID[A[0][i]], nByID[A[1][i]])
    return(X)


def _TemporalDifferences(curCity, dsconf, H, nodes=None):
    ds = curCity['ds']

    if (nodes is not None):
        if (nodes==[]):
            return([])
        G=H.subgraph(nodes)
    else:
        G=H
    
    years = curCity['years']

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


def _graph2display(G, L, curCity, corr):
    labels = []
    labelsByDID = dict()                
    years= curCity['years']
    ds=curCity['ds']


    for n in sorted(G.nodes()):
        cYear = n[0]
        for i,dl in enumerate(sorted(G.node[n]['display_ids'])):
            labels.append({'year': cYear, 'did': dl, 'id': L[n]})            
            if (G.node[n]['areas'][i]>1e-5):
                if (dl not in labelsByDID):
                    labelsByDID[dl]=[]
                labelsByDID[dl].append({'id':L[n],'year':cYear})



    traj=dict()
    nodesByTID=dict()

    for did in labelsByDID:
        labelsByDID[did]=sorted(labelsByDID[did],key=lambda x: x['year'])

    for lvl in range(len(corr)):
        nodesByTID[lvl]=dict()
        traj[lvl]=[]
        for did in sorted(labelsByDID):
            usedYears=[x['year'] for x in labelsByDID[did]]            
            chain=[corr[lvl][x['id']] for x in labelsByDID[did]]
            for i in range(len(traj[lvl])):
                if (chain==traj[lvl][i]['chain']) and (usedYears==traj[lvl][i]['years']):
                    tid=i
                    break
            else:
                tid=len(traj[lvl])
                if (len(set(usedYears))!=len(usedYears)):
                    print(chain,usedYears)
                    input('.')
                traj[lvl].append({'tid':tid, 'chain':chain, 'years':usedYears, 'pop':{y:0 for y in years},'ctCount':{y:0 for y in years}})


            if (tid not in nodesByTID[lvl]):
                nodesByTID[lvl][tid]=[]

            for y in sorted(usedYears):
                n=None
                try:
                    n=curCity['nByYearDisplayId'][(y, did)]
                except:
                    pass
                if (n):                    
                    nodesByTID[lvl][tid].append(n)                
                    traj[lvl][tid]['pop'][y]+=ds.getPopulation(n)
                    traj[lvl][tid]['ctCount'][y]+=1

        for tid in nodesByTID[lvl]:
            nodesByTID[lvl][tid]=list(set(nodesByTID[lvl][tid]))

    return(labels,traj,nodesByTID)





def _runAll(webapp, cityID):
    ds = cities[cityID]['ds']
    V = [x['id'] for x in ds.avVars()]
    F = [x['id'] for x in ds.avFilters()]
    for i in range(1, len(V) + 1):
        for cv in combinations(V, i):
            for cf in combinations_with_replacement(F, i):
                for k in range(0, 10):
                    webapp.getSegmentation(cityID=cityID, variables=','.join(['{0}'.format(
                        x) for x in cv]), filters=','.join(['{0}'.format(x) for x in cf]), k=k)


@cherrypy.expose
class server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def availableCities(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret = []
        for i, city in enumerate(cities):
            ret.append({'id': i,
                        'name': city['name'],
                        'kind': city['kind'],
                        'years': city['years'],
                        'variables': [{'id': v['id'], 'name': v['name']} for v in city['ds'].avVars()],
                        'filters': [{'id': v['id'], 'name': v['name']} for v in city['ds'].avFilters()]})
        return(ret)

    @cherrypy.expose
    def getGJ(self, cityID):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        with open(cities[int(cityID)]['folder'] + '/display.gj', 'r') as fin:
            buff = fin.read()
        return(buff)


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getPath(self):#, cityID, nodes, variables=None, filters=None):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        cityID=input_json['cityID']
        nodes=input_json['nodes']
        #print(input_json)
        variables=input_json['variables']
        filters=input_json['filters']

        dsconf = {}
        curCity = cities[int(cityID)]
        ds = curCity['ds']
        basegraph = curCity['basegraph']

        # if (variables):
        #     ivars = np.array([int(x) for x in variables])
        # else:
        ivars = np.array([x['id'] for x in ds.avVars()])

        rightOrder = np.argsort(ivars)
        dsconf['ivars'] = ivars[rightOrder]

        # if (filters):
        #     fs = np.array([int(x) for x in filters])
        # else:
        fs = np.zeros_like(ivars)

        dsconf['fs'] = fs[rightOrder]
        ret=_TemporalDifferences(curCity,dsconf,basegraph,[ds.Node(int(x)) for x in nodes])
        # print(ret)
        return(ret)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip()
    def getSegmentation(self, cityID, variables=None, filters=None, weights=None, k=2):
        """Returns a json containing the segmentation results considering the variables
           The results are composed by the initial set of labels + the merges done at each level"""
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        # cherrypy.request.config.update({'tools.sessions.timeout': 1200})
        ret = dict()

        dsconf = {}
        curCity = cities[int(cityID)]
        ds = curCity['ds']
        basegraph = curCity['basegraph']

        if (variables):
            ivars = np.array([int(x) for x in variables.split(',')])
        else:
            ivars = np.array([x['id'] for x in ds.avVars()])

        rightOrder = np.argsort(ivars)
        dsconf['ivars'] = ivars[rightOrder]

        if (filters):
            fs = np.array([int(x) for x in filters.split(',')])
        else:
            fs = np.zeros_like(ivars)

        dsconf['fs'] = fs[rightOrder]


        ret['dsconf']={'vars':dsconf['ivars'].tolist(),'fs':dsconf['fs'].tolist()} #easier to get back later


        k = int(k)
        dsconf['k'] = [k, ]
        if (weights):
            w = np.array([float(x) for x in weights.split(',')])
            w = w[rightOrder]
        else:
            w = np.array([1.0, ] * len(ivars))

        ret['dsconf']={'vars':dsconf['ivars'].tolist(),'fs':dsconf['fs'].tolist(),'w': w.tolist(),'k':k} #easier to get back later

        dsconf['weights'] = w/np.sum(w)

        cID = _createID(dsconf)
        cacheName = curCity['cache'] + '/{0}.json'.format(cID)
        if (exists(cacheName)):
            with open(cacheName, 'r') as fc:
                buff = json.loads(fc.read())
            return(buff)

        G = basegraph.copy()

        to_remove = []
        for n in G:
            for tVar in ds.getValue(n, dsconf):
                if ((len(tVar) == 1) and (np.isnan(tVar[0]))) or ((len(tVar) > 1) and (np.sum(tVar) < 0.5)):
                    to_remove.append(n)
                    break

        G.remove_nodes_from(to_remove)


        ret['years'] = curCity['years']

        if (k > 0):
            print('knn sk')
            t0 = time()
            G = _skKNN(G, curCity, dsconf, k)
            print(time() - t0)

        print('segmentation')
        t0 = time()
        X, NbI = ds.tabDataList(dsconf, G.nodes())
        D = _getD(curCity, dsconf, X)

        baseLabels, corr, clusterNodes = hierMWW(
            D, G, NbI, dsconf, maxClusters=8)
        ret['levelCorr'] = corr
        print(time() - t0)

        print('display labels')
        t0 = time()
        ret['labels'], ret['traj'], nodesByTID= _graph2display(G, baseLabels, curCity, corr)
        print(time() - t0)



        print('temporal differences')
        t0 = time()
        tdsconf={**dsconf}
        tdsconf['ivars']=np.array([x['id'] for x in ds.avVars()])
        tdsconf['fs']=np.zeros_like(tdsconf['ivars'])
        ret['basepath']=_TemporalDifferences(curCity, tdsconf, G)
        ret['nodesByTID']=dict()
        for lvl in range(len(corr)):
            ret['nodesByTID'][lvl]=dict()
            for tid in nodesByTID[lvl]:
                ret['nodesByTID'][lvl][tid]=[ds.JSID(x) for x in nodesByTID[lvl][tid]]
        print(time() - t0)

        print(time() - t0)
        

        print('cluster stats')
        t0 = time()

        Q = dict()
        aspects=set()
        for c in clusterNodes:
            temp = {y:{} for y in curCity['years']}
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

        ret['centroid'] = curCity['centroid']

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

        ret['conf'] = [{"var": ds.getVarName(dsconf['ivars'][i]), 'w':w[i], 'filter':ds.getFilterName(
            dsconf['fs'][i])} for i in range(len(dsconf['ivars']))]

        

        with open(cacheName, 'w') as fc:
            json.dump(ret,fc)
        return(ret)

    @cherrypy.expose
    def index(self):
        return("It works!")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getRegionDetails(self, cityID, displayID):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        displayID = int(displayID)
        cityID = int(cityID)
        curCity = cities[cityID]
        ret = dict()
        for year in curCity['years']:
            try:  # not all display id actually exist...
                n = curCity['nByYearDisplayId'][(year, displayID)]
                ret[year] = curCity['ds'].getRaw(n) + [{'type': "internal", 'short': [
                    'CTID', ], 'values': [n[1], ], 'name': 'CTID', 'labels': ['name']}, ]
                for i in range(len(ret[year])):
                    for j in range(len(ret[year][i]['values'])):
                        if (np.isnan(ret[year][i]['values'][j])):
                            ret[year][i]['values'][j] = 0
            except:
                pass
        return(ret)


if __name__ == '__main__':
    if ((len(sys.argv)) != 2) and ((len(sys.argv)) != 3):
        print(".py conf.json (genCache? - optional = Y/N)")
        exit(-1)

    with open(sys.argv[1], 'r') as f:
        citiesConfig = json.load(f)

    genCache = False
    if (len(sys.argv) == 3) and (sys.argv[2] == 'Y'):
        genCache = True

    cities = []
    webapp = server()

    for i, v in enumerate(citiesConfig):
        if (v['kind']=='SY'):
            continue
        cData = dict()

        baseFolder = v['folder']
        cData['folder'] = baseFolder
        cacheDir = baseFolder + '/cache'
        if (not exists(cacheDir)):
            makedirs(cacheDir)

        cData['cache'] = cacheDir

        cData['centroid'] = v['centroid']

        cName = v['name']
        print('\n\n'+cName)
        cData['name'] = cName
        cData['kind'] = v['kind']

        cData['ds'] = dataStore()
        cData['basegraph'] = nx.read_gpickle(baseFolder + '/basegraph.gp')
        years = []
        cData['nByYearDisplayId'] = dict()
        for n in cData['basegraph']:
            years.append(n[0])
            for did in cData['basegraph'].node[n]['display_ids']:
                cData['nByYearDisplayId'][(n[0], did)] = n
        cData['years'] = sorted(list(set(years)))
        del(years)
        cData['ds'].loadAndPrep(
            baseFolder + '/normGeoJsons.zip', cData['basegraph'])

        cities.append(cData)
        webapp.getSegmentation(cityID=i)#,variables='1,3,5,6,7')
        # break

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

    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
