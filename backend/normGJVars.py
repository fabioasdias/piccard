""" This script gather the usable variables across the years and
put them on the same place, with the same names, saving it as an actual geojson"""
import sys
from util import zipJsons
from varConf import getVariables
from geojson import FeatureCollection, Feature, dump
import numpy as np
from os.path import dirname
from shapely.geometry import shape   
from util import indexedPols,split    
from shapely.ops import unary_union

def _newProps(varNames):
    ret = {}
    for n in varNames:
        ret[n] = []
    return(ret)


def _setVals(year, avVars, props):
    newProps = {'CT_ID': props['CT_ID'], 'variables': []}
    for v in avVars:
        newProps['variables'].append({
            'name'  : v.getName(),
            'labels': v.getLabels(),
            'short' : v.getShortLabels(), 
            'type'  : v.getType(),
            'values': v.computeValue(props, year)
        })
        
        # if (any([isinstance(x,str) for x in newProps['variables'][-1]['values']])):
        #     print(newProps['CT_ID'])
        #     print(newProps['variables'][-1])
    
    return(newProps)


if __name__ == '__main__':
    if (len(sys.argv)) != 3:
        print(".py geoJsons.zip US/CA")
        exit(-1)

    folder = dirname(sys.argv[1])

    avVars = getVariables(sys.argv[2])
    print([v.getName() for v in avVars])
    with zipJsons(sys.argv[1]) as gj:
        for year, cgj in gj:
            usedPols=indexedPols()

            if ('labels' in cgj):
                with open('{0}_labels.txt'.format(year), 'w') as f:
                    f.write("\n".join(
                        ['{0}-{1}'.format(k, cgj['labels'][k]) for k in sorted(cgj['labels'].keys())]))

            feats = []
            for f in cgj['features']:
                g = shape(f['geometry']).buffer(0)
                I = usedPols.search(g)
                if (len(I)>0):
                    # print('found stuff!', year,len(I),f['properties']['CT_ID'])
                    UB=unary_union([usedPols.getPolygon(i) for i in I]).buffer(0)
                    g=g.difference(UB).buffer(0)

                if (not g.is_empty):
                    feats.append(Feature(geometry=g, properties=_setVals(year, avVars, f['properties'])))
                    usedPols.insert(g)


            with open(folder+'/{0}_n.gj'.format(year), 'w') as fout:
                if ('crs' not in cgj):
                    dump(FeatureCollection(feats,crs={"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4269"}}),fout,indent=4, sort_keys=True)
                else:
                    dump(FeatureCollection(feats, crs=cgj['crs']),fout,indent=4, sort_keys=True)