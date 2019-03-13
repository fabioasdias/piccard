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
from datetime import datetime

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

def _infer_aspects_nhgis(df):
    #for nhgis, the 3 first letters of the column name are roughly equivalent to
    #aspects. 
    ret=[]

    cols=df.columns
    prefixes=list(set([x[:3] for x in cols if (len(x)==6) and all([y.isdigit() for y in x[4:]]) ]))
    for p in prefixes:
        ret.append([x for x in cols if x.startswith(p)])

    return(ret)

def _process_nhgis(nh,uploadDir,remoteIP):
    descriptions={}
    ret={}
    df={}

    for i in range(len(nh)):
        try:
            print(nh[i])
            code=nh[i][0]
            csv=nh[i][1]

            year=_get_year(basename(code))

            cdf=pd.read_csv(csv,low_memory=False,encoding = 'latin1',dtype={'GISJOIN': object},index_col=False)
            cdf=cdf.set_index('GISJOIN').dropna(axis=1,how='all') #drops columns that are empty
                
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
        except:
            ret['errors'].append(nh[i][0])

    ret['ids']=[]

    for year in df:
        print(year)
        id=str(uuid4())
        ret['ids'].append(id)
        #lets save the file first, so if the json is in there, the data is also
        #guaranteed to be
        with open(join(uploadDir,'{0}.tsv'.format(id)),'w') as ftsv:
            df[year].to_csv(ftsv,sep='\t')

        info={'id':id,
              'year':year,
              'geometry': {'name': 'US_CT_{0}'.format(year)}, #check in conf.json
              'ip': str(remoteIP),
              'index': 'GISJOIN',
              'UTC' : str(datetime.utcnow()),
              'aspects': _infer_aspects_nhgis(df[year]),
              'country': 'US',
              'columns':{}, 
              'samples':{}}
        for c in df[year].columns:
            info['samples'][c]=str(df[year][c][df[year][c].first_valid_index()])

            if (c in descriptions[year]):
                info['columns'][c]=descriptions[year][c]
            elif (c[:-2] in descriptions[year]):
                info['columns'][c]=descriptions[year][c[:-2]]
            else:
                info['columns'][c]=''

        dtypes=dict(df[year].dtypes)
        dtypes={k:str(dtypes[k]) for k in dtypes.keys()}
        info['dtypes']=dtypes
        with open(join(uploadDir,'{0}.info.json'.format(id)),'w') as finfo:
            json.dump(info,finfo, indent=4, sort_keys=True)
    return(ret)


def processUploadFolder(tempDir,uploadDir,remoteIP):    
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
    
    ret={}
    ret.update(_process_nhgis(nh,uploadDir,remoteIP))
    #TODO: CSV
    #TODO: json
                
    return(ret)

    
def gatherInfoJsons(jsondir):
    ret=[]
    for f in glob(join(jsondir,'*.info.json')):
        with open(f,'r') as fin:
            data=json.load(fin)
        if 'dtypes' in data:
            del(data['dtypes'])
        if 'ip' in data:
            del(data['ip'])
        if 'UTC' in data:
            del(data['UTC'])
        ret.append(data)
    return(ret)

def create_aspect_from_upload(aspects, uploadDir, countries):
    ret=[]
    for aspect in aspects:
        if aspect['enabled']:
            try:
                with open(join(uploadDir,aspect['fileID']+'.info.json')) as fin:
                    info=json.load(fin)
                data=pd.read_csv(join(uploadDir, aspect['fileID']+'.tsv'), 
                                sep='\t', dtype=info['dtypes'], 
                                usecols=aspect['columns']+[aspect['index'],])
                data=data.set_index([aspect['index'],])

                #dict_keys(['enabled', 'country', 'year', 'geometry', 
                # 'name', 'normalized', 'fileID', 'columns'])
                VarInfo={**aspect}
                dtypes=dict(data.dtypes)
                dtypes={k:str(dtypes[k]) for k in dtypes.keys()}

                VarInfo.update({'id':str(uuid4()), 
                    'descriptions':{c:info['columns'][c] for c in aspect['columns']},
                    'dtypes':dtypes,
                    })
                del(VarInfo['enabled'])
                with open(join(countries[aspect['country']]['raw'],VarInfo['id']+'.tsv'),'w') as fout:
                    data.to_csv(fout, sep='\t')
                with open(join(countries[aspect['country']]['raw'],VarInfo['id']+'.info.json'),'w') as fout:
                    json.dump(VarInfo, fout)
                ret.append(VarInfo)
            except:
                pass
    return(ret)



