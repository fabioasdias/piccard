from collections import defaultdict

import matplotlib.pylab as plt
import networkx as nx
from joblib import Memory

from numpy import histogram, median

import logging
# from dataStore import dataStore

cachedir = './cache/'
memory = Memory(cachedir, verbose=0)


logging.basicConfig(filename='hier.log', level=logging.DEBUG)

def _plotHier(H):
    pos = {}
    for n in H:
        pos[n] = H.node[n]['pos'][:2]

    cmap=plt.cm.Blues
    E = [e for e in H.edges(data='level')]
    vmin=0
    vmax=1
    nx.draw_networkx_nodes(H, pos=pos, node_size=2)
    nx.draw_networkx_edges(H, pos=pos, edgelist=E, edge_color=[e[2] for e in E], edge_cmap=cmap,
           with_labels=False, vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = vmin, vmax=vmax))
    sm._A = []
    plt.colorbar(sm)

def compareHierarchies(ds, a1, a2, g1: str = None, g2: str = None, level: str = 'level') -> float:
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


# def _hierMerge(G1: nx.Graph, G2: nx.Graph, X: nx.Graph, level: str = 'level') -> nx.Graph:
#     """
#     Merges two different hierarchies represented by G1 and G2.

#     X: CrossGeometry from G1 to G2.
#     Level is the data label associated with the edge representing the hierarchical level of joining (0-1).

#     -> Always returns a new graph (same topology as G1 - unless G1 is None).
#     """

#     if (G1 is None) and (G2 is not None):
#         return(G2.copy())
#     if (G1 is not None) and (G2 is None):
#         return(G1.copy())

#     H = G1.copy()
#     for e in tqdm(H.edges(),desc='edges hier'):
#         otherside = []
#         for n in e:
#             if n in X:
#                 otherside.extend(X.neighbors(n))
#         if otherside:
#             H[e[0]][e[1]][level] = max(
#                 [H[e[0]][e[1]][level], ]+[x[2] for x in G2.subgraph(otherside).edges(data=level)])

#     # plt.hist([e[2] for e in G1.edges(data='level')])
#     # plt.axis([0, 1, 0, len(G1.edges())])
#     # plt.title('G1')

#     # plt.figure()
#     # plt.hist([e[2] for e in G2.edges(data='level')])
#     # plt.axis([0, 1, 0, len(G2.edges())])
#     # plt.title('G2')

#     # plt.figure()
#     # plt.hist([e[2] for e in H.edges(data='level')])
#     # plt.axis([0, 1, 0, len(H.edges())])
#     # plt.title('H')

#     # plt.show()


#     return(H)

# @profile


def _mergeAll(ds, aspects: list,
              level: str = 'level',
              hist: str = 'hist',
              bbox: list = None) -> nx.Graph:
    """
    Creates a nx.Graph output with the levels of all involved aspects associated to the edges. 
    :param aspects: list of aspect id, ON THE SAME GEOMETRY
    """
    logger = logging.getLogger()
    assert(len(set([ds.getGeometry(a) for a in aspects])) == 1)
    logger.debug([ds.getGeometry(a) for a in aspects])
    F = nx.Graph()
    for a in aspects:
        logger.debug('Starting {a}:{name}'.format(a=a,name=ds.getAspectName(a)))
        G = ds.getHierarchy(a, bbox=bbox)

        plt.figure()
        _plotHier(G)
        plt.title(ds.getAspectName(a))
        
        for n in G:
            F.add_node(n)
            for k in G.node[n]:
                F.node[n][k]=G.node[n][k]
        # F.add_nodes_from(G.nodes())
        logger.debug('#F {nf}, {ef} #G {ng}, {eg}'.format(nf=len(F),ef=len(F.edges()),ng=len(G),eg=len(G.edges())))

        for e in G.edges():
            logger.debug('Looking at edge {e}'.format(e=str(e[0])+'-'+str(e[1])))
            #Hierarchies can have different edges because of NaNs (all involved edges get removed)
            if (not F.has_edge(e[0], e[1])):
                logger.debug('New edge for F')
                F.add_edge(e[0], e[1], _combined=[])
            logger.debug('Adding {newVal} to {combined}'.format(newVal=G[e[0]][e[1]][level],combined=str(F[e[0]][e[1]]['_combined'])))
            F[e[0]][e[1]]['_combined'].append(G[e[0]][e[1]][level])

    logger.debug('----Merge finished----')
    for e in F.edges():
        logger.debug('Looking at edge {e}'.format(e=str(e[0])+'-'+str(e[1])))
        combined = F[e[0]][e[1]]['_combined']
        # try:
        #     assert(len(combined)==len(aspects))
        # except :
        #     print(e)
        #     print(len(aspects), combined)
        #     raise
        F[e[0]][e[1]][level] = min(combined)
        H, _ = histogram(combined, range=(0,1))
        F[e[0]][e[1]][hist] = list(H/sum(H))
        logger.debug('combined '+str(combined))
        logger.debug('hist '+str(list(F[e[0]][e[1]][hist])))
        logger.debug('level '+str(F[e[0]][e[1]][level]))

        
        if (F[e[0]][e[1]][level] > 1):
            # sometimes rounding can lead to 1.0000000000000002
            F[e[0]][e[1]][level] = 1

    plt.figure()
    _plotHier(F)
    plt.title('merged')


    # vals = [e[2] for e in F.edges(data=level)]
    # assert((max(vals) <= 1)and(min(vals)>=0))
    # plt.hist(vals)
    # plt.title('-'.join([ds.getAspectName(a) for a in aspects]))
    plt.show()

    return(F)


@memory.cache(ignore=['ds'])
def mapHierarchies(ds, aspects: list, level: str = 'level', hist='hist', bbox: list = None) -> dict:
    """
    ds 
    :param aspects:  list of aspects(hierarchies) [a1,a2,...] 
    :param level: key for the data
    :param bbox: limiting bounding box to consider only regions inside it. (integers == better caching)
    :param hist: key for the histogram output vector associated with each edge

    Returns the resulting hierarchy represented in all involved geometries/years
    """
    print('=-=', aspects)

    aspectsByYearGeometry = defaultdict(list)
    for aspect in aspects:
        aspectsByYearGeometry[(ds.getAspectYear(
            aspect), ds.getGeometry(aspect))].append(aspect)

    merged = {}
    years_geoms = sorted(aspectsByYearGeometry.keys())
    for yg in years_geoms:
        merged[yg] = _mergeAll(ds, aspectsByYearGeometry[yg],
                               level=level, hist=hist, bbox=bbox)

    return(merged)
