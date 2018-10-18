from scipy.stats import skew
from os.path import exists
import numpy as np
from util import geoJsons
from copy import deepcopy
from scipy.spatial.distance import sqeuclidean

def _norm(X):
    if (len(X)==1):
        return(X)
    sX=np.sum(X)
    if (sX>0):
        ret=X/sX
    else:
        ret=np.zeros_like(X)
    return(ret)
def _varDist(v1, v2):
    if len(v1)==1:
        return(sqeuclidean(v1,v2))
    else:
        return(1-np.sum(np.sqrt(np.multiply(v1,v2))))


class dataStore(object):
    def __init__(self):
        self._avFilters=[{'id':0, 'name':'Original data', 'func':(lambda x:x)},
                        {'id':1, 'name':'Skewness (+1)', 'func':(lambda x:skew(x)+1)},
                        ]     # available filters 
        self._avVars=[]       # variables included
        self._nodes=[]        # list of nodes (year,rid)
        self._rawdata=dict()  # raw data
        self._normdata=dict() # normalized data
        self._tabdata=None    # tabular version of the data - faster knn
        self._rowByVarID={}   # row ranges for each var
        self._varById={}      # variable name (key) by varID
        self._distCache={}    # cache of computed distances
        self._NodeByJSID={} # to enable talk with the react frontend - stable ordering
        self._JSIDByNode={}

    def avVars(self):
        return(self._avVars)
    def getVarName(self,varInd):
        return(self._avVars[varInd]['name'])
    def getFilterName(self,fInd):
        return(self._avFilters[fInd]['name'])
    def getVarLabels(self,varInd):
        return(self._avVars[varInd]['labels'])    
    def getVarShortLabels(self,varInd):
        return(self._avVars[varInd]['short'])    
    def avFilters(self):
        return(self._avFilters)
    def getRaw(self,n):
        return(list(self._rawdata[n].values()))
    def getPopulation(self,n):
        return(self._rawdata[n]['Population']['values'][0])
    def _buildtabdata(self):
        lenVars=0        
        for V in self.avVars():
            clen=len(self._normdata[self._nodes[0]][V['name']]['values'])
            self._rowByVarID[V['id']]=(lenVars,lenVars+clen)
            lenVars+=clen

        self._IDbyN={v:k for (k,v) in enumerate(self._nodes)}#indexes for the matrix
        self._NbyInd={k:v for (k,v) in enumerate(self._nodes)}#indexes for the matrix

        self._tabdata=np.zeros((len(self._nodes),lenVars))
        for n in self._nodes:
            for V in self.avVars():
                r=self._rowByVarID[V['id']]
                self._tabdata[self._IDbyN[n],r[0]:r[1]]=self._normdata[n][V["name"]]['values']
    def tabData(self,dsconf, nodes):
        outNbyInd={i:n for i,n in enumerate(nodes)}
        outIbyN={n:i for i,n in enumerate(nodes)}        
        ivars=dsconf['ivars']
        fs=dsconf['fs']
        if (self._tabdata is None):
            self._buildtabdata()
        ind=dict()
        oi=dict()
        lenVars=0
        for v in ivars:
            r=self._rowByVarID[v]
            ind[v]=[]
            oi[v]=[]
            for t in range(r[0],r[1]):
                oi[v].append(lenVars)
                lenVars+=1
                ind[v].append(t)

        ret=np.zeros((len(nodes),lenVars))
        for i in range(len(ivars)):
            v=ivars[i]
            f=self._avFilters[fs[i]]['func']
            for n in nodes:
                ret[outIbyN[n],oi[v]]=f(self._tabdata[self._IDbyN[n],ind[v]])
        
        return(ret,outNbyInd)
    def tabDataList(self,dsconf,Nodes):
        nodes=sorted(Nodes)
        outNbyInd={i:n for i,n in enumerate(nodes)}
        outIbyN={n:i for i,n in enumerate(nodes)}
        ivars=dsconf['ivars']
        fs=dsconf['fs']
        if (self._tabdata is None):
            self._buildtabdata()
        ind=dict()
        res=[]
        for i in range(len(ivars)):
            f=self._avFilters[fs[i]]['func']
            v=ivars[i]
            r=self._rowByVarID[v]
            ind[v]=[]
            for t in range(r[0],r[1]):
                ind[v].append(t)
            res.append(np.zeros((len(nodes),np.size(f(self._tabdata[0,ind[v]])))))
            
            for n in nodes:
                res[-1][outIbyN[n],:]=f(self._tabdata[self._IDbyN[n],ind[v]])
        return(res,outNbyInd)
    def getValue(self, n, dsconf=None):
        """If dsconf==None, returns all variables, original data, in the avVars order"""
        if (dsconf):
            ivars=dsconf['ivars']
            fs=dsconf['fs']
        else:
            ivars=[v['id'] for v in self._avVars]
            fs=[0,]*len(ivars)

        ret=[]
        for i in range(len(ivars)):
            r=self._rowByVarID[ivars[i]]
            ret.append(self._avFilters[fs[i]]['func'](self._tabdata[self._IDbyN[n],r[0]:r[1]]))
        return(ret)
    def distance(self, node1, node2, dsconf):
        ivars=dsconf['ivars']
        fs=dsconf['fs']
        

        kid=' '.join(['{0}'.format(x) for x in ivars])+'|'+' '.join(['{0}'.format(x) for x in fs])
        if (kid not in self._distCache):
            self._distCache[kid]={}
        n1=min((node1,node2))
        n2=max((node1,node2))
        if (n1 not in self._distCache[kid]):
            self._distCache[kid][n1]={}
        
        if (n2 in self._distCache[kid][n1]):
            return(self._distCache[kid][n1][n2])

        ind=[]
        for i in ivars:
            r=self._rowByVarID[i]
            for t in range(r[0],r[1]):
                ind.append(t)

        res=[]
        for i in range(len(ivars)):
            val1=self._normdata[n1][self._varById[ivars[i]]]['values']
            val2=self._normdata[n2][self._varById[ivars[i]]]['values']
            res.append(_varDist(
                                self._avFilters[fs[i]]['func'](val1),
                                self._avFilters[fs[i]]['func'](val2) ))
        res=sum(res)/len(ivars)
        self._distCache[kid][n1][n2]=res
        return(res)#THIS IS A PROBLEM TODO
    def read(self,gjzip):
        """reads a zipped set of geojsons. Use loadAndPrep instead!"""
        with geoJsons(gjzip) as gj:
            for year, cgj in gj:
                for feat in cgj['features']:
                    rid = feat['properties']['CT_ID']
                    n=(year,rid)              
                    self._rawdata[n]=dict()
                    self._nodes.append(n)
                    for v in feat['properties']['variables']:
                        self._rawdata[n][v['name']]=v
        self._varById=dict()
        self._avVars=[]

        tVar=self._rawdata[self._nodes[0]]
        for i,vName in enumerate(sorted([x for x in tVar if tVar[x]['type']!='internal'])):
            V=tVar[vName]
            self._avVars.append({'id':i, 'name':V['name'],'labels':V['labels'],'short':V['short'], 'type':V['type']})

        for V in self._avVars:
            self._varById[V['id']]=V['name']        
    def normalize(self):
        self._normdata=deepcopy(self._rawdata)
        divs=dict()

        for n in self._nodes:
            for v in self._rawdata[n]:
                if (v not in divs):
                    if (len(self._rawdata[n][v]['values'])==1): #scalar data
                        divs[v]=max([1,]+[self._rawdata[nn][v]['values'][0] for nn in self._nodes])
                        print('Max {0}-{1}'.format(self._rawdata[n][v]['name'],divs[v]))
                    else:   
                        divs[v]=1.0
                self._normdata[n][v]['values']=[x/divs[v] for x in _norm(self._rawdata[n][v]['values'])]
            #     print('-------',self._normdata[n][v]['name'],self._rawdata[n][v]['values'],self._normdata[n][v]['values'])
            # input('.')

        self._buildtabdata()
    def clean(self,basegraph):
        for n in self._nodes:
            for v in self._rawdata[n]:
                for j,val in enumerate(self._rawdata[n][v]['values']):
                        if (isinstance(val,str)):
                            self._rawdata[n][v]['values'][j]=np.float('NaN')
    def JSID(self, node):
        return(self._JSIDByNode[node])
    def Node(self, jsid):
        return(self._NodeByJSID[jsid])
    def loadAndPrep(self,gjzip,basegraph):
        self.read(gjzip)
        self.clean(basegraph)
        self.normalize()
        self._NodeByJSID={i:n for i,n in enumerate(basegraph.nodes())}
        self._JSIDByNode={self._NodeByJSID[i]:i for i in self._NodeByJSID}
