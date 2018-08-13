import networkx as nx
from fibonacci_heap_mod import Fibonacci_heap, merge
#import matplotlib.pylab as plt
from collections import deque
import numpy as np

#from auxplots import plot3dWS
from time import time


def bhat(u1,u2,v1,v2):
    return((1.0/4) * np.log ( 1.0/4 * (v1/v2 + v2/v1 + 2)) + 1.0/4 * (((u1-u2)**2)/(v1+v2)))


# Reference: https://hal.archives-ouvertes.fr/file/index/docid/622505/filename/hal.pdf
def MakeSet(C,x):
    C[x]={'rank':0,'parent':x}
    
def find(C, x):
    if (C[x]['parent']!=x):
        C[x]['parent']=find(C,C[x]['parent'])
    return(C[x]['parent'])

def Link(C, x, y):
    xRoot = find(C,x)
    yRoot = find(C,y)
 
    if xRoot == yRoot:
        return
   
    if C[xRoot]['rank'] < C[yRoot]['rank']:
        C[xRoot]['parent'] = yRoot
    elif C[xRoot]['rank'] > C[yRoot]['rank']:
        C[yRoot]['parent'] = xRoot
    else:
        C[yRoot]['parent'] = xRoot    
        C[xRoot]['rank']   = C[xRoot]['rank'] + 1
    return(find(C,x))

def meld(C, L, x, y):
    res=Fibonacci_heap()
    while (len(L[x])>0):
        el=L[x].dequeue_min()
        _,v=el.get_value()
        if (find(C,v[0])!=find(C,v[1])):
            res.enqueue(el.get_value(),el.get_priority())
    while (len(L[y])>0):
        el=L[y].dequeue_min()
        _,v=el.get_value()
        if (find(C,v[0])!=find(C,v[1])):
            res.enqueue(el.get_value(),el.get_priority())
    return(res)

def uprooting(G, X, ds, dsconf):
    C = dict()
    L = dict()
    I = dict()
    for x in G.nodes():
        MakeSet(C, x)
        L[x] = Fibonacci_heap()

    for u in G.edges():
        if (u in X.edges()):
            I[(min(u), max(u))]=0
        else:
            I[(min(u), max(u))]=-1

    for u in X.edges():
        xp=find(C,u[0])
        yp=find(C,u[1])
        if (xp!=yp):
            Link(C,xp,yp)

    for u in G.edges():
        if (u in X.edges()):
            continue
        cVal=ds.distance(u[0],u[1],dsconf)
        x=find(C,u[0])
        y=find(C,u[1])
        if (x!=y):
            L[x].enqueue((y,u),cVal)
            L[y].enqueue((x,u),cVal)

    merges=[]
    nCC=sum([1 for x in L if len(L[x])>0])
    for i in range(1,nCC):
        x=None
        xmin=np.inf
        for xx in L:
            if (len(L[xx])==0):
                continue
            cP=L[xx].min().get_priority()
            if (cP < xmin):
                x=xx
                xmin=cP
        xp=find(C,x)
        while len(L[xp])>0:
            (y,v)=L[xp].dequeue_min().get_value()
            yp=find(C,y)
            if (xp!=yp):
                break
        merges.append((min(v),max(v)))
        I[(min(v),max(v))]=i
        z=Link(C,xp,yp)
        L[z]=meld(C,L,xp,yp)
    return(I,merges)

def Fminus(G,n,ds,dsconf):
    return(min([ds.distance(e[0],e[1],dsconf) for e in G.edges(n)]))

def stream(G,psi,x,MSF,ds,dsconf):
    L = [x,]
    lp = deque([x,])
    while (len(lp)>0):
        y = lp.popleft()
        breadth_first = True
        allZ = [z for z in G.neighbors(y) if (z not in L) and ds.distance(y,z,dsconf)==Fminus(G,y,ds,dsconf)]
        if (not allZ):
            break
        for z in allZ:
            if (not breadth_first):
                break
            MSF.add_edge(min((y,z)),max((y,z)))
            if (psi[z]>=0):
                return([L,psi[z]])
            elif Fminus(G,z,ds,dsconf)<Fminus(G,y,ds,dsconf):
                L.append(z)
                lp.clear()
                lp.append(z)
                breadth_first = False
            else:
                L.append(z)
                lp.append(z)
    return (L,-1)

def MSF_watershed(G,ds,dsconf):
    MSF=nx.Graph()
    MSF.add_nodes_from(G.nodes())
    psi = dict()
    for n in G.nodes():
        psi[n] = -1
    nb_labs = 0
    for x in G.nodes():
        if (psi[x]==-1):
            [L,lab] = stream(G,psi,x,MSF,ds,dsconf,)
            if (lab==-1):
                for y in L:
                    psi[y] = nb_labs
                nb_labs+=1 #starts in zero
            else:
                for y in L:
                    psi[y] = lab
    return(MSF,psi)

