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
            if (len(g2p.edges())>0):
                try:
                    H[e[0]][e[1]][level]=max([H[e[0]][e[1]][level],max([x[2] for x in g2p.edges(data=level)])])
                except:
                    print(e)
                    print(g2p.nodes())
                    print([x[2] for x in g2p.edges(data=level)])
                    input('.')
                    raise
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
            if (curGeometry!=lastGeometry):
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

    #merge "projects" everyone into the first geom on the list
    F=_mergeAll(conf,FromAspects,aspectInfo)
    FG=aspectInfo[FromAspects[0]]['geometry']

    T=_mergeAll(conf,ToAspects,aspectInfo)
    TG=aspectInfo[ToAspects[0]]['geometry']
    
    if (TG!=FG):
        X=nx.read_gpickle(join(conf['folder'],crossGeomFileName(TG,FG)))
    else:
        X=None

    R=_hierMerge(F,T,X)

    pos={}
    for n in R:
        pos[n]=R.node[n]['pos'][0:2]

    nx.draw_networkx_nodes(R,pos,node_size=5)
    E=list(R.edges())
    W=[10*R[e[0]][e[1]]['level'] for e in E]
    nx.draw_networkx_edges(R,pos,edgelist=E,width=W)
    plt.show()
    
    return({})
    # G1=nx.read_gpickle(crossGeomFileName(aspectInfo[a1],aspectInfo[a2]))
    