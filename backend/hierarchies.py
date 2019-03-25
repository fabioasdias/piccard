from upload import gatherInfoJsons
from os.path import join
import networkx as nx
from util import crossGeomFileName


import matplotlib.pylab as plt


def _hierMerge(G1:nx.Graph, G2: nx.Graph, X :nx.Graph = None, level:str='level') -> nx.Graph:
    """Merge two different hierarchies represented by G1 and G2. 
       Cross geometry represented by X. Level is the data label associated 
       with the edge representing the hierarchical level of joining (0-1)"""

    H=G1.copy()
    if (X is None):
        for e in H.edges():
            H[e[0]][e[1]][level]=max([H[e[0]][e[1]][level],G2[e[0]][e[1]][level]])
    else:
        for e in H.edges():
            g2p=G2.subgraph(list(X.neighbors(e[0]))+list(X.neighbors(e[1])))
            H[e[0]][e[1]][level]=max([H[e[0]][e[1]][level],]+[x[2] for x in g2p.edges(data=level)])
    return(H)
        

def _getMaxLevel(G:nx.Graph,level:str='level')-> int:
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
        G=_read_and_normalize(join(conf['aspects'],a+'.gp'))
        
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

def learnPredictions(conf:dict, FromAspects:list, ToAspects:list) -> dict:
    temp=gatherInfoJsons(conf['raw'])
    aspectInfo={}
    for a in FromAspects+ToAspects:
        possibles=[x for x in temp if (x['id']==a)]
        if possibles:
            aspectInfo[a]=possibles[0]
    del(temp)

    print('starting merges From')

    #merge "projects" everyone into the first geom on the list
    F=_mergeAll(conf,FromAspects,aspectInfo)
    FG=aspectInfo[FromAspects[0]]['geometry']

    print('starting merges To')

    T=_mergeAll(conf,ToAspects,aspectInfo)
    TG=aspectInfo[ToAspects[0]]['geometry']
    
    if (TG!=FG):
        X=nx.read_gpickle(join(conf['folder'],crossGeomFileName(TG,FG)))
    else:
        X=None

    print('final merges')
    #resulting hierarchy using both geometries as base
    RF=_hierMerge(F,T,X)
    RT=_hierMerge(T,F,X)

    print('removing >0.5')
    
    RF.remove_edges_from([e[:2] for e in RF.edges(data='level') if (e[2]>0.5)])
    RT.remove_edges_from([e[:2] for e in RT.edges(data='level') if (e[2]>0.5)])

    print('all Rs ready')

    matches=[]

    for GF in nx.connected_component_subgraphs(RF):
        otherside=[]
        for n in GF.nodes():
            otherside.extend(X.neighbors(n))

        GT = max(nx.connected_component_subgraphs(nx.subgraph(RT,otherside)), key=len)
        matches.append([list(GF.nodes()),list(GT.nodes())])
            





    res={}
    N=nx.number_connected_components(RF)
    S=[]
    for i,GG in enumerate(nx.connected_component_subgraphs(RF)):
        S.append(len(GG))
        for n in GG:
            res[n[1]]=i/N

    return(res)
    # G1=nx.read_gpickle(crossGeomFileName(aspectInfo[a1],aspectInfo[a2]))
    