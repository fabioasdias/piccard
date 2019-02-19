from uuid import uuid4
import zipfile
import magic
from os.path import basename
from os import remove
from os.path import isdir,join
from glob import glob
import pandas as pd
import numpy as np
import json

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

def _fix_duplicated_columns(df, dupPrefix='_x'):
    dupes=[x for x in df.columns if x.endswith(dupPrefix)]
    # to_remove=[]
    # for col in dupes:
    #     print(col,col[:-2])
    #     if (np.all(df[col]==df[col[:-2]])):            
    #         to_remove.append(col)
    # print(set(dupes)-set(to_remove))
    # return(df.drop(labels=to_remove,axis=1))
    return(df.drop(labels=dupes,axis=1))

def _get_year(fname):
    #nhgis0013_ds176_20105_2010_tract_E_codebook.txt
    vals=basename(fname).split('_')
    for i in range(1,len(vals)):
        if (vals[i]=='tract'):
            return(int(vals[i-1]))
    return(-1)


        

def processUploadFolder(tempDir,uploadDir):    
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
                if (kind=='text/plain'):
                    if (('.csv' in fname)or('.tsv' in fname)):
                        csvs.append(fname)
                    if ('.json' in fname):
                        jsons.append(fname)

    print('found: csvs {0}, jsons {1}, nhgis {2}'.format(len(csvs),len(jsons),len(nh)))
    print(csvs)
    print(jsons)
    print(nh)
    
    df={}
    descriptions={}

    for i in range(len(nh)):
        print(nh[i])
        code=nh[i][0]
        csv=nh[i][1]

        year=_get_year(basename(code))

        cdf=pd.read_csv(csv,low_memory=False,encoding = 'latin1',dtype={'GISJOIN': object},index_col=False)
        cdf=cdf.set_index('GISJOIN')
            
        cols=cdf.columns
        if year not in descriptions:
            descriptions[year]={}
            df[year]=cdf
        else:
            df[year]=pd.merge(cdf,df[year],on='GISJOIN',suffixes=['','_x'])
            df[year]=_fix_duplicated_columns(df[year])
            

        with open(code,'r') as ffin:
            for line in ffin:
                for c in cols:
                    if (c in line):
                        descriptions[year][c]=line.strip()

    ret={}
    ret['ids']=[]

    for year in df:
        print(year)
        id=str(uuid4())
        ret['ids'].append(id)
        #lets save the file first, so if the json is in there, the data is also
        #guaranteed to be
        with open(join(uploadDir,'{0}.tsv'.format(id)),'w') as ftsv:
            df[year].to_csv(ftsv,sep='\t')

        info={'id':id,'year':year,'description':{}}
        for c in df[year].columns:
            if (c in descriptions[year]):
                info['description'][c]=descriptions[year][c]
            elif (c[:-2] in descriptions[year]):
                info['description'][c]=descriptions[year][c[:-2]]
            else:
                info['description'][c]=''
        dtypes=dict(df[year].dtypes)
        dtypes={k:str(dtypes[k]) for k in dtypes.keys()}
        info['dtypes']=dtypes
        with open(join(uploadDir,'{0}.info.json'.format(id)),'w') as finfo:
            json.dump(info,finfo)
                
    return(ret)

    