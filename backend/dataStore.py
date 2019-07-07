import json
from glob import glob
from os.path import basename, exists, join
from random import choice
from uuid import uuid4

import matplotlib.pylab as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import skew
from sklearn.preprocessing import minmax_scale
from rtree.index import Rtree
from clustering import ComputeClustering
from hierarchies import compareHierarchies

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
        self._projection = {}         # 1D projection data
        self._geometry_folder = geometry_folder
        self._data_folder = data_folder

    def getPaths(self, aspects: list) -> list:
        """
        Computes all the possible paths between the aspects, *in order*.
        """
        geoms = [self.getGeometry(a) for a in aspects]
        paths = []
        for i in range(len(geoms)):
            g = geoms[i]
            if i == 0:
                X = self.getCrossGeometry(g, g)
            else:    
                X = self.getCrossGeometry(geoms[i-1], g)

            unused = set([n for n in X if n[0] == g])
            to_add = []
            while paths:
                current = paths.pop(0)
                last = current[-1]
                if last[0] == g:  # same geometry:
                    to_add.append(current+[last, ])
                else:
                    options = [n for n in X.neighbors(last) if n[0] == g]
                    if not options:
                        to_add.append(current)
                    for op in options:
                        unused.discard(op)
                        to_add.append((current+[op, ]))

            # puts in the paths that start in this aspect
            paths = to_add+[[(-1,-1),]*i+[n, ] for n in unused]

        return(paths)

    def _do_projection(self, aspectID: str):
        """
            Computes and saves a 1D projection of the data for aspectID
        """
        self._check_and_read(aspectID, data=True)
        X = self._data[aspectID].to_numpy()

        if X.shape[1] == 1:
            Y = minmax_scale(X)
        else:
            bins = X.shape[1]
            step = 1/bins
            Y = np.argmax(X, axis=1)*step+step/2
            Y = Y + minmax_scale(skew(X, axis=1),
                                 feature_range=(-step/2, step/2))
            # print(bins, step)
            # plt.hist(Y, 100)
            # plt.show()

            # return()
            # # plt.figure()
            # # plt.hist(Y,100)

            # nSteps = 10000

            # Y = minmax_scale(Y, feature_range=(0, nSteps-1)).astype(np.int32)
            # h, _ = np.histogram(Y, nSteps)
            # cS = np.cumsum(h)
            # cS = nSteps*(cS / max(cS))
            # Y = cS[Y]
            # Y = minmax_scale(Y)

            # # plt.figure()
            # # plt.hist(Y,100)
            # # plt.show()

        df = pd.DataFrame(
            data=Y, index=self._data[aspectID].index, columns=['1D'])
        df.to_csv(join(self._data_folder,
                       '{0}.proj'.format(aspectID)), sep='\t')
    # @profile

    def _check_and_read(self, aspectID: str, data: bool = False, proj: bool = False) -> None:
        """
        Checks if the basic info for given aspect is in memory, reads it from disk otherwise.
        Set data/proj to do additionally for data/proj reading.
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
                [self._info[aspectID]['index'], ]).dropna(how='any')

        if proj and (aspectID not in self._projection):
            if not exists(join(self._data_folder, '{0}.proj'.format(aspectID))):
                print('proj', aspectID, self.getAspectName(aspectID))
                self._do_projection(aspectID)

            if (len(self._projection)) > MAX_CACHE:
                pick = choice(list(self._projection.keys()))
                # print('removing from cache',pick,self.getAspectName(pick))
                del(self._projection[pick])

            tableFile = join(self._data_folder, '{0}.proj'.format(aspectID))
            self._projection[aspectID] = pd.read_csv(tableFile, sep='\t')
            self._projection[aspectID] = self._projection[aspectID].set_index(
                [self._info[aspectID]['index'], ]).to_dict()['1D']

    def aspects(self) -> list:
        aspects = glob(join(self._data_folder, '*.info.json'))
        return([basename(x)[:-10] for x in aspects])

    def hierarchies(self) -> list:
        hiers = glob(join(self._data_folder, '*.gp'))
        return([basename(x)[:-3] for x in hiers])

    def getHierarchy(self, aspectID: str, level: str = 'level', bbox: list = None) -> nx.Graph():
        """
            Returns the graph with the hierarchy of aspectID (same ID as the aspect that created it)
        """
        if (aspectID not in self._hiers):
            if len(self._hiers) > MAX_CACHE:
                del(self._hiers[choice(list(self._hiers.keys()))])

            G = nx.read_gpickle(join(self._data_folder, aspectID+'.gp'))
            m = _getMaxLevel(G, level)
            for e in G.edges():
                G[e[0]][e[1]][level] /= m
            self._hiers[aspectID] = G
        else:
            G = self._hiers[aspectID]
        geom = self.getGeometry(aspectID)
        if bbox is None:
            return(G)
        else:
            I = Rtree(join(self._geometry_folder, geom+'.rt'))
            hits = list(I.intersection(bbox, objects=True))
            return(nx.subgraph(G, [(geom, item.object) for item in hits]))

    def getCrossGeometry(self, g1: str, g2: str) -> nx.Graph():
        """
            Returns the graph that connects nodes of the _geometry_ g1 to g2 (and vice versa)
        """
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
                # mins = {k:float(data[k].dropna(how='all').min()) for k in dtypes.keys()}
                # maxs = {k:data[k].dropna(how='all').max() for k in dtypes.keys()}

                VarInfo.update({'id': str(uuid4()),
                                'descriptions': {c: info['columns'][c] for c in aspect['columns']},
                                'dtypes': dtypes,
                                # 'mins': mins,
                                # 'maxs': maxs
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

    def createHierarchy(self, aspect: str):
        G = nx.read_gpickle(
            join(self._geometry_folder, self.getGeometry(aspect)+'.gp'))
        ncols = len(self.getColumns(aspect))
        for n in G.nodes():
            vals = self.getData(aspect, n[1])
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

    def getProjection(self, aspectID: str, id: str) -> float:
        """
            Returns the pre-computed projection of the 'id' point from aspectID.
        """
        self._check_and_read(aspectID, proj=True)
        if id in self._projection[aspectID]:
            return(self._projection[aspectID][id])
        else:
            return(None)
