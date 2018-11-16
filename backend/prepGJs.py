import json
from util import geoJsons
import sys

if __name__ == '__main__':
    if (len(sys.argv)) < 2:
        print(".py geojsons.zip (display.json)")
        exit(-1)
    if (len(sys.argv)==2):
        outName='display.json'
    else:
        outName=sys.argv[2]

    display={}
    print('Make sure you are using 4269!')
    with geoJsons(sys.argv[1]) as gj:
        for year,cgj in gj:
            display[year]={}
            display[year]["type"]= "FeatureCollection"
            display[year]["features"]= []

            for feat in cgj['features']:
                display[year]['features'].append({'type': "Feature",
                                                  'geometry':feat['geometry'], 
                                                  'properties':{'CT_ID':feat['properties']['CT_ID'],}})
    with open(outName,'w') as fout:
        json.dump(display,fout)
