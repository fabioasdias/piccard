from uuid import uuid4
import zipfile
import magic
from os.path import basename
from os import remove
from os.path import isdir,join
from glob import glob
import pandas as pd

def _extractErase(fname,tempDir):
    zip_ref = zipfile.ZipFile(fname, 'r')
    zip_ref.extractall(tempDir)
    zip_ref.close()
    remove(fname)


def _nhgis(folder):
    codebooks=[x for x in glob(join(folder,'*.txt')) if 'codebook' in basename(x)]
    csvs=glob(join(folder,'*.csv'))
    ret=[]
    for c in codebooks:
        try:
            i=csvs.index(c.replace('_codebook.txt','.csv'))
            ret.append((c,csvs[i]))
        except:
            print('not found',c)

    return(ret)    

def processUploadFolder(tempDir):    
    csvs=[]
    jsons=[]
    nh=[]
    folders=[tempDir,]
    nzips=0
    while folders:
        cf=folders.pop(0)
        for fname in glob(join(cf,'*')):
            if (isdir(fname)):
                pairs=_nhgis(fname)
                if pairs:
                    nh.extend(pairs)
                else:
                    folders.append(fname)
            else:
                kind=magic.from_file(fname,mime=True)
                if (kind=='application/zip'):
                    newdir=join(tempDir,'{0}'.format(nzips))
                    nzips+=1
                    _extractErase(fname,newdir)
                    folders.append(newdir)
                if ((kind=='text/plain') and (('.csv' in fname)or('.tsv' in fname))):
                    csvs.append(fname)
                if ((kind=='text/plain') and ('.json' in fname)):
                    jsons.append(fname)

    id=uuid4()
    ret={}
    ret['id']=str(id)
    ret['status']={}
    df={}
    descriptions={}

    for i in range(len(nh)):
        print(i)
        code=nh[i][0]
        csv=nh[i][1]
        year=int(basename(code).split('_')[2])
        # try:
        #     cdf=pd.read_csv(csv,low_memory=False)
        # except:
        cdf=pd.read_csv(csv,low_memory=False,encoding = 'latin1',dtype={'GISJOIN': object},index_col=False)
        cdf=cdf.set_index('GISJOIN')
            
        cols=cdf.columns
        if year not in descriptions:
            descriptions[year]={}
            df[year]=cdf
        else:
            df[year]=pd.merge(cdf,df[year],on='GISJOIN',suffixes=['','_x'])
            df[year]=df[year].drop(labels=[x for x in df[year].columns if '_x' in x],axis=1)

        with open(code,'r') as ffin:
            for line in ffin:
                for c in cols:
                    if (c in line):
                        descriptions[year][c]=line.strip()

    print('cols')
    for y in df:
        print(y)
        for c in df[y].columns:
            if (c in descriptions[y]):
                print(descriptions[y][c])
            else:
                print('dont have ',c)
        print('\n')
                
    return(ret)

    