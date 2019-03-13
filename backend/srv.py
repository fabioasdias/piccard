"""Server module for the backend"""
import json
import os
import pickle
import sys
from itertools import combinations, combinations_with_replacement
from os import makedirs
from os.path import exists, join
from time import time

import numpy as np
from numpy import nan

import cherrypy
import networkx as nx
import tempfile

from clustering import ComputeClustering
from networkx.readwrite import json_graph
from upload import processUploadFolder, gatherInfoJsons, create_aspect_from_upload
from aspects import compareAspects, showAspect
import pandas as pd

def cors():
  if cherrypy.request.method == 'OPTIONS':
    # preflign request 
    # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
    cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
    cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
    cherrypy.response.headers['Access-Control-Allow-Origin']  = '*'
    # tell CherryPy no avoid normal handler
    return True
  else:
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)

def _doStats(V):
    return(np.nanmedian(V,axis=0),np.nanmin(V,axis=0),np.nanmax(V,axis=0),np.percentile(V,25,axis=0),np.percentile(V,75,axis=0))

def _createID(dsconf, useOnly=[]):
    ID = 'cache'
    for k in sorted(dsconf.keys()):
        if (not useOnly) or (k in useOnly):
            ID = ID + '-' + '_'.join(['{0}'.format(i) for i in dsconf[k]])
    return(ID)


def _TemporalDifferences(curCountry, dsconf, H, nodes=None):
    ds = curCountry['ds']

    if (nodes is not None):
        if (nodes==[]):
            return([])
        G=H.subgraph(nodes)
    else:
        G=H
    

    states = dict()
    pop = dict()

    indVars={v:i for i,v in enumerate(dsconf['ivars'])}

    for n in G.nodes():
        V=ds.getValue(n,dsconf)
        if (n[0] not in states):
            states[n[0]]=dict()
            pop[n[0]]=0
            
        pop[n[0]]+=ds.getPopulation(n)


        for i in dsconf['ivars']:
            if (i not in states[n[0]]):
                states[n[0]][i]=[]
            states[n[0]][i].append(V[indVars[i]])
            
    smin=dict()
    smax=dict()
    smed=dict()
    sq1=dict()
    sq3=dict()

    for y in states:
        smin[y]=dict()
        smax[y]=dict()
        smed[y]=dict()
        sq1[y]=dict()
        sq3[y]=dict()
        for i in states[y]:
            states[y][i]=np.array(states[y][i])
            smed[y][i], smin[y][i], smax[y][i], sq1[y][i], sq3[y][i]=_doStats(states[y][i])



    ret=[]

    for i in dsconf['ivars']:
        short=ds.getVarShortLabels(i)
        labels=ds.getVarLabels(i)

        ranges=[]
        for j in range(len(smin[y][i])):
            row={'short':short[j],'ord':j,'long':labels[j],'states':dict(),}
            for y in states:
                row['states'][y]=[{'min':smin[y][i][j],
                                   'max':smax[y][i][j],
                                   'Q1' : sq1[y][i][j],
                                   'Q3' : sq3[y][i][j],
                                   'med':smed[y][i][j],
                                   'y' :0,
                                   'x': (sq1[y][i][j]+sq3[y][i][j])/2.0
                                }]
            ranges.append(row)
        ret.append({'name':ds.getVarName(i),'ranges':ranges})
    return({'population':pop, 'paths':ret})


def _computeTrajectories(G, L, curCountry, corr):

    years= curCountry['years']
    paths=curCountry['temporalPaths']

    traj=dict()    


    for lvl in range(len(corr)):
        traj[lvl]=[]
        for p in paths:
            usedYears=[n[0] for n in p]            
            chain=[corr[lvl][L[n]] for n in p if n in L]
            if (len(chain)!=len(p)):
                continue #missing data in one of them

            for i in range(len(traj[lvl])):
                if (chain==traj[lvl][i]['chain']) and (usedYears==traj[lvl][i]['years']):
                    tid=i
                    break
            else:
                tid=len(traj[lvl])
                if (len(set(usedYears))!=len(usedYears)):
                    print(chain,usedYears)
                    input('.')
                traj[lvl].append({'tid':tid, 'chain':chain, 'years':usedYears,'nodes':[], 'numNodes':{y:0 for y in years}})

            
            for n in p:
                traj[lvl][tid]['nodes'].append(G.node[n]['nid'])
                traj[lvl][tid]['numNodes'][n[0]]+=1

        for i in range(len(traj[lvl])):
            traj[lvl][i]['nodes']=sorted(set(traj[lvl][i]['nodes']))
    return(traj)



