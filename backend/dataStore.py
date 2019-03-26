from os.path import exists, join
import numpy as np
import pandas as pd
import json


class dataStore(object):
    def __init__(self, folder:str):
        self._aspects=[]   # aspects included
        self._info={}
        self._data={}  # raw data
        self._folder=folder # data folder
        
    def _check_and_read(self,aspectID:str) -> None:
        """
        Checks if a given aspect is in memory, reads it from disk otherwise
        """
        if (aspectID not in self._info):
            infoFile=join(self._folder,'{0}.info.json'.format(aspectID))
            tableFile=join(self._folder,'{0}.tsv'.format(aspectID))
            if (not exists(infoFile)) or (not exists(tableFile)):
                print("Trying to read non-existent aspect ",aspectID)
                return

            with open(infoFile,'r') as fin:
                self._info[aspectID]=json.load(fin)
            self._data[aspectID]=pd.read_csv(tableFile, 
                                sep='\t', dtype=self._info[aspectID]['dtypes'], 
                                usecols=self._info[aspectID]['columns']+[self._info[aspectID]['index'],])
            self._data[aspectID]=self._data[aspectID].set_index([self._info[aspectID]['index'],]).dropna(how='all')


    def aspects(self)->list:
        return(self._aspects)

    def getAspectName(self, aspectID:str) -> str:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['name'])

    def getGeometry(self, aspectID:str) -> str:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['geometry'])

    def getColumns(self,aspectID:str) -> list:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['columns'])    

    def getDescriptions_AsDict(self,aspectID:str) -> dict:
        self._check_and_read(aspectID)
        return(self._info[aspectID]['descriptions'])    

    def getDescriptions_AsList(self,aspectID:str) -> list:
        self._check_and_read(aspectID)
        return([self._info[aspectID]['descriptions'][x] for x in self._info[aspectID]['columns']])    


    def getData(self, aspectID:str, id:any) -> list:
        self._check_and_read(aspectID)
        return(list(self._data[aspectID].loc[id]))

