from upload import gatherInfoJsons_AsDict
from os.path import join
import networkx as nx
from util import crossGeomFileName
from itertools import combinations

import matplotlib.pylab as plt
from numpy import median

def compareHierarchies(conf: dict, a1: str, a2: str, level: str = 'level') -> float:
    """
        Computes a distance between hierarchies/aspects a1 and a2.
        Returns 0-1.
    """
    aspectInfo = gatherInfoJsons_AsDict(conf['data'])

    g1 = aspectInfo[a1]['geometry']
    g2 = aspectInfo[a2]['geometry']

    G1 = _read_and_normalize(join(conf['data'], a1+'.gp'))
    G2 = _read_and_normalize(join(conf['data'], a2+'.gp'))

    D = 0

    if g1 != g2:
        X = nx.read_gpickle(join(conf['folder'], crossGeomFileName(g1, g2)))
        for e in G1.edges():
            otherside = []
            for ee in e:
                if ee in X:
                    otherside.extend(X.neighbors(ee))
            if otherside:
                g2p = G2.subgraph(otherside)
                if len(g2p.edges()) > 0:
                    D += abs(G1[e[0]][e[1]][level]-max([x[2] for x in g2p.edges(data=level)]))
    else:
        for e in G1.edges():
            D += abs(G1[e[0]][e[1]][level] - G2[e[0]][e[1]][level])
    #each edge contributes to a maximum of 1
    #(although a distance of 1 seems unlikely)
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
                else:
                    print('not found ', ee)
            if otherside:
                g2p = G2.subgraph(otherside)
                H[e[0]][e[1]][level] = max(
                    [H[e[0]][e[1]][level], ]+[x[2] for x in g2p.edges(data=level)])
    return(H)


def _getMaxLevel(G: nx.Graph, level: str = 'level') -> int:
    return(max([x[2] for x in G.edges(data=level)]))


def _read_and_normalize(PickledGraphPath: str, level: str = 'level') -> nx.Graph:
    G = nx.read_gpickle(PickledGraphPath)
    m = _getMaxLevel(G, level)
    for e in G.edges():
        G[e[0]][e[1]][level] /= m
    return(G)


def _mergeAll(conf: dict, aspects: list, aspectInfo: dict) -> nx.Graph:
    F = None
    for a in aspects:
        G = _read_and_normalize(join(conf['data'], a+'.gp'))

        if F is None:
            F = G
        else:
            curGeometry = aspectInfo[a]['geometry']
            if (curGeometry != lastGeometry):  # pylint: disable=used-before-assignment
                cX = nx.read_gpickle(
                    join(conf['folder'], crossGeomFileName(curGeometry, lastGeometry)))
            else:
                cX = None
            F = _hierMerge(F, G, cX)

        lastGeometry = aspectInfo[a]['geometry']
    return(F)


def mapHierarchies(conf: dict, aspects: list, thresholds: list = [0.8, 0.6, 0.4, 0.2]) -> dict:
    """
    conf: base configuration from srv.py
    aspects: list of list of aspects (hierarchies) [ [a1,a2], [a3,a4], ] 
    thresholds: _lists_ of cutting points for the normalized hierarchies.

    This function will merge the aspects in the sublists returning the connected
    components for each in their original geometries.
    """
    if len(aspects) < 2:
        print('mapHierarchies - need at least 2 geometries/bases')
        return({})

    aspectInfo = gatherInfoJsons_AsDict(conf['data'])
    print('starting individual merges')

    geoms = []
    merged = []
    # merge "projects" everyone into the first geom on the list
    for sublist in aspects:
        merged.append(_mergeAll(conf, sublist, aspectInfo))
        geoms.append(aspectInfo[sublist[0]]['geometry'])

    allCrosses = {}
    for g1, g2 in combinations(set(geoms), 2):
        fname = crossGeomFileName(g1, g2)
        if fname not in allCrosses:
            allCrosses[fname] = nx.read_gpickle(join(conf['folder'], fname))
    for g1 in set(geoms):
        allCrosses[crossGeomFileName(g1,g1)]=None

    # holds the resulting hierarchy on each original geometry
    print('final merges')
    final = []
    for i, g1 in enumerate(geoms):
        backwards = None
        forwards = None

        # print('doing i=',i)
        if i != (len(geoms)-1):
            backwards = merged[-1]
            for j in range(len(geoms)-2, i-1, -1):
                # print('j',j,geoms[j],geoms[j+1])
                backwards = _hierMerge(
                    merged[j], backwards, allCrosses[crossGeomFileName(geoms[j], geoms[j+1])])

        if i != 0:
            forwards = merged[0]
            for j in range(1, i+1):
                # print('j',j,geoms[j],geoms[j-1])
                forwards = _hierMerge(
                    merged[j], forwards, allCrosses[crossGeomFileName(geoms[j], geoms[j-1])])

        # same geometry, no cross needed
        final.append(_hierMerge(backwards, forwards))

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
            curX = allCrosses[crossGeomFileName(geoms[i], geoms[i+1])]

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
