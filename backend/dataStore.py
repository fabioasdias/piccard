from os.path import exists, join
import numpy as np
import pandas as pd
import json
import networkx as nx
from os.path import join, basename
from glob import glob
from hierarchies import compareHierarchies
from uuid import uuid4
from clustering import ComputeClustering
from random import choice

MAX_CACHE = 10


def _getMaxLevel(G: nx.Graph, level: str = 'level') -> int:
    return(max([x[2] for x in G.edges(data=level)]))


def crossGeomFileName(name1, name2):
    minName = min([name1, name2])
    maxName = max([name1, name2])
    return('{0}_2_{1}.gp'.format(minName, maxName))


class dataStore(object):
    def __init__(self, geometry_folder: str, data_folder: str):
        self._info = {}        # aspect information
        self._hiers = {}       # hierarchies
        self._cross = {}       # cross geometry graphs
        self._data = {}        # raw data
        self._geometry_folder = geometry_folder
        self._data_folder = data_folder

        # pairwise distances between the hierarchies

        # it should be gp (but then glob *gp fails - hiers)
        # self._saved = join(self._data_folder, 'distances.xgp')
        # if exists(self._saved):
        #     self._distances = nx.read_gpickle(self._saved)
        # else:
        #     self._distances = nx.Graph()
        # self._update_distances()

    # def _update_distances(self):
    #     d = 'distance'
    #     for aspect in self.hierarchies():
    #         if aspect not in self._distances:
    #             to_add = list(self._distances.nodes())
    #             self._distances.add_node(aspect)
    #             for n in to_add:
    #                 self._distances.add_edge(aspect, n, distance=-1)

    #     for e in self._distances.edges():
    #         if self._distances[e[0]][e[1]][d] == -1:
    #             print('computing', e[0], e[1])
    #             self._distances[e[0]][e[1]][d] = compareHierarchies(
    #                 self, e[0], e[1])
    #     nx.write_gpickle(self._distances, self._saved)

    # def getDistanceGraph(self, aspects: list):
    #     """
    #         Returns a graph representation of the aspects including their distances.
    #     """
    #     # if not aspects:
    #     #     to_use = self.aspects()
    #     # else:
    #     #     to_use = aspects

    #     return(nx.subgraph(self._distances, aspects))

    def _check_and_read(self, aspectID: str, data:bool=False) -> None:
        """
        Checks if a given aspect is in memory, reads it from disk otherwise
        """
        if (aspectID not in self._info):
            infoFile = join(self._data_folder,
                            '{0}.info.json'.format(aspectID))
            with open(infoFile, 'r') as fin:
                self._info[aspectID] = json.load(fin)

        if data and (aspectID not in self._data):
            if (len(self._data)) > MAX_CACHE:
                pick = choice(list(self._data.keys()))
                del(self._data[pick])
            
            tableFile = join(self._data_folder, '{0}.tsv'.format(aspectID))
            self._data[aspectID] = pd.read_csv(tableFile,
                                               sep='\t', dtype=self._info[aspectID]['dtypes'],
                                               usecols=self._info[aspectID]['columns']+[self._info[aspectID]['index'], ])
            self._data[aspectID] = self._data[aspectID].set_index(
                [self._info[aspectID]['index'], ]).dropna(how='all')



    def aspects(self) -> list:
        aspects = glob(join(self._data_folder, '*.info.json'))
        return([basename(x)[:-10] for x in aspects])

    def hierarchies(self) -> list:
        hiers = glob(join(self._data_folder, '*.gp'))
        return([basename(x)[:-3] for x in hiers])

    def getHierarchy(self, aspectID: str, level: str = 'level') -> nx.Graph():
        """
            Returns the graph with the hierarchy of aspectID (same ID as the aspect that created it)
        """
        if (aspectID not in self._hiers):
            if len(self._hiers) > MAX_CACHE:
                first = list(self._hiers.keys())[0]
                del(self._hiers[first])

            G = nx.read_gpickle(join(self._data_folder, aspectID+'.gp'))
            m = _getMaxLevel(G, level)
            for e in G.edges():
                G[e[0]][e[1]][level] /= m
            self._hiers[aspectID] = G
        else:
            G = self._hiers[aspectID]
        return(G)

    def getCrossGeometry(self, g1: str, g2: str) -> nx.Graph():
        """
            Returns the graph that connects nodes of the _geometry_ g1 to g2 (and vice versa)
        """
        if (g1 == g2):
            return(None)
        fname = crossGeomFileName(g1, g2)
        if fname in self._cross:
            return(self._cross[fname])
        else:
            X = nx.read_gpickle(join(self._geometry_folder, fname))
            self._cross[fname] = X
            return(X)

    def createAspect(self, config: list, temporary_dir: str):
        ret = []
        for aspect in [a for a in config if a['enabled']]:
            try:
                with open(join(temporary_dir, aspect['fileID']+'.info.json')) as fin:
                    info = json.load(fin)
                data = pd.read_csv(join(temporary_dir, aspect['fileID']+'.tsv'),
                                   sep='\t', dtype=info['dtypes'],
                                   usecols=aspect['columns']+[aspect['index'], ])
                data = data.set_index(
                    [aspect['index'], ]).dropna(how='all')

                # dict_keys(['enabled', 'country', 'year', 'geometry',
                # 'name', 'normalized', 'fileID', 'columns'])
                VarInfo = {**aspect}
                dtypes = dict(data.dtypes)
                dtypes = {k: str(dtypes[k]) for k in dtypes.keys()}

                VarInfo.update({'id': str(uuid4()),
                                'descriptions': {c: info['columns'][c] for c in aspect['columns']},
                                'dtypes': dtypes,
                                })
                del(VarInfo['enabled'])
                with open(join(self._data_folder, VarInfo['id']+'.tsv'), 'w') as fout:
                    data.to_csv(fout, sep='\t')
                with open(join(self._data_folder, VarInfo['id']+'.info.json'), 'w') as fout:
                    json.dump(VarInfo, fout)
                ret.append(VarInfo)
                
                self.createHierarchy(VarInfo['id'])
            except:
                print('problem with ', aspect)
                raise
        return(ret)
    
    def createHierarchy(self, aspect:str):
        G = nx.read_gpickle(join(self._geometry_folder, self.getGeometry(aspect)+'.gp'))
        ncols = len(self.getColumns(aspect))
        for n in G.nodes():
            vals = self.getData(aspect,n[1])
            if vals is not None:
                G.node[n]['data'] = np.array(vals)
            else:
                G.node[n]['data'] = np.empty((ncols,))
                G.node[n]['data'][:] = np.nan

        G = ComputeClustering(G, 'data')
        nx.write_gpickle(G, join(self._data_folder, aspect+'.gp'))
        # self._update_distances()


    def getAspectName(self, aspectID: str) -> str:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['name'])

    def getAspectYear(self, aspectID: str) -> int:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['year'])

    def getGeometry(self, aspectID: str) -> str:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['geometry'])

    def getColumns(self, aspectID: str) -> list:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['columns'])

    def getDescriptions_AsDict(self, aspectID: str) -> dict:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['descriptions'])

    def getDescriptions_AsList(self, aspectID: str) -> list:
        self._check_and_read(aspectID)
        return([self._info[aspectID]['descriptions'][x] for x in self._info[aspectID]['columns']])

    def getData(self, aspectID: str, id: str) -> list:
        self._check_and_read(aspectID, data=True)
        if id in self._data[aspectID].index:
            return(list(self._data[aspectID].loc[id]))
        else:
            return(None)
