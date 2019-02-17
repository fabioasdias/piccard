all: US
	python3 srv.py conf.json

US: ./US/basegraph.gp
	
./US/basegraph.gp: genBasegraph.py ./data/US_tract_1970.shp ./data/US_tract_1980.shp ./data/US_tract_1990.shp ./data/US_tract_2000.shp ./data/US_tract_2010.shp
	python3 genBasegraph.py GISJOIN ./US/basegraph.gp 1970 ./data/US_tract_1970.shp 1980 ./data/US_tract_1980.shp 1990 ./data/US_tract_1990.shp 2000 ./data/US_tract_2000.shp 2010 ./data/US_tract_2010.shp
