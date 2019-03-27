all: US
	python3 srv.py conf.json

US: BASE_US ./US/cross.done

./US/cross.done: crossGeometryConnections.py ./data/US_tract_1970.shp ./data/US_tract_1980.shp ./data/US_tract_1990.shp ./data/US_tract_2000.shp ./data/US_tract_2010.shp
	python3 crossGeometryConnections.py ./US/ GISJOIN US_CT_1970 ./data/US_tract_1970.shp GISJOIN US_CT_1980 ./data/US_tract_1980.shp GISJOIN US_CT_1990 ./data/US_tract_1990.shp GISJOIN US_CT_2000 ./data/US_tract_2000.shp GISJOIN US_CT_2010 ./data/US_tract_2010.shp

BASE_US: ./US/US_CT_1970.gp ./US/US_CT_1980.gp ./US/US_CT_1990.gp ./US/US_CT_2000.gp ./US/US_CT_2010.gp

./US/US_CT_1970.gp: genBasegraph.py ./data/US_tract_1970.shp 
	python3 genBasegraph.py GISJOIN ./US/US_CT_1970.gp US_CT_1970 ./data/US_tract_1970.shp
./US/US_CT_1980.gp: genBasegraph.py ./data/US_tract_1980.shp 
	python3 genBasegraph.py GISJOIN ./US/US_CT_1980.gp US_CT_1980 ./data/US_tract_1980.shp
./US/US_CT_1990.gp: genBasegraph.py ./data/US_tract_1990.shp 
	python3 genBasegraph.py GISJOIN ./US/US_CT_1990.gp US_CT_1990 ./data/US_tract_1990.shp
./US/US_CT_2000.gp: genBasegraph.py ./data/US_tract_2000.shp 
	python3 genBasegraph.py GISJOIN ./US/US_CT_2000.gp US_CT_2000 ./data/US_tract_2000.shp
./US/US_CT_2010.gp: genBasegraph.py ./data/US_tract_2010.shp 
	python3 genBasegraph.py GISJOIN ./US/US_CT_2010.gp US_CT_2010 ./data/US_tract_2010.shp
