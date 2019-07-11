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
from sortedEdges import SortedEdges

NBINS = 100
THR_STEP = 0.10
THR_START = 0.10


def _clusterDistance(G, x, y, layer):
    h1 = G.node[x]['histogram']
    h2 = G.node[y]['histogram']
    if np.any(np.isnan(h1)) or np.any(np.isnan(h2)):
        return(1)

    s1 = np.sum(h1)
    if (s1 > 0):
        h1 = h1/s1

    s2 = np.sum(h2)
    if (s2 > 0):
        h2 = h2/s2
    # X2 = np.cumsum(h2)

    # D = np.sum(np.abs(X1-X2))/NBINS
    # D = cosine(h1,h2)
    D = euclidean(h1, h2)/np.sqrt(2)

    return(D)


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
        if (layer not in G.node[n]) or (G.node[n][layer] is None) or np.any(np.isnan(G.node[n][layer])):
            to_remove.append(n)
            continue
        i2n[i] = n
        cData.append(G.node[n][layer])
        i += 1
    cData = np.array(cData)

    G.remove_nodes_from(to_remove)
    for e in G.edges():
        G[e[0]][e[1]]['level'] = -1

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
    # extra_edges = [(i2n[A[0][i]], i2n[A[1][i]]) for i in range(A[0].shape[0])]
    # extra_edges = [e for e in extra_edges if not G.has_edge(
    #     e[0], e[1])]  # only non-existing links

    extra_edges=[]
    # print(G.node[firstNode][layer])

    if NDIMS == 1:
        minVal = G.node[firstNode][layer][0]
        maxVal = G.node[firstNode][layer][0]

    # nToVisit = []

    C = nx.Graph()
    C.add_nodes_from(G.nodes())

    for n in G.nodes():
        C.node[n]['members'] = [n, ]
        if (G.node[n][layer] is not None):
            if NDIMS == 1:
                minVal = min((minVal, G.node[n][layer][0]))
                maxVal = max((maxVal, G.node[n][layer][0]))
    if NDIMS == 1:
        print('Value range: {0}-{1}'.format(minVal, maxVal))
        for n in G():
            C.node[n]['histogram'] = _createHist(
                G.node[n][layer], minVal, maxVal,)
    else:
        for n in G:
            C.node[n]['histogram'] = G.node[n][layer][:]

    print('computing distances')
    for (x, y) in tqdm(list(G.edges())+extra_edges):
        dist = _clusterDistance(C, x, y, layer=layer)
        C.add_edge(x, y, distance=dist)

    tempC = C.copy()
    tempC.remove_edges_from([e[:2] for e in tempC.edges(
        data='distance') if not np.isclose(0, e[2])])
    to_merge = [nodes for nodes in nx.connected_components(
        tempC) if len(nodes) > 1]
    del(tempC)

    newNodeId = 0
    for nodes in to_merge:
        members = []
        for n in nodes:
            members.extend(C.node[n]['members'])
        smallG = nx.subgraph(G, members)
        for e in smallG.edges():
            G[e[0]][e[1]]['level'] = 0

        parts = [list(nlist) for nlist in nx.connected_components(smallG)]
        for i in range(1, len(parts)):
            e = [parts[i-1][0], parts[i][0]]
            G.add_edge(e[0], e[1])
            G[e[0]][e[1]]['level'] = 0

        newMembers = list(set(members))

        newHist = C.node[newMembers[0]]['histogram']
        for i in range(1, len(newMembers)):
            newHist = newHist+C.node[newMembers[i]]['histogram']

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

    SE = SortedEdges()
    SE.batch_add([(
        (C[x][y]['distance'],
         min([len(C.node[x]['members']), len(C.node[y]['members'])])),
        x, y) for (x, y) in tqdm(C.edges())])
    curThreshold = THR_START

    while len(C) > 1:
        dMin = SE.minVal()[0][0]
        dMax = SE.maxVal()[0][0]
        print(len(C), dMin, dMax)
        if np.isclose(dMin, dMax):
            for e in G.edges():
                if G[e[0]][e[1]]['level'] == -1:
                    G[e[0]][e[1]]['level'] = curThreshold

        while (dMin > curThreshold):
            curThreshold += THR_STEP
            continue

        touched = {}
        backlog = []
        while len(SE)>0:
            while len(SE) > 0:
                (v, x, y) = SE.pop()
                newNeighbors = set(list(C.neighbors(x))+list(C.neighbors(y)))
                if (v[0] >= curThreshold):
                    break
                if any([c in touched for c in newNeighbors]):
                    touched[x]=True
                    touched[y]=True
                    backlog.append((v, x, y))
                else:
                    break

            if (v[0] >= curThreshold):
                backlog.append((v, x, y))
                SE.batch_add(backlog)
                break

            for c in newNeighbors:
                touched[c] = True

            SE.remove([x, y])
            # assert(len([i for i in range(len(SE._data)) if x in SE._data[i].val and i not in SE._frees])==0)
            # assert(len([i for i in range(len(SE._data)) if y in SE._data[i].val and i not in SE._frees])==0)
            assert(not any([x in backlog[i] for i in range(len(backlog))]))
            assert(not any([y in backlog[i] for i in range(len(backlog))]))

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
            newNeighbors.discard(x)
            newNeighbors.discard(y)

            for n in newNeighbors:
                v = ((_clusterDistance(C, newNodeId, n, layer=layer), min(
                    [len(C.node[x]['members']), len(C.node[y]['members'])])), newNodeId, n)
                SE.add(v)
                C.add_edge(newNodeId, n)

            C.remove_nodes_from([x, y])
            # print(len(C))

    return(G)
