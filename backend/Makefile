all: srv.py Toronto Greater_Toronto_Area Montreal Vancouver Calgary Edmonton Halifax Ottawa Quebec_City Regina Saskatoon St_John Winnipeg LA_County Staten_Island Manhattan Queens The_Bronx Brooklyn Chicago Atlanta Austin Baltimore Boston Columbus Dallas Denver Fargo Houston Indianapolis Jacksonville Kansas_City Las_Vegas Miami Minneapolis Philadelphia Phoenix Salt_Lake_City San_Antonio San_Francisco Seattle Washington_DC Synthetic
	 python3 srv.py conf.json

./cities/CA_Toronto/normGeoJsons.zip: normGJVars.py ./cities/CA_Toronto/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Toronto/geojsons.zip CA
	zip -9j ./cities/CA_Toronto/normGeoJsons.zip ./cities/CA_Toronto/*_n.gj
	rm ./cities/CA_Toronto/*_n.gj
./cities/CA_Toronto/display.json: ./cities/CA_Toronto/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Toronto/normGeoJsons.zip ./cities/CA_Toronto/display.json
./cities/CA_Toronto/basegraph.gp: ./cities/CA_Toronto/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Toronto/normGeoJsons.zip ./cities/CA_Toronto/basegraph.gp
Toronto: ./cities/CA_Toronto/basegraph.gp ./cities/CA_Toronto/normGeoJsons.zip ./cities/CA_Toronto/display.json
./cities/CA_Greater_Toronto_Area/normGeoJsons.zip: normGJVars.py ./cities/CA_Greater_Toronto_Area/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Greater_Toronto_Area/geojsons.zip CA
	zip -9j ./cities/CA_Greater_Toronto_Area/normGeoJsons.zip ./cities/CA_Greater_Toronto_Area/*_n.gj
	rm ./cities/CA_Greater_Toronto_Area/*_n.gj
./cities/CA_Greater_Toronto_Area/display.json: ./cities/CA_Greater_Toronto_Area/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Greater_Toronto_Area/normGeoJsons.zip ./cities/CA_Greater_Toronto_Area/display.json
./cities/CA_Greater_Toronto_Area/basegraph.gp: ./cities/CA_Greater_Toronto_Area/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Greater_Toronto_Area/normGeoJsons.zip ./cities/CA_Greater_Toronto_Area/basegraph.gp
Greater_Toronto_Area: ./cities/CA_Greater_Toronto_Area/basegraph.gp ./cities/CA_Greater_Toronto_Area/normGeoJsons.zip ./cities/CA_Greater_Toronto_Area/display.json
./cities/CA_Montreal/normGeoJsons.zip: normGJVars.py ./cities/CA_Montreal/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Montreal/geojsons.zip CA
	zip -9j ./cities/CA_Montreal/normGeoJsons.zip ./cities/CA_Montreal/*_n.gj
	rm ./cities/CA_Montreal/*_n.gj
./cities/CA_Montreal/display.json: ./cities/CA_Montreal/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Montreal/normGeoJsons.zip ./cities/CA_Montreal/display.json
./cities/CA_Montreal/basegraph.gp: ./cities/CA_Montreal/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Montreal/normGeoJsons.zip ./cities/CA_Montreal/basegraph.gp
Montreal: ./cities/CA_Montreal/basegraph.gp ./cities/CA_Montreal/normGeoJsons.zip ./cities/CA_Montreal/display.json
./cities/CA_Vancouver/normGeoJsons.zip: normGJVars.py ./cities/CA_Vancouver/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Vancouver/geojsons.zip CA
	zip -9j ./cities/CA_Vancouver/normGeoJsons.zip ./cities/CA_Vancouver/*_n.gj
	rm ./cities/CA_Vancouver/*_n.gj
./cities/CA_Vancouver/display.json: ./cities/CA_Vancouver/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Vancouver/normGeoJsons.zip ./cities/CA_Vancouver/display.json
./cities/CA_Vancouver/basegraph.gp: ./cities/CA_Vancouver/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Vancouver/normGeoJsons.zip ./cities/CA_Vancouver/basegraph.gp
Vancouver: ./cities/CA_Vancouver/basegraph.gp ./cities/CA_Vancouver/normGeoJsons.zip ./cities/CA_Vancouver/display.json
./cities/CA_Calgary/normGeoJsons.zip: normGJVars.py ./cities/CA_Calgary/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Calgary/geojsons.zip CA
	zip -9j ./cities/CA_Calgary/normGeoJsons.zip ./cities/CA_Calgary/*_n.gj
	rm ./cities/CA_Calgary/*_n.gj
./cities/CA_Calgary/display.json: ./cities/CA_Calgary/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Calgary/normGeoJsons.zip ./cities/CA_Calgary/display.json
./cities/CA_Calgary/basegraph.gp: ./cities/CA_Calgary/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Calgary/normGeoJsons.zip ./cities/CA_Calgary/basegraph.gp
Calgary: ./cities/CA_Calgary/basegraph.gp ./cities/CA_Calgary/normGeoJsons.zip ./cities/CA_Calgary/display.json
./cities/CA_Edmonton/normGeoJsons.zip: normGJVars.py ./cities/CA_Edmonton/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Edmonton/geojsons.zip CA
	zip -9j ./cities/CA_Edmonton/normGeoJsons.zip ./cities/CA_Edmonton/*_n.gj
	rm ./cities/CA_Edmonton/*_n.gj
./cities/CA_Edmonton/display.json: ./cities/CA_Edmonton/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Edmonton/normGeoJsons.zip ./cities/CA_Edmonton/display.json
./cities/CA_Edmonton/basegraph.gp: ./cities/CA_Edmonton/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Edmonton/normGeoJsons.zip ./cities/CA_Edmonton/basegraph.gp
Edmonton: ./cities/CA_Edmonton/basegraph.gp ./cities/CA_Edmonton/normGeoJsons.zip ./cities/CA_Edmonton/display.json
./cities/CA_Halifax/normGeoJsons.zip: normGJVars.py ./cities/CA_Halifax/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Halifax/geojsons.zip CA
	zip -9j ./cities/CA_Halifax/normGeoJsons.zip ./cities/CA_Halifax/*_n.gj
	rm ./cities/CA_Halifax/*_n.gj
./cities/CA_Halifax/display.json: ./cities/CA_Halifax/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Halifax/normGeoJsons.zip ./cities/CA_Halifax/display.json
./cities/CA_Halifax/basegraph.gp: ./cities/CA_Halifax/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Halifax/normGeoJsons.zip ./cities/CA_Halifax/basegraph.gp
Halifax: ./cities/CA_Halifax/basegraph.gp ./cities/CA_Halifax/normGeoJsons.zip ./cities/CA_Halifax/display.json
./cities/CA_Ottawa/normGeoJsons.zip: normGJVars.py ./cities/CA_Ottawa/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Ottawa/geojsons.zip CA
	zip -9j ./cities/CA_Ottawa/normGeoJsons.zip ./cities/CA_Ottawa/*_n.gj
	rm ./cities/CA_Ottawa/*_n.gj
./cities/CA_Ottawa/display.json: ./cities/CA_Ottawa/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Ottawa/normGeoJsons.zip ./cities/CA_Ottawa/display.json
./cities/CA_Ottawa/basegraph.gp: ./cities/CA_Ottawa/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Ottawa/normGeoJsons.zip ./cities/CA_Ottawa/basegraph.gp
Ottawa: ./cities/CA_Ottawa/basegraph.gp ./cities/CA_Ottawa/normGeoJsons.zip ./cities/CA_Ottawa/display.json
./cities/CA_Quebec_City/normGeoJsons.zip: normGJVars.py ./cities/CA_Quebec_City/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Quebec_City/geojsons.zip CA
	zip -9j ./cities/CA_Quebec_City/normGeoJsons.zip ./cities/CA_Quebec_City/*_n.gj
	rm ./cities/CA_Quebec_City/*_n.gj
./cities/CA_Quebec_City/display.json: ./cities/CA_Quebec_City/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Quebec_City/normGeoJsons.zip ./cities/CA_Quebec_City/display.json
./cities/CA_Quebec_City/basegraph.gp: ./cities/CA_Quebec_City/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Quebec_City/normGeoJsons.zip ./cities/CA_Quebec_City/basegraph.gp
Quebec_City: ./cities/CA_Quebec_City/basegraph.gp ./cities/CA_Quebec_City/normGeoJsons.zip ./cities/CA_Quebec_City/display.json
./cities/CA_Regina/normGeoJsons.zip: normGJVars.py ./cities/CA_Regina/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Regina/geojsons.zip CA
	zip -9j ./cities/CA_Regina/normGeoJsons.zip ./cities/CA_Regina/*_n.gj
	rm ./cities/CA_Regina/*_n.gj
./cities/CA_Regina/display.json: ./cities/CA_Regina/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Regina/normGeoJsons.zip ./cities/CA_Regina/display.json
./cities/CA_Regina/basegraph.gp: ./cities/CA_Regina/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Regina/normGeoJsons.zip ./cities/CA_Regina/basegraph.gp
Regina: ./cities/CA_Regina/basegraph.gp ./cities/CA_Regina/normGeoJsons.zip ./cities/CA_Regina/display.json
./cities/CA_Saskatoon/normGeoJsons.zip: normGJVars.py ./cities/CA_Saskatoon/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Saskatoon/geojsons.zip CA
	zip -9j ./cities/CA_Saskatoon/normGeoJsons.zip ./cities/CA_Saskatoon/*_n.gj
	rm ./cities/CA_Saskatoon/*_n.gj
./cities/CA_Saskatoon/display.json: ./cities/CA_Saskatoon/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Saskatoon/normGeoJsons.zip ./cities/CA_Saskatoon/display.json
./cities/CA_Saskatoon/basegraph.gp: ./cities/CA_Saskatoon/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Saskatoon/normGeoJsons.zip ./cities/CA_Saskatoon/basegraph.gp
Saskatoon: ./cities/CA_Saskatoon/basegraph.gp ./cities/CA_Saskatoon/normGeoJsons.zip ./cities/CA_Saskatoon/display.json
./cities/CA_St_John/normGeoJsons.zip: normGJVars.py ./cities/CA_St_John/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_St_John/geojsons.zip CA
	zip -9j ./cities/CA_St_John/normGeoJsons.zip ./cities/CA_St_John/*_n.gj
	rm ./cities/CA_St_John/*_n.gj
./cities/CA_St_John/display.json: ./cities/CA_St_John/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_St_John/normGeoJsons.zip ./cities/CA_St_John/display.json
./cities/CA_St_John/basegraph.gp: ./cities/CA_St_John/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_St_John/normGeoJsons.zip ./cities/CA_St_John/basegraph.gp
St_John: ./cities/CA_St_John/basegraph.gp ./cities/CA_St_John/normGeoJsons.zip ./cities/CA_St_John/display.json
./cities/CA_Winnipeg/normGeoJsons.zip: normGJVars.py ./cities/CA_Winnipeg/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/CA_Winnipeg/geojsons.zip CA
	zip -9j ./cities/CA_Winnipeg/normGeoJsons.zip ./cities/CA_Winnipeg/*_n.gj
	rm ./cities/CA_Winnipeg/*_n.gj
./cities/CA_Winnipeg/display.json: ./cities/CA_Winnipeg/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/CA_Winnipeg/normGeoJsons.zip ./cities/CA_Winnipeg/display.json
./cities/CA_Winnipeg/basegraph.gp: ./cities/CA_Winnipeg/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/CA_Winnipeg/normGeoJsons.zip ./cities/CA_Winnipeg/basegraph.gp
Winnipeg: ./cities/CA_Winnipeg/basegraph.gp ./cities/CA_Winnipeg/normGeoJsons.zip ./cities/CA_Winnipeg/display.json
./cities/US_LA_County/normGeoJsons.zip: normGJVars.py ./cities/US_LA_County/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_LA_County/geojsons.zip US
	zip -9j ./cities/US_LA_County/normGeoJsons.zip ./cities/US_LA_County/*_n.gj
	rm ./cities/US_LA_County/*_n.gj
./cities/US_LA_County/display.json: ./cities/US_LA_County/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_LA_County/normGeoJsons.zip ./cities/US_LA_County/display.json
./cities/US_LA_County/basegraph.gp: ./cities/US_LA_County/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_LA_County/normGeoJsons.zip ./cities/US_LA_County/basegraph.gp
LA_County: ./cities/US_LA_County/basegraph.gp ./cities/US_LA_County/normGeoJsons.zip ./cities/US_LA_County/display.json
./cities/US_Staten_Island/normGeoJsons.zip: normGJVars.py ./cities/US_Staten_Island/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Staten_Island/geojsons.zip US
	zip -9j ./cities/US_Staten_Island/normGeoJsons.zip ./cities/US_Staten_Island/*_n.gj
	rm ./cities/US_Staten_Island/*_n.gj
./cities/US_Staten_Island/display.json: ./cities/US_Staten_Island/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Staten_Island/normGeoJsons.zip ./cities/US_Staten_Island/display.json
./cities/US_Staten_Island/basegraph.gp: ./cities/US_Staten_Island/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Staten_Island/normGeoJsons.zip ./cities/US_Staten_Island/basegraph.gp
Staten_Island: ./cities/US_Staten_Island/basegraph.gp ./cities/US_Staten_Island/normGeoJsons.zip ./cities/US_Staten_Island/display.json
./cities/US_Manhattan/normGeoJsons.zip: normGJVars.py ./cities/US_Manhattan/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Manhattan/geojsons.zip US
	zip -9j ./cities/US_Manhattan/normGeoJsons.zip ./cities/US_Manhattan/*_n.gj
	rm ./cities/US_Manhattan/*_n.gj
./cities/US_Manhattan/display.json: ./cities/US_Manhattan/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Manhattan/normGeoJsons.zip ./cities/US_Manhattan/display.json
./cities/US_Manhattan/basegraph.gp: ./cities/US_Manhattan/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Manhattan/normGeoJsons.zip ./cities/US_Manhattan/basegraph.gp
Manhattan: ./cities/US_Manhattan/basegraph.gp ./cities/US_Manhattan/normGeoJsons.zip ./cities/US_Manhattan/display.json
./cities/US_Queens/normGeoJsons.zip: normGJVars.py ./cities/US_Queens/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Queens/geojsons.zip US
	zip -9j ./cities/US_Queens/normGeoJsons.zip ./cities/US_Queens/*_n.gj
	rm ./cities/US_Queens/*_n.gj
./cities/US_Queens/display.json: ./cities/US_Queens/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Queens/normGeoJsons.zip ./cities/US_Queens/display.json
./cities/US_Queens/basegraph.gp: ./cities/US_Queens/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Queens/normGeoJsons.zip ./cities/US_Queens/basegraph.gp
Queens: ./cities/US_Queens/basegraph.gp ./cities/US_Queens/normGeoJsons.zip ./cities/US_Queens/display.json
./cities/US_The_Bronx/normGeoJsons.zip: normGJVars.py ./cities/US_The_Bronx/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_The_Bronx/geojsons.zip US
	zip -9j ./cities/US_The_Bronx/normGeoJsons.zip ./cities/US_The_Bronx/*_n.gj
	rm ./cities/US_The_Bronx/*_n.gj
./cities/US_The_Bronx/display.json: ./cities/US_The_Bronx/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_The_Bronx/normGeoJsons.zip ./cities/US_The_Bronx/display.json
./cities/US_The_Bronx/basegraph.gp: ./cities/US_The_Bronx/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_The_Bronx/normGeoJsons.zip ./cities/US_The_Bronx/basegraph.gp
The_Bronx: ./cities/US_The_Bronx/basegraph.gp ./cities/US_The_Bronx/normGeoJsons.zip ./cities/US_The_Bronx/display.json
./cities/US_Brooklyn/normGeoJsons.zip: normGJVars.py ./cities/US_Brooklyn/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Brooklyn/geojsons.zip US
	zip -9j ./cities/US_Brooklyn/normGeoJsons.zip ./cities/US_Brooklyn/*_n.gj
	rm ./cities/US_Brooklyn/*_n.gj
./cities/US_Brooklyn/display.json: ./cities/US_Brooklyn/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Brooklyn/normGeoJsons.zip ./cities/US_Brooklyn/display.json
./cities/US_Brooklyn/basegraph.gp: ./cities/US_Brooklyn/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Brooklyn/normGeoJsons.zip ./cities/US_Brooklyn/basegraph.gp
Brooklyn: ./cities/US_Brooklyn/basegraph.gp ./cities/US_Brooklyn/normGeoJsons.zip ./cities/US_Brooklyn/display.json
./cities/US_Chicago/normGeoJsons.zip: normGJVars.py ./cities/US_Chicago/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Chicago/geojsons.zip US
	zip -9j ./cities/US_Chicago/normGeoJsons.zip ./cities/US_Chicago/*_n.gj
	rm ./cities/US_Chicago/*_n.gj
./cities/US_Chicago/display.json: ./cities/US_Chicago/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Chicago/normGeoJsons.zip ./cities/US_Chicago/display.json
./cities/US_Chicago/basegraph.gp: ./cities/US_Chicago/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Chicago/normGeoJsons.zip ./cities/US_Chicago/basegraph.gp
Chicago: ./cities/US_Chicago/basegraph.gp ./cities/US_Chicago/normGeoJsons.zip ./cities/US_Chicago/display.json
./cities/US_Atlanta/normGeoJsons.zip: normGJVars.py ./cities/US_Atlanta/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Atlanta/geojsons.zip US
	zip -9j ./cities/US_Atlanta/normGeoJsons.zip ./cities/US_Atlanta/*_n.gj
	rm ./cities/US_Atlanta/*_n.gj
./cities/US_Atlanta/display.json: ./cities/US_Atlanta/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Atlanta/normGeoJsons.zip ./cities/US_Atlanta/display.json
./cities/US_Atlanta/basegraph.gp: ./cities/US_Atlanta/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Atlanta/normGeoJsons.zip ./cities/US_Atlanta/basegraph.gp
Atlanta: ./cities/US_Atlanta/basegraph.gp ./cities/US_Atlanta/normGeoJsons.zip ./cities/US_Atlanta/display.json
./cities/US_Austin/normGeoJsons.zip: normGJVars.py ./cities/US_Austin/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Austin/geojsons.zip US
	zip -9j ./cities/US_Austin/normGeoJsons.zip ./cities/US_Austin/*_n.gj
	rm ./cities/US_Austin/*_n.gj
./cities/US_Austin/display.json: ./cities/US_Austin/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Austin/normGeoJsons.zip ./cities/US_Austin/display.json
./cities/US_Austin/basegraph.gp: ./cities/US_Austin/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Austin/normGeoJsons.zip ./cities/US_Austin/basegraph.gp
Austin: ./cities/US_Austin/basegraph.gp ./cities/US_Austin/normGeoJsons.zip ./cities/US_Austin/display.json
./cities/US_Baltimore/normGeoJsons.zip: normGJVars.py ./cities/US_Baltimore/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Baltimore/geojsons.zip US
	zip -9j ./cities/US_Baltimore/normGeoJsons.zip ./cities/US_Baltimore/*_n.gj
	rm ./cities/US_Baltimore/*_n.gj
./cities/US_Baltimore/display.json: ./cities/US_Baltimore/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Baltimore/normGeoJsons.zip ./cities/US_Baltimore/display.json
./cities/US_Baltimore/basegraph.gp: ./cities/US_Baltimore/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Baltimore/normGeoJsons.zip ./cities/US_Baltimore/basegraph.gp
Baltimore: ./cities/US_Baltimore/basegraph.gp ./cities/US_Baltimore/normGeoJsons.zip ./cities/US_Baltimore/display.json
./cities/US_Boston/normGeoJsons.zip: normGJVars.py ./cities/US_Boston/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Boston/geojsons.zip US
	zip -9j ./cities/US_Boston/normGeoJsons.zip ./cities/US_Boston/*_n.gj
	rm ./cities/US_Boston/*_n.gj
./cities/US_Boston/display.json: ./cities/US_Boston/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Boston/normGeoJsons.zip ./cities/US_Boston/display.json
./cities/US_Boston/basegraph.gp: ./cities/US_Boston/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Boston/normGeoJsons.zip ./cities/US_Boston/basegraph.gp
Boston: ./cities/US_Boston/basegraph.gp ./cities/US_Boston/normGeoJsons.zip ./cities/US_Boston/display.json
./cities/US_Columbus/normGeoJsons.zip: normGJVars.py ./cities/US_Columbus/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Columbus/geojsons.zip US
	zip -9j ./cities/US_Columbus/normGeoJsons.zip ./cities/US_Columbus/*_n.gj
	rm ./cities/US_Columbus/*_n.gj
./cities/US_Columbus/display.json: ./cities/US_Columbus/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Columbus/normGeoJsons.zip ./cities/US_Columbus/display.json
./cities/US_Columbus/basegraph.gp: ./cities/US_Columbus/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Columbus/normGeoJsons.zip ./cities/US_Columbus/basegraph.gp
Columbus: ./cities/US_Columbus/basegraph.gp ./cities/US_Columbus/normGeoJsons.zip ./cities/US_Columbus/display.json
./cities/US_Dallas/normGeoJsons.zip: normGJVars.py ./cities/US_Dallas/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Dallas/geojsons.zip US
	zip -9j ./cities/US_Dallas/normGeoJsons.zip ./cities/US_Dallas/*_n.gj
	rm ./cities/US_Dallas/*_n.gj
./cities/US_Dallas/display.json: ./cities/US_Dallas/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Dallas/normGeoJsons.zip ./cities/US_Dallas/display.json
./cities/US_Dallas/basegraph.gp: ./cities/US_Dallas/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Dallas/normGeoJsons.zip ./cities/US_Dallas/basegraph.gp
Dallas: ./cities/US_Dallas/basegraph.gp ./cities/US_Dallas/normGeoJsons.zip ./cities/US_Dallas/display.json
./cities/US_Denver/normGeoJsons.zip: normGJVars.py ./cities/US_Denver/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Denver/geojsons.zip US
	zip -9j ./cities/US_Denver/normGeoJsons.zip ./cities/US_Denver/*_n.gj
	rm ./cities/US_Denver/*_n.gj
./cities/US_Denver/display.json: ./cities/US_Denver/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Denver/normGeoJsons.zip ./cities/US_Denver/display.json
./cities/US_Denver/basegraph.gp: ./cities/US_Denver/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Denver/normGeoJsons.zip ./cities/US_Denver/basegraph.gp
Denver: ./cities/US_Denver/basegraph.gp ./cities/US_Denver/normGeoJsons.zip ./cities/US_Denver/display.json
./cities/US_Fargo/normGeoJsons.zip: normGJVars.py ./cities/US_Fargo/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Fargo/geojsons.zip US
	zip -9j ./cities/US_Fargo/normGeoJsons.zip ./cities/US_Fargo/*_n.gj
	rm ./cities/US_Fargo/*_n.gj
./cities/US_Fargo/display.json: ./cities/US_Fargo/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Fargo/normGeoJsons.zip ./cities/US_Fargo/display.json
./cities/US_Fargo/basegraph.gp: ./cities/US_Fargo/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Fargo/normGeoJsons.zip ./cities/US_Fargo/basegraph.gp
Fargo: ./cities/US_Fargo/basegraph.gp ./cities/US_Fargo/normGeoJsons.zip ./cities/US_Fargo/display.json
./cities/US_Houston/normGeoJsons.zip: normGJVars.py ./cities/US_Houston/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Houston/geojsons.zip US
	zip -9j ./cities/US_Houston/normGeoJsons.zip ./cities/US_Houston/*_n.gj
	rm ./cities/US_Houston/*_n.gj
./cities/US_Houston/display.json: ./cities/US_Houston/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Houston/normGeoJsons.zip ./cities/US_Houston/display.json
./cities/US_Houston/basegraph.gp: ./cities/US_Houston/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Houston/normGeoJsons.zip ./cities/US_Houston/basegraph.gp
Houston: ./cities/US_Houston/basegraph.gp ./cities/US_Houston/normGeoJsons.zip ./cities/US_Houston/display.json
./cities/US_Indianapolis/normGeoJsons.zip: normGJVars.py ./cities/US_Indianapolis/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Indianapolis/geojsons.zip US
	zip -9j ./cities/US_Indianapolis/normGeoJsons.zip ./cities/US_Indianapolis/*_n.gj
	rm ./cities/US_Indianapolis/*_n.gj
./cities/US_Indianapolis/display.json: ./cities/US_Indianapolis/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Indianapolis/normGeoJsons.zip ./cities/US_Indianapolis/display.json
./cities/US_Indianapolis/basegraph.gp: ./cities/US_Indianapolis/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Indianapolis/normGeoJsons.zip ./cities/US_Indianapolis/basegraph.gp
Indianapolis: ./cities/US_Indianapolis/basegraph.gp ./cities/US_Indianapolis/normGeoJsons.zip ./cities/US_Indianapolis/display.json
./cities/US_Jacksonville/normGeoJsons.zip: normGJVars.py ./cities/US_Jacksonville/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Jacksonville/geojsons.zip US
	zip -9j ./cities/US_Jacksonville/normGeoJsons.zip ./cities/US_Jacksonville/*_n.gj
	rm ./cities/US_Jacksonville/*_n.gj
./cities/US_Jacksonville/display.json: ./cities/US_Jacksonville/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Jacksonville/normGeoJsons.zip ./cities/US_Jacksonville/display.json
./cities/US_Jacksonville/basegraph.gp: ./cities/US_Jacksonville/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Jacksonville/normGeoJsons.zip ./cities/US_Jacksonville/basegraph.gp
Jacksonville: ./cities/US_Jacksonville/basegraph.gp ./cities/US_Jacksonville/normGeoJsons.zip ./cities/US_Jacksonville/display.json
./cities/US_Kansas_City/normGeoJsons.zip: normGJVars.py ./cities/US_Kansas_City/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Kansas_City/geojsons.zip US
	zip -9j ./cities/US_Kansas_City/normGeoJsons.zip ./cities/US_Kansas_City/*_n.gj
	rm ./cities/US_Kansas_City/*_n.gj
./cities/US_Kansas_City/display.json: ./cities/US_Kansas_City/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Kansas_City/normGeoJsons.zip ./cities/US_Kansas_City/display.json
./cities/US_Kansas_City/basegraph.gp: ./cities/US_Kansas_City/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Kansas_City/normGeoJsons.zip ./cities/US_Kansas_City/basegraph.gp
Kansas_City: ./cities/US_Kansas_City/basegraph.gp ./cities/US_Kansas_City/normGeoJsons.zip ./cities/US_Kansas_City/display.json
./cities/US_Las_Vegas/normGeoJsons.zip: normGJVars.py ./cities/US_Las_Vegas/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Las_Vegas/geojsons.zip US
	zip -9j ./cities/US_Las_Vegas/normGeoJsons.zip ./cities/US_Las_Vegas/*_n.gj
	rm ./cities/US_Las_Vegas/*_n.gj
./cities/US_Las_Vegas/display.json: ./cities/US_Las_Vegas/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Las_Vegas/normGeoJsons.zip ./cities/US_Las_Vegas/display.json
./cities/US_Las_Vegas/basegraph.gp: ./cities/US_Las_Vegas/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Las_Vegas/normGeoJsons.zip ./cities/US_Las_Vegas/basegraph.gp
Las_Vegas: ./cities/US_Las_Vegas/basegraph.gp ./cities/US_Las_Vegas/normGeoJsons.zip ./cities/US_Las_Vegas/display.json
./cities/US_Miami/normGeoJsons.zip: normGJVars.py ./cities/US_Miami/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Miami/geojsons.zip US
	zip -9j ./cities/US_Miami/normGeoJsons.zip ./cities/US_Miami/*_n.gj
	rm ./cities/US_Miami/*_n.gj
./cities/US_Miami/display.json: ./cities/US_Miami/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Miami/normGeoJsons.zip ./cities/US_Miami/display.json
./cities/US_Miami/basegraph.gp: ./cities/US_Miami/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Miami/normGeoJsons.zip ./cities/US_Miami/basegraph.gp
Miami: ./cities/US_Miami/basegraph.gp ./cities/US_Miami/normGeoJsons.zip ./cities/US_Miami/display.json
./cities/US_Minneapolis/normGeoJsons.zip: normGJVars.py ./cities/US_Minneapolis/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Minneapolis/geojsons.zip US
	zip -9j ./cities/US_Minneapolis/normGeoJsons.zip ./cities/US_Minneapolis/*_n.gj
	rm ./cities/US_Minneapolis/*_n.gj
./cities/US_Minneapolis/display.json: ./cities/US_Minneapolis/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Minneapolis/normGeoJsons.zip ./cities/US_Minneapolis/display.json
./cities/US_Minneapolis/basegraph.gp: ./cities/US_Minneapolis/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Minneapolis/normGeoJsons.zip ./cities/US_Minneapolis/basegraph.gp
Minneapolis: ./cities/US_Minneapolis/basegraph.gp ./cities/US_Minneapolis/normGeoJsons.zip ./cities/US_Minneapolis/display.json
./cities/US_Philadelphia/normGeoJsons.zip: normGJVars.py ./cities/US_Philadelphia/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Philadelphia/geojsons.zip US
	zip -9j ./cities/US_Philadelphia/normGeoJsons.zip ./cities/US_Philadelphia/*_n.gj
	rm ./cities/US_Philadelphia/*_n.gj
./cities/US_Philadelphia/display.json: ./cities/US_Philadelphia/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Philadelphia/normGeoJsons.zip ./cities/US_Philadelphia/display.json
./cities/US_Philadelphia/basegraph.gp: ./cities/US_Philadelphia/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Philadelphia/normGeoJsons.zip ./cities/US_Philadelphia/basegraph.gp
Philadelphia: ./cities/US_Philadelphia/basegraph.gp ./cities/US_Philadelphia/normGeoJsons.zip ./cities/US_Philadelphia/display.json
./cities/US_Phoenix/normGeoJsons.zip: normGJVars.py ./cities/US_Phoenix/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Phoenix/geojsons.zip US
	zip -9j ./cities/US_Phoenix/normGeoJsons.zip ./cities/US_Phoenix/*_n.gj
	rm ./cities/US_Phoenix/*_n.gj
./cities/US_Phoenix/display.json: ./cities/US_Phoenix/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Phoenix/normGeoJsons.zip ./cities/US_Phoenix/display.json
./cities/US_Phoenix/basegraph.gp: ./cities/US_Phoenix/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Phoenix/normGeoJsons.zip ./cities/US_Phoenix/basegraph.gp
Phoenix: ./cities/US_Phoenix/basegraph.gp ./cities/US_Phoenix/normGeoJsons.zip ./cities/US_Phoenix/display.json
./cities/US_Salt_Lake_City/normGeoJsons.zip: normGJVars.py ./cities/US_Salt_Lake_City/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Salt_Lake_City/geojsons.zip US
	zip -9j ./cities/US_Salt_Lake_City/normGeoJsons.zip ./cities/US_Salt_Lake_City/*_n.gj
	rm ./cities/US_Salt_Lake_City/*_n.gj
./cities/US_Salt_Lake_City/display.json: ./cities/US_Salt_Lake_City/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Salt_Lake_City/normGeoJsons.zip ./cities/US_Salt_Lake_City/display.json
./cities/US_Salt_Lake_City/basegraph.gp: ./cities/US_Salt_Lake_City/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Salt_Lake_City/normGeoJsons.zip ./cities/US_Salt_Lake_City/basegraph.gp
Salt_Lake_City: ./cities/US_Salt_Lake_City/basegraph.gp ./cities/US_Salt_Lake_City/normGeoJsons.zip ./cities/US_Salt_Lake_City/display.json
./cities/US_San_Antonio/normGeoJsons.zip: normGJVars.py ./cities/US_San_Antonio/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_San_Antonio/geojsons.zip US
	zip -9j ./cities/US_San_Antonio/normGeoJsons.zip ./cities/US_San_Antonio/*_n.gj
	rm ./cities/US_San_Antonio/*_n.gj
./cities/US_San_Antonio/display.json: ./cities/US_San_Antonio/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_San_Antonio/normGeoJsons.zip ./cities/US_San_Antonio/display.json
./cities/US_San_Antonio/basegraph.gp: ./cities/US_San_Antonio/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_San_Antonio/normGeoJsons.zip ./cities/US_San_Antonio/basegraph.gp
San_Antonio: ./cities/US_San_Antonio/basegraph.gp ./cities/US_San_Antonio/normGeoJsons.zip ./cities/US_San_Antonio/display.json
./cities/US_San_Francisco/normGeoJsons.zip: normGJVars.py ./cities/US_San_Francisco/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_San_Francisco/geojsons.zip US
	zip -9j ./cities/US_San_Francisco/normGeoJsons.zip ./cities/US_San_Francisco/*_n.gj
	rm ./cities/US_San_Francisco/*_n.gj
./cities/US_San_Francisco/display.json: ./cities/US_San_Francisco/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_San_Francisco/normGeoJsons.zip ./cities/US_San_Francisco/display.json
./cities/US_San_Francisco/basegraph.gp: ./cities/US_San_Francisco/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_San_Francisco/normGeoJsons.zip ./cities/US_San_Francisco/basegraph.gp
San_Francisco: ./cities/US_San_Francisco/basegraph.gp ./cities/US_San_Francisco/normGeoJsons.zip ./cities/US_San_Francisco/display.json
./cities/US_Seattle/normGeoJsons.zip: normGJVars.py ./cities/US_Seattle/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Seattle/geojsons.zip US
	zip -9j ./cities/US_Seattle/normGeoJsons.zip ./cities/US_Seattle/*_n.gj
	rm ./cities/US_Seattle/*_n.gj
./cities/US_Seattle/display.json: ./cities/US_Seattle/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Seattle/normGeoJsons.zip ./cities/US_Seattle/display.json
./cities/US_Seattle/basegraph.gp: ./cities/US_Seattle/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Seattle/normGeoJsons.zip ./cities/US_Seattle/basegraph.gp
Seattle: ./cities/US_Seattle/basegraph.gp ./cities/US_Seattle/normGeoJsons.zip ./cities/US_Seattle/display.json
./cities/US_Washington_DC/normGeoJsons.zip: normGJVars.py ./cities/US_Washington_DC/geojsons.zip varConf.py
	python3 normGJVars.py ./cities/US_Washington_DC/geojsons.zip US
	zip -9j ./cities/US_Washington_DC/normGeoJsons.zip ./cities/US_Washington_DC/*_n.gj
	rm ./cities/US_Washington_DC/*_n.gj
./cities/US_Washington_DC/display.json: ./cities/US_Washington_DC/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/US_Washington_DC/normGeoJsons.zip ./cities/US_Washington_DC/display.json
./cities/US_Washington_DC/basegraph.gp: ./cities/US_Washington_DC/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/US_Washington_DC/normGeoJsons.zip ./cities/US_Washington_DC/basegraph.gp
Washington_DC: ./cities/US_Washington_DC/basegraph.gp ./cities/US_Washington_DC/normGeoJsons.zip ./cities/US_Washington_DC/display.json
./cities/SY_Synthetic/normGeoJsons.zip: genSynt.py
	python3 genSynt.py ./cities/SY_Synthetic
	zip -9j ./cities/SY_Synthetic/normGeoJsons.zip ./cities/SY_Synthetic/*_n.gj
	rm ./cities/SY_Synthetic/*_n.gj
./cities/SY_Synthetic/display.json: ./cities/SY_Synthetic/normGeoJsons.zip prepGJs.py
	python3 prepGJs.py ./cities/SY_Synthetic/normGeoJsons.zip ./cities/SY_Synthetic/display.json
./cities/SY_Synthetic/basegraph.gp: ./cities/SY_Synthetic/normGeoJsons.zip genBasegraph.py util.py
	python3 genBasegraph.py ./cities/SY_Synthetic/normGeoJsons.zip ./cities/SY_Synthetic/basegraph.gp
Synthetic: ./cities/SY_Synthetic/basegraph.gp ./cities/SY_Synthetic/normGeoJsons.zip ./cities/SY_Synthetic/display.json
