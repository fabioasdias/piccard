import sys
import networkx as nx
import fiona
from util import indexedPols
from shapely.geometry import shape   
import geojson
import json

if __name__ == '__main__':

    if len(sys.argv)!=5:
        print(".py field outName.gp geometryName shp ")
        exit(-1)

    field = sys.argv[1]
    outName=sys.argv[2]
    baseGeometry=sys.argv[3]
    shp=sys.argv[4]


    geo=indexedPols()
    #if it can't find gcs.csv, $> declare -x GDAL_DATA="/usr/share/gdal"
    with fiona.open(shp, 'r') as source:
        for feat in source:
            geo.insertJSON(G=feat['geometry'],props={'Geom_ID':feat['properties'][field],})


    print('starting spatial edges')
    B = nx.Graph()
    
    for fid, geom in geo.iterIDGeom('Geom_ID'):
        n=(baseGeometry,fid)

        B.add_node(n) 
        if ('pos' not in B.node[n]):
            representative=geom.representative_point()
            B.node[n]['pos']=[representative.x, representative.y,baseGeometry]
        #spatial edges                
        for polID in geo.search(geom.buffer(1e-3)):
            nid=geo.getProperty(polID,'Geom_ID')
            if (fid != nid):
                B.add_edge(n,(baseGeometry, nid))                    

    print('edges',len(B.edges()))

    nodes=sorted(B.nodes())
    for i,n in enumerate(nodes):
        B.node[n]['nid']=i
                
    print('saving')
    nx.write_gpickle(B,outName)
