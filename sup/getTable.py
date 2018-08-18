import json
import sys


if len(sys.argv)!=3:
    print('.py folder US/CA')
    exit(-1)


which=sys.argv[2]

if (which=='CA'):
    CT_ID=['CA021065','CA5350065.00','CA535065.00','CA5350065.00','CA5350065.00']
    years=[1971,1981,1991,2001,2011]
if (which=='US'):
    years=[1970,1980,1990,2000,2010]
    CT_ID=['US36047014700',]*5

savedData={}

for i,y in enumerate(years):
    savedData[y]={}
    f=sys.argv[1]+'/{0}_n.gj'.format(y)
    with open(f,'r') as inGJ:
        gj=json.load(inGJ)
        for feat in gj['features']:
            if feat['properties']['CT_ID']==CT_ID[i]:
                for v in feat['properties']['variables']:
                    savedData[y][v['name']]={'labels':v['labels'],'values':v['values']}

newData={}
for y in savedData:
    for v in savedData[y]:
        if (v not in newData):
            newData[v]={}
        newData[v][y]=savedData[y][v]

print("\\begin{tabular}{lccccc}")
for v in newData:
    print('\t\\hline')
    print('\t'+v+'&'+'&'.join(['{0}'.format(y) for y in years])+'\\\\')
    print('\t\\hline')
    for i,l in enumerate(newData[v][years[0]]['labels']):
        print('\t',l,'&','&'.join(['{0}'.format(int(newData[v][y]['values'][i])) for y in years]),'\\\\')

print("\\end{tabular}")