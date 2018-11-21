from shutil import rmtree
from os.path import exists
from os import makedirs, remove
from glob import glob
import json
import sys

with open('conf.json','r') as fin:
    cities=json.load(fin)

erase=(len(sys.argv)>1)


for city in cities:
    cache=city['folder']+'/cache'
#    remove('basegraph.gp')

    if (not exists(cache)):
        makedirs(cache)
    else:
        if (erase):
            rmtree(cache)
            makedirs(cache)
        else:        
            for f in glob(cache+'/*.json'):
                remove(f)


