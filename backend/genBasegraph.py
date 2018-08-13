import sys
import networkx as nx
from util import indexedPols,geoJsons
from shapely.geometry import shape   
import geojson
#from auxplots import plotPolys
#import matplotlib.pylab as plt
#from mpl_toolkits.mplot3d import Axes3D



if __name__ == '__main__':
    if (len(sys.argv)) < 3:
        print(".py geojsons.zip display.gj (basegraph.gp)")
        exit(-1)

    if (len(sys.argv)==3):
        outName='basegraph.gp'
    else:
        outName=sys.argv[3]
    geo = {}
    print('Make sure you are using 4269!')
    with geoJsons(sys.argv[1]) as gj:
        for year,cgj in gj:
            print(year)
            geo[year]=indexedPols()
            for feat in cgj['features']:
                geo[year].insertJSON(G=feat['geometry'],props={'CT_ID':feat['properties']['CT_ID'],})
    years = sorted(geo.keys())

    print('loading display')
    with open(sys.argv[2],'r') as fgjin:
        displayGJ=geojson.load(fgjin)

    didByN=dict()
    AreaByDid=dict()
    for feat in displayGJ['features']:
        did=feat['properties']['display_id']
        AreaByDid[did]=feat['properties']['area']
        for n in feat['properties']['nodes']:
            n=tuple(n)
            if n not in didByN:
                didByN[n]=[]
            didByN[n].append(did)


    print('starting spatial edges')
    B = nx.Graph()


    
    for year in years:
        for fid, geom in geo[year].iterIDGeom('CT_ID'):
            n=(year,fid)

            B.add_node(n) 
            if ('display_ids' not in B.node[n]):
                if (n not in didByN):
                    B.node[n]['display_ids']=[]
                    B.node[n]['areas']=[]
                else:
                    B.node[n]['display_ids']=didByN[n]
                    B.node[n]['areas']=[AreaByDid[x] for x in didByN[n]]

                representative=geom.representative_point()
                B.node[n]['pos']=[representative.x, representative.y,year]
            #spatial edges                
            for polID in geo[year].search(geom.buffer(1e-3)):
                nid=geo[year].getProperty(polID,'CT_ID')
                if (fid != nid):
                    B.add_edge(n,(year, nid))                    

    #temporal edges
    print('temporal edges')
    for i in range(1, len(years)):
        thisYear = years[i-1]
        nextYear = years[i]
        for tid,tgeom in geo[thisYear].iterIDGeom('CT_ID'):
            for polID in geo[nextYear].search(shape(tgeom).buffer(-1e-6)):   
                matched=geo[nextYear].getPolygon(polID) 
                nID=geo[nextYear].getProperty(polID,'CT_ID')
                B.add_edge((thisYear, tid),(nextYear, nID))
                B[(thisYear, tid)][(nextYear, nID)]['intersection']=geom.intersection(matched).area
                
    print('saving')
    nx.write_gpickle(B,outName)
