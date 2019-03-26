from upload import gatherInfoJsons_AsDict
from os.path import join
import networkx as nx

def compareAspects(conf,a1,a2):
    aspectInfo=gatherInfoJsons_AsDict(conf['data'])
    graphs={}
    maxLevel={}
    for a in [a1,a2]:
        maxLevel[a]=0
        graphs[a]=nx.read_gpickle(join(conf['data'],a+'.gp'))
        for e in graphs[a].edges():
            maxLevel[a]=max([maxLevel[a],graphs[a][e[0]][e[1]]['level']])
    
    res={}
    vals=[]
    for n in graphs[a1]:
        v1=[x[2]/maxLevel[a1] for x in graphs[a1].edges(n,data='level')]
        if v1:
            d1=(max(v1)-min(v1))/maxLevel[a1]
        else:
            d1=1
        v2=[x[2]/maxLevel[a2] for x in graphs[a2].edges(n,data='level')]            
        if v2:
            d2=(max(v2)-min(v2))/maxLevel[a2]
        else:
            d2=1
        res[n[1]]=abs(d1-d2)

        vals.append(abs(d1-d2))

    mv=max(vals)
    for n in res:
        res[n]=res[n]/mv

    return(res)

def showAspect(conf,a):
    aspectInfo=gatherInfoJsons_AsDict(conf['data'])
    maxLevel={}
    maxLevel=0

    G=nx.read_gpickle(join(conf['data'],a+'.gp'))
    for e in G.edges():
        maxLevel=max([maxLevel,G[e[0]][e[1]]['level']])
    
    res={}
    for n in G:
        v=[x[2]/maxLevel for x in G.edges(n,data='level')]
        if v:
            # d1=(max(v)-min(v))/maxLevel
            res[n[1]]=max(v)

    return(res)


    
    
    
    