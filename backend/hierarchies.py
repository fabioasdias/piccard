from upload import gatherInfoJsons_AsDict
from os.path import join
import networkx as nx
from util import crossGeomFileName
from itertools import combinations

import matplotlib.pylab as plt


def _hierMerge(G1:nx.Graph, G2: nx.Graph, X :nx.Graph = None, level:str='level') -> nx.Graph:
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

    H=G1.copy()
    if (X is None):
        for e in H.edges():
            H[e[0]][e[1]][level]=max([H[e[0]][e[1]][level],G2[e[0]][e[1]][level]])
    else:
        for e in H.edges():
            g2p=G2.subgraph(list(X.neighbors(e[0]))+list(X.neighbors(e[1])))
            H[e[0]][e[1]][level]=max([H[e[0]][e[1]][level],]+[x[2] for x in g2p.edges(data=level)])
    return(H)
        

def _getMaxLevel(G:nx.Graph, level:str='level')-> int:
    return(max([x[2] for x in G.edges(data=level)]))

def _read_and_normalize(PickledGraphPath:str, level:str='level')->nx.Graph:
    G=nx.read_gpickle(PickledGraphPath)
    m=_getMaxLevel(G,level)
    for e in G.edges():
        G[e[0]][e[1]][level]/=m
    return(G)

def _mergeAll(conf:dict,aspects:list,aspectInfo:dict)->nx.Graph:
    F=None
    for a in aspects:
        G=_read_and_normalize(join(conf['data'],a+'.gp'))
        
        if F is None:
            F=G
        else:
            curGeometry=aspectInfo[a]['geometry']
            if (curGeometry!=lastGeometry): #pylint: disable=used-before-assignment
                X=nx.read_gpickle(join(conf['folder'],crossGeomFileName(curGeometry,lastGeometry)))
            else:
                X=None
            F=_hierMerge(F,G,X)

        lastGeometry=aspectInfo[a]['geometry']                
    return(F)

def mapHierarchies(conf:dict, aspects:list, threshold:float=0.5) -> dict:
    """
    conf: base configuration from srv.py
    aspects: list of list of aspects (hierarchies) [ [a1,a2], [a3,a4], ] 
    threshold: where to cut the resulting hierarchies

    This function will merge the aspects in the sublists and compare them across the lists
    """
    if len(aspects)<2:
        print('mapHierarchies - need at least 2 geometries/bases')
        return({})

    temp=gatherInfoJsons_AsDict(conf['data'])
    aspectInfo={}
    for sublist in aspects:
        for a in sublist:
            possibles=[x for x in temp if (x['id']==a)]
            if possibles:
                aspectInfo[a]=possibles[0]
    del(temp)

    print('starting merges From')

    geoms=[]
    merged=[]
    #merge "projects" everyone into the first geom on the list
    for sublist in aspects:
        merged.append(_mergeAll(conf,sublist,aspectInfo))
        geoms.append(aspectInfo[sublist[0]]['geometry'])

    
    X={}
    for g1,g2 in combinations(set(geoms)):
        X[crossGeomFileName(g1,g2)]=nx.read_gpickle(join(conf['folder'],crossGeomFileName(g1,g2)))

    #holds the resulting hierarchy on each original geometry
    print('final merges')
    final=[]
    for i,g1 in enumerate(geoms):
        backwards = None
        forwards = None
        
        if i != (len(geoms)-1):
            backwards = merged[-1]
            for j in range(len(geoms)-2,i-1,-1):
                backwards = _hierMerge(merged[j], backwards, X[crossGeomFileName(geoms[j],geoms[j+1])])

        if i != 0:
            forwards = merged[0]
            for j in range(1, i+1):
                forwards = _hierMerge(merged[j], forwards, X[crossGeomFileName(geoms[j],geoms[j-1])])

        final.append(_hierMerge(backwards, forwards)) #same geometry, no cross needed

    print('removing >',threshold)

    for i in range(len(final)):
        final[i].remove_edges_from([e[:2] for e in final[i].edges(data='level') if (e[2]>threshold)])
        for cc, n in nx.connected_components(final[i]):
            final[i].node[n]['cc']=cc
            final[i].node[n]['used']=False
    

    paths=[]
    for i in range(len(final)):
        if (i!=(len(final)-1)):
            curX=X[crossGeomFileName(geoms[i],geoms[i+1])]
            

        todo=[n for n in final[i].nodes() if not final[i].node[n]['used']]
        while todo:
            cpath=todo.pop(0)
            options=[]

            if (i!=(len(final)-1)):
                options=curX.neighbors(cpath[-1])

            if not options:
                paths.append(cpath)
                print(cpath)
            else:
                for op in options:
                    final[i+1].node[op]['used']=True
                    todo.append(cpath+[op,])
    return({})
    
    