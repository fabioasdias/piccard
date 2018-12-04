import sys
import networkx as nx
import fiona
from util import indexedPols
from shapely.geometry import shape   
import geojson
import json

if __name__ == '__main__':
    nargs=len(sys.argv)
    if (nargs<5) or ((nargs%2)!=1):
        print(".py field outName.gp year1 shp1 y2 s2 ...")
        exit(-1)

    field = sys.argv[1]
    outName=sys.argv[2]

    args=sys.argv[3:]
    i=0
    years=[]
    shps=[]
    while i < len(args):
        years.append(args[i])
        shps.append(args[i+1])
        i+=2

    geo = {}
    print('Make sure you are using 4269!')
    for i,year in enumerate(years):
        print(year)
        geo[year]=indexedPols()

        with fiona.open(shps[i], 'r') as source:
            for feat in source:
                geo[year].insertJSON(G=feat['geometry'],props={'CT_ID':feat['properties'][field],})


    print('starting spatial edges')
    B = nx.Graph()
    
    for year in years:
        print(year)
        for fid, geom in geo[year].iterIDGeom('CT_ID'):
            n=(year,fid)

            B.add_node(n) 
            if ('pos' not in B.node[n]):
                representative=geom.representative_point()
                B.node[n]['pos']=[representative.x, representative.y,year]
            #spatial edges                
            for polID in geo[year].search(geom.buffer(1e-3)):
                nid=geo[year].getProperty(polID,'CT_ID')
                if (fid != nid):
                    B.add_edge(n,(year, nid))                    

    #temporal edges
    print('edges',len(B.edges()))
    print('temporal edges')
    for i in range(1, len(years)):
        thisYear = years[i-1]
        nextYear = years[i]
        for tid,tgeom in geo[thisYear].iterIDGeom('CT_ID'):
            for polID in geo[nextYear].search(shape(tgeom).buffer(-1e-6)):   
                matched=geo[nextYear].getPolygon(polID) 
                nID=geo[nextYear].getProperty(polID,'CT_ID')
                # print(tgeom.intersection(matched).area/tgeom.area,(thisYear, tid),(nextYear, nID))
                interArea=tgeom.intersection(matched).area
                if ((interArea/tgeom.area)>0.05) or ((interArea/matched.area)>0.05):
                    B.add_edge((thisYear, tid),(nextYear, nID))

    print('edges',len(B.edges()))

    nodes=sorted(B.nodes())
    for i,n in enumerate(nodes):
        B.node[n]['nid']=i
                
    print('saving')
    nx.write_gpickle(B,outName)

    def _noLessYear(G,n):
        for nv in G.neighbors(n):
            if (nv[0]<n[0]):
                return(False)
        return(True)
    def _temporal(G,n):
        ret=[]
        for nv in G.neighbors(n):
            if (nv[0]>n[0]):
                ret.append(nv)
        return(ret)

    paths=[]
    starts=[n for n in B.nodes() if _noLessYear(B,n)]
    for n0 in sorted(starts):
        todo=[[n0,],]
        while todo:
            cpath=todo.pop(0)
            options=_temporal(B,cpath[-1])
            if not options:
                paths.append(cpath)
            else:
                for op in options:
                    todo.append(cpath+[op,])
    with open(outName+'.tpaths','w') as fout:
        json.dump(paths,fout)