def otherHierarchy(G,psi,ds,dsconf):
    C=dict()    
    for n in G.nodes():
        MakeSet(C,n)
    
        
    for e in G.edges():
        r0=find(C,e[0])
        r1=find(C,e[1])
        if (psi[r0]==psi[r1]):
            Link(C,r0,r1)



    merges=[]
    allC=sorted(list(set(psi.values())))

    clusters=dict()
    V=dict()
    rep=dict()
    M=len(allC)
    D=np.zeros((M,M))
    D[:]=np.nan
    indByC={c:i for i,c in enumerate(allC)}
    Cbyind={i:c for i,c in enumerate(allC)}


    toUpdate=allC[:]
    print('number of iterations',len(allC)-1)

    for i in range(len(allC)-1):
        print(i)
        for c in toUpdate:
            clusters[c]=[]


        NG=nx.Graph()

        t0=time()
        for n in C:
            c=psi[find(C,n)]
            if (c in toUpdate):
                clusters[c].append(n)
        nc=np.sum([1 for c in clusters if len(clusters[c])>0])
        print('#clusters',nc)
        if (nc < 20):
            break
            
        for c in toUpdate:
            N=len(clusters[c])
            if (N==0):
                continue
            tm=np.zeros((N,N))
            for i1,n1 in enumerate(clusters[c]):

                for nn in G.neighbors(n1):
                    if (c!=psi[nn]):
                        NG.add_edge(c,psi[nn])

                for i2,n2 in enumerate(clusters[c]):
                    if (i2<=i1):
                        continue
                    tm[i1,i2]=np.power(ds.distance(n1,n2,dsconf),2)

            V[c]=max((1e-6,np.sum(tm)/np.power(N,2))) #Variance zero is bad (and unrealistic)
            rep[c]=clusters[c][np.argmin(np.sum(tm+tm.T,axis=1))]

        print('v',time()-t0)
        t0=time()


        for c1 in toUpdate:
            if (len(clusters[c1])==0):
                continue
            i1=indByC[c1]
            for c2 in NG.neighbors(c1):
                if (len(clusters[c2])==0):
                    continue

                i2=indByC[c2]
                if (i2<=i1):
                    continue


                D[i1,i2]=bhat(0, ds.distance(rep[c1],rep[c2],dsconf), V[c1], V[c2])

        if (np.all(np.isnan(D))):
            break

        vals=D[~np.isnan(D)].flatten()
        if (nc>200):
            thr=np.percentile(vals,90)
        else:
            thr=np.inf
        toUpdate=[]
        while (True):
            if (np.all(np.isnan(D))):
                break
            indMin=np.unravel_index(np.nanargmin(D), D.shape)        
            if (D[indMin]>thr):
                break
            c1=Cbyind[indMin[0]]
            c2=Cbyind[indMin[1]]
            m1=rep[c1]
            m2=rep[c2]
            merges.append((m1,m2))
            toUpdate.extend([c1,c2])
            Link(C, m1, m2)
            #print('{0} - {1} : {2:f}-'.format(m1,m2,D[indMin]))
            D[indMin[0],:]=np.nan
            D[indMin[1],:]=np.nan
            D[:,indMin[0]]=np.nan
            D[:,indMin[1]]=np.nan
        print('T',thr)

    return(merges)

def segmentation(G,ds,dsconf):
    MSF,psi=MSF_watershed(G,ds,dsconf)
    print('hier')

    
    #merges=otherHierarchy(G,psi,ds,dsconf)
    #plot3dWS(G,psi,ds,dsconf)
    #I,merges=uprooting(G,MSF,ds,dsconf)
    return(psi,merges)

if __name__ == '__main__':
    class dsdummy(object):
        def __init__(self,G):
            self._G=G.copy()
        def distance(self,n1,n2,dsconf):
            return(self._G[n1][n2]['data'])

    #tests for the algorithm
    G=nx.Graph()
    #    horz=[[7,5,5,7],
    #          [7,5,6,7],
    #          [8,3,2,3],
    #          [7,6,2,4]]
    horz=[[0,0,0,0],
          [0,0,0,0],
          [0,0,0,0],
          [0,0,0,0]]

    for y,line in enumerate(horz):
        for x,val in enumerate(line):
            G.add_edge((x,y),(x+1,y),data=val)

    vert=[[1,6,4,6,3],
          [8,8,9,8,9],
          [8,4,2,2,5]]

    for y,line in enumerate(vert):
        for x,val in enumerate(line):
            G.add_edge((x,y),(x,y+1),data=val)
    
    pos=dict()
    for n in G.nodes():
        pos[n]=[n[0],-n[1]]

    ds=dsdummy(G)
    
    baseLabels,merges=segmentation(G,ds,{})

    corr=[]
    labels=list(set(baseLabels.values()))
    print(len(set(labels)))
    print(len(labels))
    lastlabel=max(labels)
    corr.append(labels)
    for m in merges:
        tVec=corr[-1][:]
        lastlabel+=1
        l1=baseLabels[m[0]]
        l2=baseLabels[m[1]]
        oldL1=tVec[l1]
        oldL2=tVec[l2]
        for j in range(len(tVec)):
            if (tVec[j]==oldL1) or (tVec[j]==oldL2):
                tVec[j]=lastlabel
        corr.append(tVec)

    nLevels=len(merges)
    for i in range(nLevels):
        plt.figure()
        nx.draw(G,pos)
        data = nx.get_edge_attributes(G,'data')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=data)
        nl=dict()
        for n in G.nodes():
            nl[n]=corr[i][baseLabels[n]]
        nx.draw_networkx_labels(G,pos=pos,labels=nl)
    
    plt.show()
        
    
