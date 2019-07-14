from upload import gatherInfoJsons_AsDict
from os.path import join
import networkx as nx
from itertools import combinations

import matplotlib.pylab as plt
from numpy import median
from joblib import Memory

from itertools import combinations
from tqdm import tqdm


cachedir = './cache/'
memory = Memory(cachedir, verbose=0)


def _plotHier(H, threshold: float = 0.5):
    pos = {}
    for n in H:
        pos[n] = H.node[n]['pos'][:2]
    nx.draw_networkx_nodes(H, pos=pos, node_size=2)
    nx.draw_networkx_edges(H, pos=pos, edgelist=[e for e in H.edges(
        data='level') if e[2] < threshold], edge_color='blue')
    nx.draw_networkx_edges(H, pos=pos, edgelist=[e for e in H.edges(
        data='level') if e[2] >= threshold], edge_color='red')


def compareHierarchies(ds: dict, a1, a2, g1: str = None, g2: str = None, level: str = 'level') -> float:
    """
        Computes a distance between hierarchies/aspects a1 and a2.

        if a1/a2 are strings, the hierarchy is read from the datastore.

        if they are graphs, they are used directly. Then g1/g2 are necessary.

        ds: the current datastore.

        Returns 0-1.
    """

    if not isinstance(a1, nx.Graph):
        g1 = ds.getGeometry(a1)
        G1 = ds.getHierarchy(a1)
    else:
        G1 = a1
        assert(g1 is not None)

    if not isinstance(a2, nx.Graph):
        g2 = ds.getGeometry(a2)
        G2 = ds.getHierarchy(a2)
    else:
        G2 = a2
        assert(g2 is not None)

    D = 0
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

    # each edge contributes to a maximum of 1
    # (although a distance of 1 seems unlikely)
    return(D/len(G1.edges()))

# @profile


def _hierMerge(G1: nx.Graph, G2: nx.Graph, X: nx.Graph, level: str = 'level') -> nx.Graph:
    """
    Merges two different hierarchies represented by G1 and G2. 

    X: CrossGeometry from G1 to G2.
    Level is the data label associated with the edge representing the hierarchical level of joining (0-1).

    -> Always returns a new graph (same topology as G1 - unless G1 is None).
    """

    if (G1 is None) and (G2 is not None):
        return(G2.copy())
    if (G1 is not None) and (G2 is None):
        return(G1.copy())

    H = G1.copy()
    for e in H.edges():
        otherside = []
        for n in e:
            if n in X:
                otherside.extend(X.neighbors(n))
        if otherside:
            H[e[0]][e[1]][level] = max(
                [H[e[0]][e[1]][level], ]+[x[2] for x in G2.subgraph(otherside).edges(data=level)])


    # print(list(G1.nodes())[0])
    # print(list(G2.nodes())[0])
    for lvl in [0.1, 0.25, 0.5,0.75, 0.8, 0.9]:
        C = G2.copy()
        C.remove_edges_from([e[:2]
                             for e in C.edges(data=level) if e[2] >= lvl])
        for cc, nodes in enumerate(nx.connected_components(C)):
            for n in nodes:
                C.node[n]['cc'] = cc

        R = H.copy()
        R.remove_edges_from([e[:2]
                             for e in R.edges(data=level) if e[2] >= lvl])

        for cc, nodes in enumerate(nx.connected_components(R)):
            for n in nodes:
                R.node[n]['cc'] = cc

        for e in R:
            pass
    return(H)

# @profile


def _mergeAll(ds: dict, aspects: list, level: str = 'level', bbox: list = None) -> nx.Graph:
    F = None
    for a in aspects:
        G = ds.getHierarchy(a, bbox=bbox)
        curGeometry = ds.getGeometry(a)
        if F is None:
            F = G
        else:
            cX = ds.getCrossGeometry(curGeometry, lastGeometry)
            F = _hierMerge(F, G, cX, level=level)
        lastGeometry = curGeometry
    return(F)


# @memory.cache(ignore=['ds'])
# @profile
def mapHierarchies(ds: dict, aspects: list, level: str = 'level', bbox: list = None) -> dict:
    """
    ds: datastore 
    aspects:  list of aspects(hierarchies) [a1,a2,...] 
    level: key for the data
    bbox: limiting bounding box to consider only regions inside it. (integers == better caching)

    Returns the resulting hierarchy represented in all involved geometries
    """
    print('=-=', aspects)

    aspectsByGeometry = {}
    for aspect in aspects:
        g = ds.getGeometry(aspect)
        if g not in aspectsByGeometry:
            aspectsByGeometry[g] = []
        aspectsByGeometry[g].append(aspect)

    geoms = sorted(aspectsByGeometry.keys())
    merged = []
    for g in geoms:
        merged.append(
            _mergeAll(ds, aspectsByGeometry[g], level=level, bbox=bbox))

    # holds the resulting hierarchy on each original geometry
    # - This could be faster if the partial merges were reused
    final = {}
    if len(geoms) > 1:
        for i in range(len(geoms)):
            backwards = None
            forwards = None

            if i != (len(geoms)-1):
                backwards = merged[-1]
                for j in range(len(geoms)-2, i-1, -1):
                    backwards = _hierMerge(merged[j], backwards, ds.getCrossGeometry(
                        geoms[j], geoms[j+1]), level=level)

            if i != 0:
                forwards = merged[0]
                for j in range(1, i+1):
                    forwards = _hierMerge(merged[j], forwards, ds.getCrossGeometry(
                        geoms[j], geoms[j-1]), level=level)

            final[geoms[i]] = _hierMerge(
                backwards, forwards, ds.getCrossGeometry(geoms[i], geoms[i]), level=level)
    else:
        final[geoms[0]] = merged[0]

    return(final)
