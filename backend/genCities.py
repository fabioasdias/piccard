"""This file reads cities.json, cuts the data accordingly (from my personal
dropbox, sorry), and generates the appropriate folders and conf.json to run the
server"""
import sys
from geojson import load
from subprocess import call
from shapely.geometry import Polygon
from util import indexedPols, zipJsons
from os.path import exists
from os import makedirs
import string
import json
from shapely.geometry import shape
from varConf import getVariables

baseFiles=dict()
baseFiles['US']='/home/diasf/Dropbox/USCensus/us.data.gj.zip'
baseFiles['CA']='/home/diasf/Dropbox/USCensus/CA/ca.data.gj.zip'
baseFiles['NY']='/home/diasf/workspace/ugp/analysis/CTEvo/backend/cities/US_New_York_City/geojsons.zip'
baseFiles['LA']='/home/diasf/workspace/ugp/analysis/CTEvo/backend/cities/US_Los_Angeles/geojsons.zip'

def doCut(zipname,cutPolygon,destZip):
    with zipJsons(zipname) as gj:
        for year,cgj in gj:
            print(year)
            pols=indexedPols()
            for feat in cgj['features']:
                pols.insertJSON(G=feat['geometry'],props=feat['properties'])
            pols.keepOnly(pols.bbSearch(cutPolygon))
            # pols.keepOnly(pols.search(cutPolygon))
            pols.keepOnly(pols.containedIn(cutPolygon))
            pols.saveGeoJson('{0}.gj'.format(year))
    call('zip -9 -m {0} *.gj'.format(destZip),shell=True)


if __name__ == '__main__':
    if len(sys.argv)!=2:
        print('.py cities.json')
        exit(-1)
    with open(sys.argv[1],'r') as fin:
        cities=load(fin)
    printable = set(string.printable)
    conf=[]
    makeBuff=''
    cities['features'].append({'properties':{'name':'Synthetic','kind':'SY'},'geometry':[]})

    allNames=[]
    allFolders=[]

    for city in cities['features']:
        cName=city['properties']['name']
        kind=city['properties']['kind']

        if (kind!='SY'):
            pol=shape(city['geometry'])

        print(cName)

        properName=cName[:].replace(' ','_')
        allNames.append(properName)

        if (kind=='NY') or (kind=='LA'):
            folder='./cities/US_'+properName    
        else:
            folder='./cities/'+kind+'_'+properName
        allFolders.append(folder)

        
        if (not exists(folder)):
            makedirs(folder)

        outGJ=folder+'/geojsons.zip'
        if (not exists(outGJ)) and (kind!='SY'):
            doCut(baseFiles[kind],pol,outGJ)        
        else:
            print("Reusing existing file (double check it) US2010 needs a *lot* of RAM (32Gb+) to extract")
            
        if (kind=='NY') or (kind=='LA'):            
            kind='US'

        avVars=getVariables(kind)
        conf.append({'name':cName, 'centroid':[pol.centroid.y,pol.centroid.x], 'folder':folder, 'kind':kind, 'vars':[x.getName() for x in avVars]})
        if (kind=='SY'):
            makeBuff=makeBuff+"{0}/normGeoJsons.zip: genSynt.py\n".format(folder)
            makeBuff=makeBuff+"\tpython3 genSynt.py {0}\n".format(folder)
            makeBuff=makeBuff+"\tzip -9j {0}/normGeoJsons.zip {0}/*_n.gj\n".format(folder)
            makeBuff=makeBuff+"\trm {0}/*_n.gj\n".format(folder)
        else:
            makeBuff=makeBuff+"{0}/normGeoJsons.zip: normGJVars.py {0}/geojsons.zip varConf.py\n".format(folder)
            makeBuff=makeBuff+"\tpython3 normGJVars.py {0}/geojsons.zip {1}\n".format(folder,kind)
            makeBuff=makeBuff+"\tzip -9j {0}/normGeoJsons.zip {0}/*_n.gj\n".format(folder)
            makeBuff=makeBuff+"\trm {0}/*_n.gj\n".format(folder)
        makeBuff=makeBuff+"{0}/display.json: {0}/normGeoJsons.zip prepGJs.py\n".format(folder)
        makeBuff=makeBuff+"\tpython3 prepGJs.py {0}/normGeoJsons.zip {0}/display.json\n".format(folder)        
        makeBuff=makeBuff+"{0}/basegraph.gp: {0}/normGeoJsons.zip genBasegraph.py util.py\n".format(folder)
        makeBuff=makeBuff+"\tpython3 genBasegraph.py {0}/normGeoJsons.zip {0}/basegraph.gp\n".format(folder)
        makeBuff=makeBuff+"{0}: {1}/basegraph.gp {1}/normGeoJsons.zip {1}/display.json\n".format(properName,folder)
     
    # this way, all is the first
    makeBuff="all: srv.py "+' '.join(allNames)+"\n"+"\t python3 srv.py conf.json\n\n"+makeBuff

    with open('conf.json','w') as fout:
        json.dump(conf,fout)
    with open('Makefile','w') as fout:
        fout.write(makeBuff)

        





