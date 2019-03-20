import tempfile
import zipfile
import shutil
import geojson
from glob import glob
from os.path import basename
from rtree import index
from shapely.geometry import shape, MultiPolygon
from shapely.ops import snap
from geojson import Feature, FeatureCollection
from copy import deepcopy
import json

def crossGeomFileName(name1,name2):
    minName=min([name1,name2])
    maxName=max([name1,name2])
    return('{0}_2_{1}.gp'.format(minName,maxName))


def polOnly(geom):
    if (not geom) or ('Polygon' not in geom.type):
        if ('Collection' in geom.geom_type):
          return(MultiPolygon([g for g in geom if 'Polygon' in g.geom_type]))

        return(None)
    else:
        return(geom)

def split(AA, BB):
    A=deepcopy(AA)
    B=deepcopy(BB)
    """Splits A and B into A-B, A inter B, and B-A"""
    if (not A) or (not B):
        return(A, None, B)
    try:
        AmB = A.difference(B)
        AiB = A.intersection(B)
        BmA = B.difference(A)
    except:
        nA = snap(A, B, 1e-3)
        AmB = nA.difference(B)
        AiB = nA.intersection(B)
        BmA = B.difference(nA)
    return(polOnly(AmB),
           polOnly(AiB),
           polOnly(BmA))

class indexedPols:
    def __init__(self):
        self._index = index.Index()
        self._pols = []
        self._removed = [] #each polygon has a allocated value - more memory, but faster
        self._properties = {}

    def __next__(self):
        for i in range(len(self._pols)):
            if not self._removed[i]:
                yield(self._pols[i])

    def __iter__(self):
        return(next(self))

    # def cleanup(self):
    #     """Actually removes deleted data - INVALIDATES THE INDEXES!"""
    #     toRemove = sorted([i for i, v in enumerate(self._removed) if v], reverse=True)
    #     for i in toRemove:
    #         self._index.delete(i, self._pols[i].bounds)
    #         del(self._pols[i])
    #     self._removed = [False,]*len(self._pols)
        
    def _getPols(self, geocollection):
        gc=geocollection
        res=[]
        if (gc.geom_type=='Polygon'):
            return([gc,])
        if (gc.geom_type=='MultiPolygon'):
            return([p for p in gc])
        if ('Collection' in gc.geom_type):
            res.extend([self._getPols(p) for p in gc])
        return(res)
        
    def saveGeoJson(self,fname,display_id=False,area=False, saveOnly=[]):
        """saves a geojson from the polygons - basic one, no crs, no extra data
           display_id=True inserts an 'display_id' field with unique ids"""
        feats=[]
        for k,p in enumerate(self._pols):
            if (not self._removed[k]) and ((not saveOnly) or (k in saveOnly)):
                if (p.geom_type!='Polygon'):
                    print(k,p.geom_type)
                    input('.')
                if (display_id):
                    self._properties[k]['display_id']=k
                if (area):
                    self._properties[k]['area']=p.area
                feats.append(Feature(geometry=p,properties={**self._properties[k]}))
        fc=FeatureCollection(feats)
        fout=open(fname,'w')
        geojson.dump(fc,fout)
        fout.close()

    def readGeoJson(self,fname):
        with open(fname,'r') as fin:
            data=geojson.load(fin)
        for feat in data['features']:
            self.insertJSON(G=feat['geometry'],props=feat['properties'])

    def getProps(self,polID):
        return(self._properties[polID])
    def getProperty(self,polID,prop='Geom_ID'):
        return(self._properties[polID][prop])

    def iterIDGeom(self,idfield='Geom_ID'):
        """Returns a generator that goes over the geometries, 
           returning them along the property named by idfield"""
        for i in range(len(self._pols)):
            if not self._removed[i]:
                yield(self._properties[i][idfield],self._pols[i])
    def getPolygon(self,polID):
        return(self._pols[polID])

    def insert(self,G,props={},areaThreshold=0):
        if (not G) or (not G.bounds):
            return
        #buffer might transform pol -> multipol
        for g in self._getPols(G.buffer(0)): 
            if (g.is_empty) or (g.area<areaThreshold):
                continue
            self._index.insert(len(self._pols),g.bounds)
            self._properties[len(self._pols)]=deepcopy(props)
            self._pols.append(deepcopy(g))
            self._removed.append(False)
        if ('Collection' in G.geom_type):
            self.insert(MultiPolygon(self._getPols(G)))

    def insertJSON(self,G,props={}):
        """Converts from JSON to shapely's shape"""
        self.insert(shape(G),props)        
    def remove(self,geoID):
        """removes AND RETURNS the element geoID"""
        self._removed[geoID]=True
        return(deepcopy({'geometry':self._pols[geoID], 'properties':self._properties[geoID]}))
    def erase(self,geoID):
        """removes the element geoID"""
        self._removed[geoID]=True

    def bbSearch(self,geom):
        if (len(self._pols)==0):
            return([])
        return([i for i in self._index.intersection(geom.bounds) if (not self._removed[i])])        
    def bbSearchJSON(self,geometry):
        if (len(self._pols)==0):
            return([])
        geom=shape(geometry)
        return([i for i in self._index.intersection(geom.bounds) if (not self._removed[i])])        

    def containedIn(self,geom):
        if (len(self._pols)==0):
            return([])
        res=[]
        for i in self._index.intersection(geom.bounds):
            if (not self._removed[i]) and (geom.contains(self._pols[i])):
                res.append(i)
        return(res)        

    def search(self,geom):
        if (len(self._pols)==0) or (geom.is_empty):
            return([])
        res=[]

        for i in self._index.intersection(geom.bounds):
            if (not self._removed[i]) and (geom.intersects(self._pols[i])):
                res.append(i)
        return(res)        
    
    def searchJSON(self,geometry):
        if (len(self._pols)==0):
            return([])
        geom=shape(geometry)
        res=[]
        for i in self._index.intersection(geom.bounds):
            if (not self._removed[i]) and (geom.intersects(self._pols[i])):
                res.append(i)
        return(res)        
    
    def keepOnly(self,ids):
        """Remove all polygons that are not in ids"""
        self._removed=[True,]*len(self._removed)
        for i in ids:
            self._removed[i]=False

class geoJsons:
    def __init__(self,zFile):
        self._zFile=zFile

    def __enter__(self):
        self._gjFolder=tempfile.mkdtemp()
        if ('.zip' in self._zFile):
            with zipfile.ZipFile(self._zFile) as zipref:
                zipref.extractall(self._gjFolder)
            self._filelist=sorted(list(glob(self._gjFolder+'/*')))
        else:
            self._filelist=self._zFile
        return(self)

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self._gjFolder)

    def __next__(self):
        for gj in self._filelist:
            with open(gj,'r') as f:
                data=geojson.load(f)
                yield(int(basename(gj)[:4]),data)
            
    def __iter__(self):
        return(next(self))

class zipJsons:
    def __init__(self,zFile):
        self._zFile=zFile

    def __enter__(self):
        self._gjFolder=tempfile.mkdtemp()
        if ('.zip' in self._zFile):
            with zipfile.ZipFile(self._zFile) as zipref:
                zipref.extractall(self._gjFolder)
            self._filelist=sorted(list(glob(self._gjFolder+'/*')))
        else:
            self._filelist=self._zFile
        return(self)

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self._gjFolder)

    def __next__(self):
        for js in self._filelist:
            with open(js,'r') as f:
                data=json.load(f)
                yield(int(basename(js)[:4]),data)
            
    def __iter__(self):
        return(next(self))
