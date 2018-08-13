import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
#from mpl_toolkits.basemap import Basemap
from mpl_toolkits.mplot3d import Axes3D #3d doesn't work without this
from matplotlib.patches import Polygon
from shapely.geometry.polygon import orient
import matplotlib.cm as cmx
import matplotlib.colors as colors
from random import random 

def plot3dWS(G,psi,ds,dsconf,showLabels=False):    
    years=[]

    cm=plt.get_cmap('viridis') 
    cNorm  = colors.Normalize(vmin=min(psi.values()), vmax=max(psi.values()))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for e in G.edges():

        c1=G.node[e[0]]['pos']
        c2=G.node[e[1]]['pos']
        lw=0.1+1*(1-ds.distance(e[0],e[1],dsconf))
        if (c1[2]==c2[2]):
            c='black'
        else:
            c='red'
        ax.plot(xs=[c1[0],c2[0]],ys=[c1[1],c2[1]],zs=[c1[2],c2[2]],c=c,linewidth=lw)
        if (showLabels):
            ax.text( (c1[0]+c2[0])/2.0,
                    (c1[1]+c2[1])/2.0,
                    (c1[0]+c2[0])/2.0,
                    "{0}".format(ds.distance(e[0],e[1],dsconf)))

    c=[]
    xs=[]
    ys=[]
    zs=[]
    for n in G.nodes():
        xs.append(G.node[n]['pos'][0])
        ys.append(G.node[n]['pos'][1])
        zs.append(G.node[n]['pos'][2])
        c.append(scalarMap.to_rgba(psi[n]))
        if (showLabels):
            ax.text(xs[-1], ys[-1], zs[-1],' '.join(['{0}'.format(ds.getValue(n,dsconf))])) 

    ax.scatter(xs, ys, zs, c=c, marker='o',alpha=1)
    

    plt.show()

def plotPolys(polylist,title=''):
    fig = plt.figure()
    plt.title(title)
    plt.set_cmap('tab20c')
    ax = fig.add_subplot(111)
    
    ax.set_aspect(1)
    patches = []
    c=[]
    for g in polylist:
        if g.geom_type == 'Polygon':
               patches.append(Polygon(np.asarray(orient(g).exterior.coords)))
               c.append(len(c))               
               continue
        for gg in g:
            if (g.bounds):
                patches.append(Polygon(np.asarray(orient(gg).exterior.coords)))
                if c:
                    c.append(c[-1])
                else:
                    c.append(0)

    p=PatchCollection(patches,alpha=0.4)
    p.set_array(np.array(c))
    ax.add_collection(p)
    plt.axis('tight')
    fig.colorbar(p, ax=ax)
    plt.show()

def plotGeoJsons(geodata):
    
    # lower left minx miny , upper right maxx maxy
    bounds = [-120, 43, -65, 60] # canada on 4269
    minx, miny, maxx, maxy = bounds
#    w, h = maxx - minx, maxy - miny

 
    
    for year in sorted(geodata.keys()):
        # create a new matplotlib figure and axes instance
        fig = plt.figure()
        plt.title('{0}'.format(year))
        ax = fig.add_subplot(111)
        # add a basemap and a small additional extent
#        m = Basemap(
#            projection='merc',
#            ellps = 'WGS84',
#            llcrnrlon=minx - 0.2 * w,
#            llcrnrlat=miny - 0.2 * h,
#            urcrnrlon=maxx + 0.2 * w,
#            urcrnrlat=maxy + 0.2 * h,
#            resolution='l')#            lat_ts=0,
#        m.drawcoastlines(linewidth=0.3)
#        m.drawmapboundary()
#        m.drawcountries()
#        m.fillcontinents()
#        m.drawstates()
        
        # set axes limits to basemap's coordinate reference system 
#        min_x, min_y = m(minx, miny)
#        max_x, max_y = m(maxx, maxy)
        #corr_w, corr_h = max_x - min_x, max_y - min_y
#        ax.set_xlim(min_x - 0.2 * corr_w, max_x + 0.2 * corr_w)
        #ax.set_ylim(min_y - 0.2 * corr_h, max_y + 0.2 * corr_h)
        # square up axes and basemap
        ax.set_aspect(1)

        patches = []
        for ctid,Mgeom in geodata[year]:
            if Mgeom.geom_type == 'Polygon':
                patches.append(Polygon(np.asarray(orient(Mgeom).exterior.coords)))
                continue
            for geom in Mgeom:
                patches.append(Polygon(
                    np.asarray(orient(geom).exterior.coords),
                    ls='solid',
                    color=[random(),random(),random()]))
                
        ax.add_collection(PatchCollection(patches))
        plt.axis('tight')
 #       ax.set_xticks([])
 #       ax.set_yticks([])                       
 #       plt.tight_layout()

    plt.show()
