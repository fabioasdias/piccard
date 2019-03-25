import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pylab as plt
import numpy as np
from scipy.spatial.distance import cdist,euclidean
from scipy.ndimage import gaussian_filter
from scipy.stats import wasserstein_distance
from heapq import heappop, heappush,heapify
from random import sample, random
from matplotlib import cm
import matplotlib.pylab as plt

NBINS=100


def _clusterDistance(G,C1,C2,layer):
    if np.any(np.isnan(C1['histogram'])) or np.any(np.isnan(C2['histogram'])):
        return(1)

    h1=C1['histogram']
    s1=np.sum(h1)
    if (s1>0):
        h1=h1/s1
    X1=np.cumsum(h1)
    
    h2=C2['histogram']
    s2=np.sum(h2)
    if (s2>0):
        h2=h2/s2
    X2=np.cumsum(h2)

    D=np.sum(np.abs(X1-X2))/NBINS
    return(D)


def Union(x, y):
     xRoot = Find(x)
     yRoot = Find(y)
     if xRoot['rank'] > yRoot['rank']:
         xRoot['members'].extend(yRoot['members'])
         xRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         del(yRoot['histogram'])
         del(yRoot['members'])
         yRoot['parent'] = xRoot
     elif xRoot['rank'] < yRoot['rank']:
         yRoot['members'].extend(xRoot['members'])
         yRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         del(xRoot['histogram'])
         del(xRoot['members'])
         xRoot['parent'] = yRoot
     elif xRoot['id'] != yRoot['id']: # Unless x and y are already in same set, merge them
         yRoot['parent'] = xRoot
         xRoot['members'].extend(yRoot['members'])
         xRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         del(yRoot['histogram'])
         del(yRoot['members'])
         xRoot['rank'] = xRoot['rank'] + 1

def Find(x):
     if x['parent']['id'] == x['id']:
        return x
     else:
        x['parent'] = Find(x['parent'])
        return x['parent']

def _createHist(vals,minVal,maxVal):
    th,_=np.histogram(vals,bins=NBINS,range=(minVal,maxVal))
    return(th)

def ComputeClustering(G,layer):
    """This function changes the graph G"""
    # print('start CC')
    e2i={}
    i2e={}
    i=0
    for e in G.edges():
        e2i[e]=i
        e2i[(e[1],e[0])]=i
        i2e[i]=e
        i+=1

    
    firstNode=list(G.nodes())[0]
    NDIMS=len(G.node[firstNode][layer])
    if NDIMS==1:
        minVal=G.node[firstNode][layer]
        maxVal=G.node[firstNode][layer]
    allVals=[]
    nToVisit=[]

    for e in G.edges():
        G[e[0]][e[1]]['level']=-1

    for n in G.nodes():
        G.node[n]['parent']=G.node[n]
        G.node[n]['rank']=0
        G.node[n]['id']=n
        G.node[n]['members']=[n,]
    
        if (G.node[n][layer] is not None):
            allVals.append(G.node[n][layer])
            nToVisit.append(n)
            if NDIMS==1:            
                minVal=min((minVal,G.node[n][layer]))
                maxVal=max((maxVal,G.node[n][layer]))
    if NDIMS==1:
        print('Value range: {0}-{1}'.format(minVal,maxVal))
        for n in nToVisit:
            G.node[n]['histogram']=_createHist(G.node[n][layer],minVal,maxVal,)
    else:
        print('Histogram dimensions', NDIMS)
        for n in nToVisit:
            G.node[n]['histogram']=G.node[n][layer][:]
        
    print('starting clustering')
    E={e2i[e]:True for e in G.edges()}
    NE=len(E.keys())

    level=0

    while (NE>0):
        # print('-----------------\n\nlevel ',level)

        level+=1

        H = {}
        queued = dict()
        dv=[]
        for ee in E:
            if (E[ee]==False):
                continue

            e=i2e[ee]
            x=Find(G.node[e[0]])
            xid=x['id']
            y=Find(G.node[e[1]])
            yid=y['id']
            if (xid!=yid):
                K=(min((xid,yid)),max((xid,yid)))
                if K not in queued:
                    queued[K]=True
                    numel=min((len(x['members']),len(y['members'])))
                    cD=_clusterDistance(G, x, y, layer=layer)
                    if (numel not in H):
                        H[numel]=[]
                    heappush(H[numel],(cD,K,(x,y)))
                    dv.append(cD)
        if (not dv):
            break

        quantileThreshold=np.percentile(dv,25)
        # print('Weights done',len(H))
        to_merge = []
        used = {}
        el=[]
        for numel in sorted(H.keys()):
            while len(H[numel])>0:
                el=heappop(H[numel])
                x,y=el[2]
                if (el[0]>quantileThreshold):
                    break
                if (x['id'] in used) or (y['id']  in used):
                    continue
                used[x['id']]=True
                used[y['id']]=True
                to_merge.append((x,y))

        # print('merge selection done: {0} clusters to merge '.format(len(used)))

        removedEdges=0
        for (x,y) in to_merge:
            x=Find(x)
            y=Find(y)
            XE=set([e2i[e] for e in list(G.edges(x['members']))])
            YE=set([e2i[e] for e in list(G.edges(y['members']))])
            rE=list(XE.intersection(YE))
            removedEdges+=len(rE)
            for ee in list(rE):
                e=i2e[ee]
                G[e[0]][e[1]]['level']=level
                E[ee]=False
                NE-=1
                    
            Union(x,y)
        # print('merging done', removedEdges)


        roots=set([Find(G.node[x])['id'] for x in G.nodes()])
        print('level {0} #clusters {1}'.format(level,len(roots))+'QT {0:2.3f} (min:{1:2.3f}, max:{2:2.3f}, median:{3:2.3f})'.format(quantileThreshold,np.min(dv),np.max(dv),np.median(dv)))
    return(G)