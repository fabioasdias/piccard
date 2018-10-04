from glob import glob
from shutil import copy
from os.path import basename

for folder in glob('./cities/*'):
    json=glob(folder+'/cache/*.json')
    if (json):
        copy(json[0],basename(folder)+'.json')
    else:
        print(folder)
