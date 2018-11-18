import numpy as np
import networkx as nx
from collections import deque
#import matplotlib.pylab as plt
from numpy.linalg import norm

from time import time
from fibonacci_heap_mod import Fibonacci_heap


def removeLayer(G, layer):
    for n in G.nodes():
        if layer in G.node[n]:
            del(G.node[n][layer])
    for e in G.edges():
        if (layer in G[e[0]][e[1]]):
            del(G[e[0]][e[1]][layer])


def Fminus(G, n, layer):
    return(min([e[2][layer] for e in G.edges(n, data=True)]))


def stream(G, psi, x, layer):
    L = [x, ]
    lp = deque([x, ])
    while (len(lp) > 0):
        y = lp.popleft()
        breadth_first = True
        allZ = [z for z in G.neighbors(y) if (
            z not in L) and G[y][z][layer] == Fminus(G, y, layer)]
        if (not allZ):
            break
        for z in allZ:
            if (not breadth_first):
                break
            if (psi[z] >= 0):
                return([L, psi[z]])
            elif Fminus(G, z, layer) < Fminus(G, y, layer):
                L.append(z)
                lp.clear()
                lp.append(z)
                breadth_first = False
            else:
                L.append(z)
                lp.append(z)
    return (L, -1)


def watershed(G, layer):
    psi = dict()
    for n in sorted(G.nodes()):
        psi[n] = -1
    nb_labs = 0
    for x in sorted(G.nodes()):
        if (psi[x] == -1):
            [L, lab] = stream(G, psi, x, layer)
            if (lab == -1):
                for y in L:
                    psi[y] = nb_labs
                nb_labs += 1
            else:
                for y in L:
                    psi[y] = lab
    return(psi)


def hierMWW(D, Gr, NbyInd, dsconf, maxClusters=20):

    IndByN = {NbyInd[i]: i for i in NbyInd}

    G = Gr.copy()

    # NaNs=[]
    # NaNInds=[]
    # for i in range(D.shape[0]):
    #     N=np.isnan(D[i,:])
    #     if np.sum(N)<(D.shape[0]-1):
    #         NaNInds=[j for j in (np.where(N)[0]).squeeze()]
    #         NaNs=[NbyInd[j] for j in NaNInds]
    #         break
    # NNaNs=len(NaNs)

    lName = 'data'
    for e in G.edges():
        i1 = IndByN[e[0]]
        i2 = IndByN[e[1]]
        cD = D[i1, i2]
        G[e[0]][e[1]][lName] = cD


    psi = watershed(G, lName)

    T=np.percentile(D,25)


    nClusters = len(set(psi.values()))
    lastNClusters = nClusters
    while (nClusters > maxClusters):
        clInds = dict()
        for L in set(psi.values()):
            clInds[L] = []
        for n in psi:
            clInds[psi[n]].append(IndByN[n])

        H = Fibonacci_heap()
        Lused = dict()
        for e in G.edges():
            l1 = min(psi[e[0]], psi[e[1]])
            l2 = max(psi[e[0]], psi[e[1]])
            if (l1 != l2):
                if (l1 not in Lused):
                    Lused[l1] = dict()
                if (l2 not in Lused[l1]):
                    Lused[l1][l2] = True
                    DD=(D[clInds[l1], :])[:, clInds[l2]]
                    if not (np.all(np.isnan(DD))):
                        P=np.nanmedian(DD)
                        if not np.isnan(P):
                            H.enqueue((l1, l2), P)

        used = []
        while len(H) > 0:
            el = H.dequeue_min()
            if (el.get_priority() > T):
                if (nClusters != lastNClusters):
                    lastNClusters = nClusters
                    print('skip', nClusters, el.get_priority())
                    break

            l1, l2 = el.get_value()
            if (l1 in used) or (l2 in used):
                continue

            used.extend([l1, l2])

            for n in psi:
                if (psi[n] == l2):
                    psi[n] = l1
            nClusters -= 1
            if (nClusters == maxClusters):
                break

    labels = list(sorted(set(psi.values())))
    print('now with ', len(labels))
    for n in psi:
        psi[n] = labels.index(psi[n])
    corr = []
    corr.append(list(range(len(labels))))
    nextlabel = len(labels)
    while (nClusters>1):
        print('#clusters', nClusters)
        H = Fibonacci_heap()
        Lused = dict()

        clInds = dict()
        for L in corr[-1]:
            clInds[L] = []
        for n in psi:
            clInds[corr[-1][psi[n]]].append(IndByN[n])

        for e in G.edges():
            l1 = min(corr[-1][psi[e[0]]], corr[-1][psi[e[1]]])
            l2 = max(corr[-1][psi[e[0]]], corr[-1][psi[e[1]]])
            if (l1 != l2):
                if (l1 not in Lused):
                    Lused[l1] = dict()
                if (l2 not in Lused[l1]):
                    Lused[l1][l2] = True
                    H.enqueue((l1, l2), np.nanmedian((D[clInds[l1], :])[:, clInds[l2]]))

        el = H.dequeue_min()
        l1, l2 = el.get_value()
        print(el.get_priority())

        tVec = corr[-1][:]
        for i in range(len(tVec)):
            if (tVec[i] == l1) or (tVec[i] == l2):
                tVec[i] = nextlabel
        corr.append(tVec)
        nextlabel += 1
        nClusters -= 1

    clusters = dict()
    for i in range(len(corr)):
        for n in psi:
            c = corr[i][psi[n]]
            if c not in clusters:
                clusters[c] = []
            clusters[c].append(n)
        for c in clusters:
            clusters[c] = list(set(clusters[c]))

    return(psi, corr, clusters)
