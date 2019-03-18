import sys
import networkx as nx
import fiona
from util import indexedPols
from shapely.geometry import shape   
import geojson
import json

def _crossGeomFileName(name1,name2):
    minName=min([name1,name2])
    maxName=max([name1,name2])
    return('{0}_2_{1}.gp'.format(minName,maxName))


if __name__ == '__main__':
    nargs=len(sys.argv)
    if (nargs<8) or ((nargs-2)%3)==0:
        print(".py outputfolder PK1 geomName1 shp1 PK2 geomName2 shp2...")
        exit(-1)

    outName=sys.argv[1]

    args=sys.argv[2:]
    i=0
    baseGeometries=[]
    shps=[]
    fields=[]
    while i < len(args):
        fields.append(args[i])
        baseGeometries.append(args[i+1])
        shps.append(args[i+2])
        i+=3

    geo = {}
    print('Make sure you are using 4269!')
    for i,bGeom in enumerate(baseGeometries):
        print(bGeom)
        geo[bGeom]=indexedPols()
        #if it can't find gcs.csv, $> declare -x GDAL_DATA="/usr/share/gdal"
        with fiona.open(shps[i], 'r') as source:
            for feat in source:
                geo[bGeom].insertJSON(G=feat['geometry'],props={'Geom_ID':feat['properties'][field],})


    for ign,thisbGeom in baseGeometries:
        for nextbGeom in baseGeometries[ign+1:]:

            B = nx.Graph()
            for tid,tgeom in geo[thisbGeom].iterIDGeom('Geom_ID'):
                for polID in geo[nextbGeom].search(shape(tgeom).buffer(-1e-6)):   
                    matched=geo[nextbGeom].getPolygon(polID) 
                    nID=geo[nextbGeom].getProperty(polID,'Geom_ID')
                    # print(tgeom.intersection(matched).area/tgeom.area,(thisbGeom, tid),(nextbGeom, nID))
                    interArea=tgeom.intersection(matched).area
                    if ((interArea/tgeom.area)>0.05) or ((interArea/matched.area)>0.05):
                        B.add_edge((thisbGeom, tid),(nextbGeom, nID))

            print('edges',len(B.edges()))
                        
            print('saving')
            nx.write_gpickle(B,_crossGeomFileName(thisbGeom,nextbGeom))
