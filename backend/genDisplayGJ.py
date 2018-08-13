from util import geoJsons
from util import indexedPols,split    
from shapely.geometry import shape   
from shapely.ops import unary_union
import sys
from auxplots import plotPolys


if __name__ == '__main__':
    if (len(sys.argv))!=3:
        print(".py <geojsons.zip> OUTPUT.gj")
        exit(-1)

    areaT=1e-9
    print('Make sure you are using 4269!')
                
#    years=sorted(geo.keys())
    resPols=indexedPols()
    print('Display geojson')
    
    with geoJsons(sys.argv[1]) as gj:
        for year,cgj in gj:
            print('\n\n')
            print(year)
            toInsert=[]
            last=[]
            for fcount,feat in enumerate(cgj['features']):
                if (len(feat['geometry']['coordinates'])==0):
                    continue
                A=shape(feat['geometry']).buffer(0)
                if (A.is_empty):
                    continue
                I=resPols.search(A.buffer(-1e-6).buffer(0))
                
                nodesA=[(year,feat['properties']['CT_ID']),]
                if (not I):
                    resPols.insert(A,props={'nodes':nodesA, 'area':A.area})
                    continue

                UB=[]
                for nii in I:
                    B=resPols.remove(nii)
                    _,AinterB,bp=split(A,B['geometry'])
                    if (AinterB is not None) and (not AinterB.is_empty):
                        resPols.insert(AinterB,props={'nodes':nodesA+B['properties']['nodes'], 'area':AinterB.area},areaThreshold=areaT)
                    if (bp is not None) and (not bp.is_empty):
                        resPols.insert(bp,props={'nodes':B['properties']['nodes'], 'area':bp.area},areaThreshold=areaT)

                    UB.append(B['geometry'])

                if (UB):
                    try:
                        UB=unary_union(UB)
                    except:
                        UB=[x.buffer(1e-6) for x in UB]
                        UB=unary_union([x for x in UB if (not x.is_empty)])
                        UB=UB.buffer(-1e-6)
                        

                    try:
                        UB=UB.buffer(2e-5).buffer(-2e-5) #removes slits                            
                    except:
                        UB=UB.buffer(2e-5).buffer(-2e-5).buffer(0) #removes slits                            

                    try:
                        newA=A.difference(UB)
                    except:   
                        if (not A.is_valid):
                            A=A.buffer(0)
                        if (not UB.is_valid):
                            UB=UB.buffer(0)
                        newA=A.buffer(0).difference(UB.buffer(0)).buffer(0)

                    toInsert.append({'geometry':newA,'nodes':nodesA})

                lnext='{0:02d}'.format(round(10*fcount/len(cgj['features'])))
                if ((last!=lnext)) or (not last):
                    last=lnext
                    print(lnext)
                                    
            for pol in toInsert:
                if (pol['geometry'] is not None) and (not pol['geometry'].is_empty):
                    resPols.insert(pol['geometry'],props={'nodes':pol['nodes'], 'area':pol['geometry'].area},areaThreshold=areaT)
            
            #resPols.saveGeoJson('out{0}.gj'.format(year))
    resPols.saveGeoJson(sys.argv[2],display_id=True,area=True)
