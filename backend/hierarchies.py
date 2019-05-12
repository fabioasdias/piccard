from upload import gatherInfoJsons_AsDict
from os.path import join
import networkx as nx
from itertools import combinations

import matplotlib.pylab as plt
from numpy import median
from joblib import Memory

cachedir = './cache/'
memory = Memory(cachedir, verbose=0)

#the datastore identifies the country, but the aspect IDs are unique, so it
#doesnt really matter for the cache
@memory.cache(ignore=['ds'])
def compareHierarchies(ds: dict, a1: str, a2: str, level: str = 'level') -> float:
    """
        Computes a distance between hierarchies/aspects a1 and a2.
        ds: the corresponding datastore (conf['ds'])
        Returns 0-1.
    """

    # ds= conf['ds']
    g1 = ds.getGeometry(a1)
    g2 = ds.getGeometry(a2)

    G1 = ds.getHierarchy(a1)
    G2 = ds.getHierarchy(a2)

    D = 0

    if g1 != g2:
        X = ds.getCrossGeometry(g1, g2)
        for e in G1.edges():
            otherside = []
            for ee in e:
                if ee in X:
                    otherside.extend(X.neighbors(ee))
            if otherside:
                g2p = G2.subgraph(otherside)
                if len(g2p.edges()) > 0:
                    D += abs(G1[e[0]][e[1]][level]-max([x[2]
                                                        for x in g2p.edges(data=level)]))
    else:
        for e in G1.edges():
            D += abs(G1[e[0]][e[1]][level] - G2[e[0]][e[1]][level])
    # each edge contributes to a maximum of 1
    # (although a distance of 1 seems unlikely)
    return(D/len(G1.edges()))


def _hierMerge(G1: nx.Graph, G2: nx.Graph, X: nx.Graph = None, level: str = 'level') -> nx.Graph:
    """
    Merges two different hierarchies represented by G1 and G2. 
    Cross geometry represented by X. Level is the data label associated 
    with the edge representing the hierarchical level of joining (0-1).
    -> Always returns a new graph.
    """

    if (G1 is None) and (G2 is not None):
        return(G2.copy())
    if (G1 is not None) and (G2 is None):
        return(G1.copy())

    H = G1.copy()
    if (X is None):
        for e in H.edges():
            H[e[0]][e[1]][level] = max(
                [H[e[0]][e[1]][level], G2[e[0]][e[1]][level]])
    else:
        for e in H.edges():
            otherside = []
            for ee in e:
                if ee in X:
                    otherside.extend(X.neighbors(ee))
            if otherside:
                g2p = G2.subgraph(otherside)
                H[e[0]][e[1]][level] = max(
                    [H[e[0]][e[1]][level], ]+[x[2] for x in g2p.edges(data=level)])
    return(H)


def _mergeAll(ds: dict, aspects: list) -> nx.Graph:
    F = None
    for a in aspects:
        G = ds.getHierarchy(a)

        if F is None:
            F = G
        else:
            curGeometry = ds.getGeometry(a)
            if (curGeometry != lastGeometry):  # pylint: disable=used-before-assignment
                cX = ds.getCrossGeometry(curGeometry, lastGeometry)
            else:
                cX = None
            F = _hierMerge(F, G, cX)

        lastGeometry = ds.getGeometry(a)
    return(F)

@memory.cache(ignore=['ds'])
def mapHierarchies(ds: dict, aspects: list, thresholds: list = [0.8, 0.6, 0.4, 0.2]) -> dict:
    """
    ds: datastore from srv.py (conf['ds'])
    aspects:  list of aspects (hierarchies) [a1,a2,...] 
    thresholds: _lists_ of cutting points for the normalized hierarchies.

    This function will merge the aspects in the sublists returning the connected
    components for each in their original geometries.
    """
    print('=-=', aspects)


    aspectsByGeometry = {}
    for aspect in aspects:
        g = ds.getGeometry(aspect)
        if g not in aspectsByGeometry:
            aspectsByGeometry[g]=[]
        aspectsByGeometry[g].append(aspect)


    geoms = sorted(aspectsByGeometry.keys())
    merged = []
    for g in geoms:
        merged.append(_mergeAll(ds, aspectsByGeometry[g]))

    # holds the resulting hierarchy on each original geometry
    # - This could be faster if the partial merges were reused
    final = []
    if len(geoms)>1:
        for i in range(len(geoms)):
            backwards = None
            forwards = None

            if i != (len(geoms)-1):
                backwards = merged[-1]
                for j in range(len(geoms)-2, i-1, -1):
                    backwards = _hierMerge(merged[j], backwards, ds.getCrossGeometry(geoms[j], geoms[j+1]))

            if i != 0:
                forwards = merged[0]
                for j in range(1, i+1):
                    forwards = _hierMerge(merged[j], forwards, ds.getCrossGeometry(geoms[j], geoms[j-1]))

            # same geometry, no cross needed
            final.append(_hierMerge(backwards, forwards))
    else:
        final.append(merged[0])

    ret = {}
    for i, g in enumerate(geoms):
        ret[g] = {}
        for n in final[i]:
            ret[g][n[1]] = []

    for threshold in thresholds:
        for i, g in enumerate(geoms):
            final[i].remove_edges_from(
                [e[:2] for e in final[i].edges(data='level') if (e[2] > threshold)])
            for cc, nodes in enumerate(nx.connected_components(final[i])):
                for n in nodes:
                    ret[g][n[1]].append(cc)

    return(ret)

    # computes all possible paths

    for i in range(len(final)):
        for cc, nodes in enumerate(nx.connected_components(final[i])):
            for n in nodes:
                final[i].node[n]['used'] = False

    paths = []
    todo = []
    for i in range(len(final)):
        todo.extend([[n, ] for n in final[i].nodes()
                     if not final[i].node[n]['used']])

        if (i == (len(final)-1)):
            paths.extend(todo)
        else:
            curX = ds.getCrossGeometry(geoms[i], geoms[i+1])

            notDone = []
            for cpath in todo:
                options = []

                if (cpath[-1] in curX):
                    options = list(curX.neighbors(cpath[-1]))

                if options:
                    for op in options:
                        final[i+1].node[op]['used'] = True
                        notDone.append(cpath+[op, ])
                else:
                    paths.append(cpath)  # nowhere to go
            todo = notDone

    with open('nothing.txt', 'w') as fout:
        for p in paths:
            fout.write(
                ' '.join(['({0},{1})'.format(n[0], n[1]) for n in p])+'\n')
    return({})
