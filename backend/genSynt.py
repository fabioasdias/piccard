import networkx as nx
from geojson import Feature, Polygon
from json import dump
from numpy.random import normal
import numpy as np
import matplotlib.pylab as plt
import sys

def _fix(p,M):
    return(int(round( (p/100) *M)))

if len(sys.argv)!=2:
    print('.py outFolder')
    exit(-1)
outFolder=sys.argv[1]

np.random.seed(783)

centers = {1:(1,1),2:(6,6), 3:(3,3), 4:(4,6), 5:(1,9), 6:(6,2), 7:(9,1), 8:(4.5,4.5) }

def getSample(c):
    X=normal(loc=10*centers[c][0],scale=4)
    Y=normal(loc=10*centers[c][1],scale=4)
    return([(X,100-X),(Y,100-Y)])

WW=20
WH=20
world=np.zeros((WW,WH,5))


world[:_fix(50,WW),:,:]=1
world[_fix(50,WW):,:,:]=2
for x in range(_fix(70,WW),_fix(75,WW)):
    world[x,np.arange((x+1)%2,WW,8),2]=3
    


# world[:5,:,:]=1
# world[5:,:,:]=2

# world[:]=4
# for i in range(world.shape[2]):
#     plt.figure()
#     plt.imshow(world[:,:,i].T,origin="lower")
#     plt.colorbar()
#     # plt.savefig('{0}_synt.png'.format(i+1))
# plt.show()



pols=dict()
points=dict()
ids=np.zeros_like(world)
clusters=dict()
revID=dict()
for y in range(world.shape[2]):
    pols[y]=[]
    points[y]=[]
    clusters[y]=dict()
    revID[y]=dict()
    print('year',y)
    for i in range(world.shape[0]):
        for j in range(world.shape[1]):
            coords=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
            iC=[]
            for c in coords:
                if (c not in points[y]):
                    iC.append(len(points[y]))
                    points[y].append(c)
                else:
                    iC.append(points[y].index(c))
            ids[i,j,y]=int(len(pols[y]))
            clusters[y][ids[i,j,y]]=world[i,j,y]
            revID[y][len(pols[y])]=(i,j)
            pols[y].append(iC)
            






N=[(0,-1),(1,0),(0,1),(-1,0)]

for y in range(world.shape[2]):
    to_merge=[]
    used=[]
    for m in np.random.randint(0,len(pols[y]),int(np.ceil(0.75*len(pols[y])))):
        if (m in used):
            continue
        else:
            used.append(m)

        ci,cj=revID[y][m]
        cID=world[ci,cj,y]
        useful=[]

        for i in range(len(N)):
            nI=ci+N[i][0]
            nJ=cj+N[i][1]
            if (nI>=0) and (nI<world.shape[0]) and (nJ>=0) and (nJ<world.shape[1]):
                if (world[nI,nJ,y]==cID):
                    m2=int(ids[nI,nJ,y])
                    if (m2 not in used):
                        useful.append(m2)

        if (len(useful)>0):
            m2=useful[np.random.randint(0,len(useful))]
            used.append(m2)
            to_merge.append((m,m2))

    for m in to_merge:
        #A
        if (pols[y][m[0]][0]==pols[y][m[1]][1]):
            pols[y][m[0]]=[pols[y][m[1]][0], pols[y][m[1]][1], pols[y][m[0]][1], pols[y][m[0]][2], pols[y][m[0]][3], pols[y][m[1]][3] ]
        # #B
        elif (pols[y][m[0]][1]==pols[y][m[1]][0]):
            pols[y][m[0]]=[pols[y][m[0]][0], pols[y][m[0]][1], pols[y][m[1]][1], pols[y][m[1]][2], pols[y][m[1]][3], pols[y][m[0]][3] ]
        # #C
        elif (pols[y][m[0]][0]==pols[y][m[1]][3]):
            pols[y][m[0]]=[pols[y][m[1]][0], pols[y][m[1]][1], pols[y][m[1]][2], pols[y][m[0]][2], pols[y][m[0]][3], pols[y][m[0]][0], ]
        # #D
        elif (pols[y][m[0]][2]==pols[y][m[1]][1]):
            pols[y][m[0]]=[pols[y][m[0]][0], pols[y][m[0]][1], pols[y][m[0]][2], pols[y][m[1]][2], pols[y][m[1]][3], pols[y][m[1]][0], ]

        pols[y][m[1]]=[]






minLat=0
minLon=0
maxLat=2
maxLon=2

for y in range(world.shape[2]):
    for k,p in enumerate(points[y]):
        if (p[0]>0) and (p[1]>0) and (p[0]<world.shape[0]) and (p[1]<world.shape[1]):
            points[y][k]=( (maxLat-minLat)*((p[0]/world.shape[0])+normal(0,0.005)) + minLat, (maxLon-minLon)*( (p[1]/world.shape[1]) + normal(0,0.005)) + minLon )
        else:
            points[y][k]=( (maxLat-minLat)*((p[0]/world.shape[0])) + minLat, (maxLon-minLon)*( (p[1]/world.shape[1])) + minLon )

for y in range(world.shape[2]):
    gj=dict()
    gj['crs']=dict()
    gj['crs']['properties']={'name':"urn:ogc:def:crs:EPSG::4269"}
    gj['crs']['type']="name"
    gj['type']="FeatureCollection"
    gj['features']=[]

    for k,p in enumerate(pols[y]):
        if (len(p)==0):
            continue

        curPoints=[]
        for i in range(len(p)):
            curPoints.append(points[y][p[i]])
        curPoints.append(points[y][p[0]])

        g=Polygon([curPoints])
        p=dict()
        i,j=revID[y][k]
        p['CT_ID']='SY.{0}.{1}'.format(i,j)
        p['variables']=[]
        p['variables'].append({'labels':['Total',],
                               'name':'Population',
                               'short':['Total',],
                               'type':'internal',
                               'values':[100,]
                               })

        X=getSample(clusters[y][k])       
        p['A1']=X[0][0]
        p['A2']=X[1][0]
        p['variables'].append({'labels':['part 1A','part 1B',],
                               'name':'Aspect 1',
                               'short':['p1A','p1B',],
                               'type':'categories',
                               'values':[X[0][0],X[0][1]]
                               })

        p['variables'].append({'labels':['part 2A','part 2B',],
                               'name':'Aspect 2',
                               'short':['p2A','p2B',],
                               'type':'categories',
                               'values':[X[1][0],X[1][1]]
                               })
        




        gj['features'].append(Feature(geometry=g,properties=p))
    
    with open(outFolder+'/{0:04d}_n.gj'.format(y),'w') as fout:
        dump(gj,fout, sort_keys=True, indent=4, separators=(',', ': '))

    




