from heapq import heapify, heappop, heappush
from random import random, sample

import matplotlib.pylab as plt
import networkx as nx
import numpy as np
from matplotlib import cm
from networkx.drawing.nx_agraph import graphviz_layout
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import cdist, euclidean
from scipy.stats import wasserstein_distance
from sklearn.neighbors import NearestNeighbors


NBINS = 100


def _clusterDistance(G, C1, C2, layer):
    if np.any(np.isnan(C1['histogram'])) or np.any(np.isnan(C2['histogram'])):
        return(1)

    h1 = C1['histogram']
    s1 = np.sum(h1)
    if (s1 > 0):
        h1 = h1/s1
    X1 = np.cumsum(h1)

    h2 = C2['histogram']
    s2 = np.sum(h2)
    if (s2 > 0):
        h2 = h2/s2
    X2 = np.cumsum(h2)

    D = np.sum(np.abs(X1-X2))/NBINS
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


def ComputeClustering(G: nx.Graph, layer: str): #, k: int = 10
    """This function changes the graph G. 
    'layer' represents the key that stores the data."""
    # 'k' is the number of knn edges to consider for each node after the geographic phase."""

    firstNode = list(G.nodes())[0]
    NDIMS = len(G.node[firstNode][layer])
    # print('Histogram dimensions', NDIMS)

    i2n = {}
    cData = []
    i = 0
    to_remove=[]
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

    # neigh = NearestNeighbors(k)
    # if NDIMS == 1:
    #     cData = (cData - cData.min()) / (cData.max() - cData.min())
    # neigh.fit(np.atleast_2d(cData))

    # A = np.nonzero(neigh.kneighbors_graph())
    # extra_edges=[(i2n[A[0][i]], i2n[A[1][i]]) for i in range(A[0].shape[0])]
    extra_edges=[]

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

    level = 0
    geographic = True

    while (NE > 0):
        print('-----------------\n\nlevel ', level)

        level += 1

        H = {}
        queued = dict()
        dv = []
        if geographic:
            to_use=E
        else:
            to_use=[e2i[ee] for ee in extra_edges]

        for ee in to_use:
            if (E[ee] == False):
                continue

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

                    # if not geographic:
                    #     print(x['histogram'])
                    #     print(y['histogram'])
                    #     plt.plot(x['histogram'],'xr')
                    #     plt.plot(y['histogram'],'ob')
                    #     plt.show()
                    #     print('.',cD)
                    heappush(H[numel], (cD, K, (x, y)))
                    dv.append(cD)
        if (not dv):
            break

        print('(min:{0:2.3f}, max:{1:2.3f}, median:{2:2.3f})'.format(np.min(dv), np.max(dv), np.median(dv)),geographic)


        # if the minimum pair is too different (as in max difference), start with the knn edges
        if np.isclose(np.min(dv), np.max(dv)):
            if geographic:
                geographic = False
                print('going knn')
                continue            
            #already tried the knn edges, clump the rest
            else:
                print('all different')
                # roots = list(set([Find(G.node[x])['id'] for x in G.nodes()]))
                # id2i = {k: i for i, k in enumerate(roots)}
                # R = len(roots)
                # D = np.zeros((R, R))-1
                # for (x,y) in extra_edges:
                #     xx = Find(G.node[x])
                #     ix = id2i[xx['id']]
                #     yy = Find(G.node[y])
                #     iy = id2i[yy['id']]
                #     if D[ix, iy] == -1:
                #         D[ix, iy] = _clusterDistance(G, xx, yy, layer=layer)
                # D=D+D.T
                # for i in range(R):
                #     D[i,i]=1

                # print(np.min(D),np.max(D))
                # plt.imshow(D)
                # plt.colorbar()
                # plt.figure()
                # plt.hist(D.flatten(),100)
                # plt.show()

                for e in G.edges():
                    if G[e[0]][e[1]]['level'] == -1:
                        G[e[0]][e[1]]['level'] = level
                break

        else:
            to_merge = []
            used = {}
            el = []
            quantileThreshold = np.percentile(dv, 25)
            # Prefers to merge small clusters first
            for numel in sorted(H.keys()):
                while len(H[numel]) > 0:
                    el = heappop(H[numel])
                    x, y = el[2]
                    if (el[0] > quantileThreshold):
                        break
                    if (x['id'] in used) or (y['id'] in used):
                        continue
                    used[x['id']] = True
                    used[y['id']] = True
                    to_merge.append((x, y))


            removedEdges = 0
            for (x, y) in to_merge:
                x = Find(x)
                y = Find(y)
                XE = set([e2i[e] for e in list(G.edges(x['members']))])
                YE = set([e2i[e] for e in list(G.edges(y['members']))])
                rE = list(XE.intersection(YE))
                removedEdges += len(rE)
                for ee in list(rE):
                    e = i2e[ee]
                    if not geographic:
                        print('merging',e)

                    G[e[0]][e[1]]['level'] = level
                    E[ee] = False
                    NE -= 1
                Union(x, y)
            roots = set([Find(G.node[x])['id'] for x in G.nodes()])
            print('level {0} #clusters {1} '.format(level, len(
                roots))+'QT {0:2.3f} (min:{1:2.3f}, max:{2:2.3f}, median:{3:2.3f})'.format(quantileThreshold, np.min(dv), np.max(dv), np.median(dv)))

    return(G)
