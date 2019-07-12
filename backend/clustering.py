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
from heapq import heapify, heappop, heappush

NBINS = 100
THR_STEP = 0.05
THR_START = 0.05


def _clusterDistance(G, x, y, layer):
    h1 = G.node[x]['histogram']
    h2 = G.node[y]['histogram']
    # if np.any(np.isnan(h1)) or np.any(np.isnan(h2)):
    #     return(1)

    # s1 = np.sum(h1)
    # if (s1 > 0):
    #     h1 = h1/s1
    # # X1 = np.cumsum(h1)

    # s2 = np.sum(h2)
    # if (s2 > 0):
    #     h2 = h2/s2
    # # X2 = np.cumsum(h2)

    # D = np.sum(np.abs(X1-X2))/NBINS
    D = cosine(h1, h2)
    # else:
    #     D = euclidean(h1, h2)/np.sqrt(2)

    return(D)


def _createHist(vals, minVal, maxVal):
    th, _ = np.histogram(vals, bins=NBINS, range=(minVal, maxVal))
    return(th)

# @profile


def ComputeClustering(G: nx.Graph, layer: str, k: int = 0):
    """This function changes the graph G. 
    'layer' represents the key that stores the data.
    'k' is the number of extra knn edges to consider for each node"""

    firstNode = list(G.nodes())[0]
    NDIMS = len(G.node[firstNode][layer])
    # print('Histogram dimensions', NDIMS)

    i2n = {}
    cData = []
    i = 0
    to_remove = []
    for n in G:
        if (layer not in G.node[n]) or (G.node[n][layer] is None) or np.any(np.isnan(G.node[n][layer])) or (np.sum(G.node[n][layer]) == 0):
            to_remove.append(n)
            continue
        i2n[i] = n
        cData.append(G.node[n][layer])
        i += 1
    cData = np.array(cData)

    G.remove_nodes_from(to_remove)
    firstNode = list(G.nodes())[0]

    for e in G.edges():
        G[e[0]][e[1]]['level'] = -1


    if k > 0:
        neigh = NearestNeighbors(k)
        if NDIMS == 1:
            if not np.isclose(0,cData.max()-cData.min()):
                cData = (cData - cData.min()) / (cData.max() - cData.min())

        neigh.fit(np.atleast_2d(cData))

        A = np.nonzero(neigh.kneighbors_graph())

        extra_edges = [(i2n[A[0][i]], i2n[A[1][i]]) for i in range(A[0].shape[0])]
        extra_edges = [e for e in extra_edges if not G.has_edge(
            e[0], e[1])]  # only non-existing links
    else:
        extra_edges = []

    if NDIMS == 1:
        minVal = G.node[firstNode][layer][0]
        maxVal = G.node[firstNode][layer][0]

    C = nx.Graph()
    n2i = {n: i for i, n in enumerate(G)}
    C.add_nodes_from(range(len(n2i)))
    newNodeId = len(n2i)+1  # the +1 is probably not necessary

    for n in G.nodes():
        C.node[n2i[n]]['members'] = [n, ]
        if (G.node[n][layer] is not None):
            if NDIMS == 1:
                minVal = min((minVal, G.node[n][layer][0]))
                maxVal = max((maxVal, G.node[n][layer][0]))
    if NDIMS == 1:
        print('Value range: {0}-{1}'.format(minVal, maxVal))
        for n in G:
            C.node[n2i[n]]['histogram'] = _createHist(
                G.node[n][layer], minVal, maxVal,)
    else:
        for n in G:
            C.node[n2i[n]]['histogram'] = G.node[n][layer][:]

    print('computing distances')
    for (x, y) in tqdm(list(G.edges())+extra_edges):
        dist = _clusterDistance(C, n2i[x], n2i[y], layer=layer)
        C.add_edge(n2i[x], n2i[y], distance=dist)

    tempC = C.copy()
    tempC.remove_edges_from([e[:2] for e in tempC.edges(
        data='distance') if not np.isclose(0, e[2])])
    to_merge = [nodes for nodes in nx.connected_components(
        tempC) if len(nodes) > 1]
    del(tempC)

    for nodes in to_merge:
        members = []
        for nid in nodes:
            members.extend(C.node[nid]['members'])
        smallG = nx.subgraph(G, members)
        for e in smallG.edges():
            G[e[0]][e[1]]['level'] = 0

        parts = [list(nlist) for nlist in nx.connected_components(smallG)]
        for i in range(1, len(parts)):
            e = [parts[i-1][0], parts[i][0]]
            G.add_edge(e[0], e[1])
            G[e[0]][e[1]]['level'] = 0

        newMembers = list(set(members))

        newHist = C.node[n2i[newMembers[0]]]['histogram']
        for i in range(1, len(newMembers)):
            newHist = newHist+C.node[n2i[newMembers[i]]]['histogram']

        newNodeId += 1
        C.add_node(newNodeId)
        C.node[newNodeId]['members'] = newMembers
        C.node[newNodeId]['histogram'] = newHist
        # triangular inequality
        for c in nodes:
            for n in C.neighbors(c):
                if (n not in nodes) and ('distance' in C[c][n]):
                    C.add_edge(newNodeId, n, distance=C[c][n]['distance'])
        C.remove_nodes_from(nodes)

    curThreshold = THR_START

    while len(C) > nx.number_connected_components(G):
        H = []
        for e in C.edges():
            if ('distance' not in C[e[0]][e[1]]) or (C[e[0]][e[1]]['distance'] == -1):
                dist = _clusterDistance(C, e[0], e[1], layer=layer)
                C[e[0]][e[1]]['distance'] = dist
            else:
                dist = C[e[0]][e[1]]['distance']
                
            v = (min([len(C.node[e[0]]['members']), len(C.node[e[1]]['members'])]),
                 dist,
                 e[0],
                 e[1])
                
            H.append(v)
        heapify(H)

        dMin = H[0][1]
        dMax = max([v[1] for v in H])
        print(len(C), curThreshold, len(H), dMin, dMax)

        while (dMin >= curThreshold):
            curThreshold += THR_STEP

        if np.isclose(curThreshold, 1) or np.isclose(dMin, dMax):
            print('last')
            for e in G.edges():
                if G[e[0]][e[1]]['level'] == -1:
                    G[e[0]][e[1]]['level'] = curThreshold
            return(G)

        while len(H) > 0:
            # already merged before
            while (len(H) > 0):
                (_, v, x, y) = heappop(H)
                if  (v < curThreshold) and (x in C) and (y in C):
                    break
            else:
                break

            XE = set([(min(e), max(e)) for e in G.edges(C.node[x]['members'])])
            YE = set([(min(e), max(e)) for e in G.edges(C.node[y]['members'])])
            rE = list(XE.intersection(YE))
            if not rE:  # knn edge
                e = (C.node[x]['members'][0], C.node[y]['members'][0])
                G.add_edge(e[0], e[1])
                G[e[0]][e[1]]['level'] = curThreshold
            else:
                for e in list(rE):
                    G[e[0]][e[1]]['level'] = curThreshold

            newMembers = C.node[x]['members']+C.node[y]['members']
            newHist = C.node[x]['histogram']+C.node[y]['histogram']

            newNodeId += 1
            C.add_node(newNodeId)
            C.node[newNodeId]['members'] = newMembers
            C.node[newNodeId]['histogram'] = newHist
            newNeighbors = set(list(C.neighbors(x))+list(C.neighbors(y)))
            newNeighbors.discard(x)
            newNeighbors.discard(y)
            C.remove_nodes_from([x, y])
            for n in newNeighbors:
                C.add_edge(newNodeId, n, distance=-1)

    return(G)
