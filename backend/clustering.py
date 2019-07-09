from heapq import heapify, heappop, heappush
from random import random, sample

import matplotlib.pylab as plt
import networkx as nx
import numpy as np
from matplotlib import cm
from networkx.drawing.nx_agraph import graphviz_layout
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import cdist, cosine, euclidean
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

NBINS = 100
THR_STEP = 0.10
THR_START = 0.10


def _clusterDistance(G, C1, C2, layer):
    if np.any(np.isnan(C1['histogram'])) or np.any(np.isnan(C2['histogram'])):
        return(1)

    h1 = C1['histogram']
    s1 = np.sum(h1)
    if (s1 > 0):
        h1 = h1/s1
    # X1 = np.cumsum(h1)

    h2 = C2['histogram']
    s2 = np.sum(h2)
    if (s2 > 0):
        h2 = h2/s2
    # X2 = np.cumsum(h2)

    # D = np.sum(np.abs(X1-X2))/NBINS
    # D = cosine(h1,h2)
    D = euclidean(h1, h2)/np.sqrt(2)

    return(D)


def Union(x, y):
    xRoot = Find(x)
    yRoot = Find(y)
    if xRoot['rank'] > yRoot['rank']:
        xRoot['members'].extend(yRoot['members'])
        xRoot['histogram'] = xRoot['histogram']+yRoot['histogram']
        del(yRoot['histogram'])
        del(yRoot['members'])
        yRoot['parent'] = xRoot
    elif xRoot['rank'] < yRoot['rank']:
        yRoot['members'].extend(xRoot['members'])
        yRoot['histogram'] = xRoot['histogram']+yRoot['histogram']
        del(xRoot['histogram'])
        del(xRoot['members'])
        xRoot['parent'] = yRoot
    elif xRoot['id'] != yRoot['id']:  # Unless x and y are already in same set, merge them
        yRoot['parent'] = xRoot
        xRoot['members'].extend(yRoot['members'])
        xRoot['histogram'] = xRoot['histogram']+yRoot['histogram']
        del(yRoot['histogram'])
        del(yRoot['members'])
        xRoot['rank'] = xRoot['rank'] + 1


def Find(x):
    if x['parent']['id'] == x['id']:
        return x
    else:
        x['parent'] = Find(x['parent'])
        return x['parent']


def _createHist(vals, minVal, maxVal):
    th, _ = np.histogram(vals, bins=NBINS, range=(minVal, maxVal))
    return(th)


