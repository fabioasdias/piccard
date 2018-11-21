import sys
import networkx as nx
from util import indexedPols,geoJsons
from shapely.geometry import shape   
import geojson
import json

if __name__ == '__main__':
    if (len(sys.argv)) < 2:
        print(".py geojsons.zip (basegraph.gp)")
        exit(-1)

    if (len(sys.argv)==2):
        outName='basegraph.gp'
    else:
        outName=sys.argv[2]
    geo = {}
    print('Make sure you are using 4269!')
    with geoJsons(sys.argv[1]) as gj:
        for year,cgj in gj:
            print(year)
            geo[year]=indexedPols()
            for feat in cgj['features']:
                geo[year].insertJSON(G=feat['geometry'],props={'CT_ID':feat['properties']['CT_ID'],})
    years = sorted(geo.keys())

    print('starting spatial edges')
    B = nx.Graph()
    
    for year in years:
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
                if (tgeom.intersection(matched).area/tgeom.area)>0.1:
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