@cherrypy.expose
class server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def availableCountries(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret = []
        for kind in countries:
            c=countries[kind]
            ret.append({'name':  c['name'],
                        'kind':  c['kind'],
                        'geometries':c['geometries']
                        })
        return(ret)
    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def createAspects(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        aspects=create_aspect_from_upload(input_json,baseconf['upload'],countries)

        for aspect in aspects:
            country=countries[aspect['country']]

            G=country['graphs'][aspect['geometry']].copy()

            data=pd.read_csv(join(country['raw'],aspect['id']+'.tsv'), 
                             sep='\t', dtype=aspect['dtypes'])
            data=data.set_index(aspect['index'])
            ncols=len(data.columns)

            for n in G.nodes():
                if n[1] in data.index:
                    G.node[n]['data']=np.array(data.loc[n[1]].values)
                else:
                    G.node[n]['data']=np.empty((ncols,))
                    G.node[n]['data'][:]=np.nan
                                                
            G=ComputeClustering(G,'data')
            nx.write_gpickle(G,join(country['aspects'],aspect['id']+'.gp'))

        return(aspects)



    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getPath(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        countryID=input_json['countryID']

        dsconf = {}
        curCountry = countries[int(countryID)]
        ds = curCountry['ds']
        basegraph = curCountry['basegraph']
        nodes=[curCountry['i2n'][int(x)] for x in input_json['nodes']]

        # if (variables):
        #     ivars = np.array([int(x) for x in variables])
        # else:
        ivars = np.array([x['id'] for x in ds.avVars()])

        rightOrder = np.argsort(ivars)
        dsconf['ivars'] = ivars[rightOrder]

        ret=_TemporalDifferences(curCountry,dsconf,basegraph,nodes)
        return(ret)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getAspectComparison(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        countryID=input_json['countryID']
        aspect1=input_json['aspects'][0]
        aspect2=input_json['aspects'][1]
        return(showAspect(countries[countryID],aspect1))
        # return(compareAspects(countries[countryID],aspect1,aspect2))


    @cherrypy.expose
    def index(self):
        return("It works!")

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})    
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def getUploadedData(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        return(gatherInfoJsons(baseconf['upload']))


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.tools.gzip()
    def getAspects(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        countryID=input_json['countryID']
        return(gatherInfoJsons(countries[countryID]['raw']))


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})    
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def upload(self, file):
        myFile=file
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        res={'name':myFile.filename,'ok':True}
        with tempfile.TemporaryDirectory() as tempDir:
            fname=join(tempDir,myFile.filename)
            with open(fname,'wb') as outFile:        
                while True:
                    data = myFile.file.read(8192)
                    if not data:
                        break
                    outFile.write(data)      
            try:
                res.update(processUploadFolder(tempDir, baseconf['upload'],cherrypy.request.remote.ip))
            except:
                raise
                res['ok']=False      
        return(res)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getRegionDetails(self, countryID, displayID):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        displayID = int(displayID)
        countryID = int(countryID)
        curCountry = countries[countryID]
        ret = dict()
        for year in curCountry['years']:
            try:  # not all display id actually exist...
                n = curCountry['nByYearDisplayId'][(year, displayID)]
                ret[year] = curCountry['ds'].getRaw(n) + [{'type': "internal", 'short': [
                    'CTID', ], 'values': [n[1], ], 'name': 'CTID', 'labels': ['name']}, ]
                for i in range(len(ret[year])):
                    for j in range(len(ret[year][i]['values'])):
                        if (np.isnan(ret[year][i]['values'][j])):
                            ret[year][i]['values'][j] = 0
            except:
                pass
        return(ret)


if __name__ == '__main__':
    if (len(sys.argv)) != 2:
        print(".py conf.json")
        exit(-1)

    countries = {}
    #freshly uploaded (and unconfigured) data goes here
    baseconf={'upload':'./upload'}
    if (not exists(baseconf['upload'])):
        makedirs(baseconf['upload'])

    with open(sys.argv[1],'r') as fin:
        countriesConfig=json.load(fin)

    for i, v in enumerate(countriesConfig):
        cData = dict()
        cData.update(v)

        baseFolder = v['folder']

        cName = v['name']
        print('\n\n'+cName)

        G = nx.read_gpickle(join(baseFolder,'basegraph.gp'))
        cData['graphs']={}
        pos={}
        for n in G.nodes():
            pos[n]=[G.node[n]['pos'][0],G.node[n]['pos'][1]]
        for g in cData['geometries']:
            strYear=str(g['year'])
            H=G.subgraph([n for n in G.nodes() if (n[0]==strYear)])
            cData['graphs'][g['name']]=H
        
        cData['basegraph']=G

        cData['raw']=join(baseFolder,'raw')
        cData['aspects']=join(baseFolder,'aspects')
        if not exists(cData['raw']):
            makedirs(cData['raw'])
        if not exists(cData['aspects']):
            makedirs(cData['aspects'])

        countries[cData['kind']]=cData

    webapp = server()
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*','application/*']
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.server.max_request_body_size = 0 #for upload
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(webapp, '/', conf)