def ComputeClustering(G: nx.Graph, layer: str, k: int = 1):
    """This function changes the graph G. 
    'layer' represents the key that stores the data.
    'k' is the number of knn edges to consider for each node after the geographic phase."""

    firstNode = list(G.nodes())[0]
    NDIMS = len(G.node[firstNode][layer])
    # print('Histogram dimensions', NDIMS)

    i2n = {}
    cData = []
    i = 0
    to_remove = []
    for n in G:
        vals = G.node[n][layer]
        if np.any(np.isnan(vals)):
            to_remove.append(n)
            continue
        i2n[i] = n
        cData.append(vals)
        i += 1
    cData = np.array(cData)

    G.remove_nodes_from(to_remove)

    neigh = NearestNeighbors(k)
    if NDIMS == 1:
        cData = (cData - cData.min()) / (cData.max() - cData.min())
    neigh.fit(np.atleast_2d(cData))

    A = np.nonzero(neigh.kneighbors_graph())

    extra_edges = [(i2n[A[0][i]], i2n[A[1][i]]) for i in range(A[0].shape[0])]
    extra_edges = [e for e in extra_edges if not G.has_edge(e[0],e[1])]#only non-existing links

    # pos={}
    # for n in G:
    #     pos[n]=G.node[n]['pos'][:2]
    # nx.draw_networkx_nodes(G,pos=pos,node_size=2)
    # nx.draw_networkx_edges(G,pos=pos,edgelist=extra_edges)
    # plt.show()

    print(len(extra_edges))
    # extra_edges=[]

    e2i = {}
    i2e = {}
    i = 0
    for e in list(G.edges())+extra_edges:
        e2i[e] = i
        e2i[(e[1], e[0])] = i
        i2e[i] = e
        i += 1

    # print(G.node[firstNode][layer])
    if NDIMS == 1:
        minVal = G.node[firstNode][layer][0]
        maxVal = G.node[firstNode][layer][0]
    allVals = []
    nToVisit = []

    for e in G.edges():
        G[e[0]][e[1]]['level'] = -1

    for n in G.nodes():
        G.node[n]['parent'] = G.node[n]
        G.node[n]['rank'] = 0
        G.node[n]['id'] = n
        G.node[n]['members'] = [n, ]

        if (G.node[n][layer] is not None):
            allVals.append(G.node[n][layer])
            nToVisit.append(n)
            if NDIMS == 1:
                minVal = min((minVal, G.node[n][layer][0]))
                maxVal = max((maxVal, G.node[n][layer][0]))
    if NDIMS == 1:
        print('Value range: {0}-{1}'.format(minVal, maxVal))
        for n in nToVisit:
            G.node[n]['histogram'] = _createHist(
                G.node[n][layer], minVal, maxVal,)
    else:
        for n in nToVisit:
            G.node[n]['histogram'] = G.node[n][layer][:]

    print('starting clustering')
    E = {e2i[e]: True for e in e2i}
    NE = len(G.edges())

    curThreshold = THR_START

    while (NE > 0):
        # print('-----------------\n\nlevel ', level)

        # level += 1

        H = {}
        queued = dict()
        dv = []
        # if geographic:
        #     to_use = [e2i[ee] for ee in G.edges()]
        # else:
        #     to_use = [e2i[ee] for ee in extra_edges]

        to_use = [ee for ee in E if E[ee]]
        print('heaping distances')
        for ee in tqdm(to_use):
            e = i2e[ee]
            x = Find(G.node[e[0]])
            xid = x['id']
            y = Find(G.node[e[1]])
            yid = y['id']
            if (xid != yid):
                K = (min((xid, yid)), max((xid, yid)))
                if K not in queued:
                    queued[K] = True
                    numel = min((len(x['members']), len(y['members'])))
                    cD = _clusterDistance(G, x, y, layer=layer)
                    if (numel not in H):
                        H[numel] = []
                    heappush(H[numel], (cD, K, [(x,y), e])) #distance, ID, data
                    dv.append(cD)
        if (not dv):
            break

        print('(min:{0:2.3f}, max:{1:2.3f}, median:{2:2.3f})'.format(
            np.min(dv), np.max(dv), np.median(dv)))

        # if the minimum pair is too different (as in max difference), start with the knn edges
        minV = np.min(dv)
        if (minV > curThreshold):
            if np.isclose(minV, np.max(dv)):
                print('Last level', minV)
                for e in G.edges():
                    if G[e[0]][e[1]]['level'] == -1:
                        G[e[0]][e[1]]['level'] = minV
                break

            curThreshold += THR_STEP
            continue

        to_merge = []
        used = {}
        el = []
        # curThreshold = np.percentile(dv, 25)
        # Prefers to merge small clusters first
        for numel in sorted(H.keys()):
            while len(H[numel]) > 0:
                el = heappop(H[numel])
                roots, _ = el[2]
                x,y = roots
                if (el[0] > curThreshold):
                    break
                if (x['id'] in used) or (y['id'] in used):
                    continue
                used[x['id']] = True
                used[y['id']] = True
                to_merge.append(el[2])
        print('merging')
        for (roots, e) in tqdm(to_merge):
            x,y = roots
            XE = set([e2i[e] for e in list(G.edges(x['members']))])
            YE = set([e2i[e] for e in list(G.edges(y['members']))])
            rE = list(XE.intersection(YE))
            if not rE: #knn edge
                # e=(xx,yy) #keep the originals, otherwise e2i doesn't know them
                G.add_edge(e[0], e[1])
                G[e[0]][e[1]]['level'] = curThreshold
                E[e2i[e]] = False
            else:
                for ee in list(rE):
                    e = i2e[ee]
                    G[e[0]][e[1]]['level'] = curThreshold
                    E[ee] = False
                    NE -= 1
            Union(x, y)
        roots = set([Find(G.node[x])['id'] for x in G.nodes()])
        print('level {0} #clusters {1} '.format(curThreshold, len(roots)))


    return(G)
