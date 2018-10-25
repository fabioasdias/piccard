import json
from glob import glob
from os.path import exists, join, basename
from shapely.geometry import shape, mapping, Point
import numpy as np

output={}
output["type"]="FeatureCollection"
output["features"]=[]


for city in glob('./cities/*'):
    useThis=basename(city)
    country=useThis[:2]
    name=useThis[3:]
    print(useThis)

    gj=join(city,'display.gj')
    if (not exists(gj)):
        continue
    with open(gj,'r') as fin:
        D=json.load(fin)

    points=[]
    for feat in D['features']:
        g=shape(feat['geometry'])
        points.append(list(g.representative_point().coords))
    points=np.array(points).squeeze()
    mp=np.median(points,axis=0)
    output['features'].append({
        "type":"Feature",
        "geometry": mapping(Point(*mp)),
        "properties": {
            "name": name,
            "country": country,
        }
    })
with open("points.gj",'w') as fout:
    json.dump(output,fout)



# {
#   "type": "FeatureCollection",
#   "features": [
#     {
#       "type": "Feature",
#       "geometry": {
#         "type": "Point",
#         "coordinates": [
#           -92.10250854492188,
#           43.32517767999296
#         ]
#       },
#       "properties": {}
#     }
#   ]
# }