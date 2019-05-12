all: US
	python3 srv.py conf.json

US: BASE_US ./db/cross.done

./db/cross.done: crossGeometryConnections.py ./shapefiles/US_tract_1970.shp ./shapefiles/US_tract_1980.shp ./shapefiles/US_tract_1990.shp ./shapefiles/US_tract_2000.shp ./shapefiles/US_tract_2010.shp
	python3 crossGeometryConnections.py ./US/ GISJOIN US_CT_1970 ./shapefiles/US_tract_1970.shp GISJOIN US_CT_1980 ./shapefiles/US_tract_1980.shp GISJOIN US_CT_1990 ./shapefiles/US_tract_1990.shp GISJOIN US_CT_2000 ./shapefiles/US_tract_2000.shp GISJOIN US_CT_2010 ./shapefiles/US_tract_2010.shp

BASE_US: ./db/US_CT_1970.gp ./db/US_CT_1980.gp ./db/US_CT_1990.gp ./db/US_CT_2000.gp ./db/US_CT_2010.gp

./db/US_CT_1970.gp: genBasegraph.py ./shapefiles/US_tract_1970.shp 
	python3 genBasegraph.py GISJOIN ./db/US_CT_1970.gp US_CT_1970 ./shapefiles/US_tract_1970.shp
./db/US_CT_1980.gp: genBasegraph.py ./shapefiles/US_tract_1980.shp 
	python3 genBasegraph.py GISJOIN ./db/US_CT_1980.gp US_CT_1980 ./shapefiles/US_tract_1980.shp
./db/US_CT_1990.gp: genBasegraph.py ./shapefiles/US_tract_1990.shp 
	python3 genBasegraph.py GISJOIN ./db/US_CT_1990.gp US_CT_1990 ./shapefiles/US_tract_1990.shp
./db/US_CT_2000.gp: genBasegraph.py ./shapefiles/US_tract_2000.shp 
	python3 genBasegraph.py GISJOIN ./db/US_CT_2000.gp US_CT_2000 ./shapefiles/US_tract_2000.shp
./db/US_CT_2010.gp: genBasegraph.py ./shapefiles/US_tract_2010.shp 
	python3 genBasegraph.py GISJOIN ./db/US_CT_2010.gp US_CT_2010 ./shapefiles/US_tract_2010.shp
