import React from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './glmap.css';
import randomColor from 'randomcolor';


mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pqc243cW9wNDN6NTNxcm1jYW1jajY2NyJ9.2C0deXZ03NJyH2f51ui4Jg';

class GeomControl {
  constructor(geoms,callback){
    this.callbackfcn=callback;
    this.geoms=geoms;
  }
  onAdd(map){
    this.map = map;
    console.log(this.geoms);
    this.container = document.createElement('div');
    // this.container.className = 'geom-control';
    this.container.className = 'mapboxgl-ctrl';
    console.log('cont',this.container)

    var sel = document.createElement("SELECT");
    sel.setAttribute("id", "mySelect");
    sel.onchange=this.callbackfcn;
    // document.body.appendChild(x);

    for (let i=0;i<this.geoms.length;i++){
      var op = document.createElement("option");
      op.setAttribute("value", this.geoms[i].name);
      var text = document.createTextNode(this.geoms[i].name);
      op.appendChild(text);
      sel.appendChild(op)  
    }
    this.container.appendChild(sel)
    // document.getElementById("mySelect").appendChild(z);
  
    // this.container.textContent = 'My custom control';
    this.container.onclick = this.callbackfcn;
    return(this.container);
  }
  onRemove(){
    this.container.parentNode.removeChild(this.container);
    this.map = undefined;
  }
}



let MapboxMap = class MapboxMap extends React.Component {
  map;
  constructor(props){
    super(props);
    this.state={loaded:false, selected:undefined}
  }
  
  componentDidUpdate(props,state) {
    console.log('UPDATE',props, state);

    let {geometries}=this.props;
    let cmaps = this.props.cmap;
    let {selected}=this.state;

    console.log('selected', props, selected, state.selected);
    if ((cmaps!==undefined)&&(geometries!==undefined)&&(geometries.length>0)){
      
      if (this.state.selected===undefined){
        this.setState({selected:geometries[0].name})
      } else {

        if ((cmaps.hasOwnProperty(selected)) && 
            ((this.state.selected===undefined)||
            (this.state.selected!==state.selected))){

            console.log('-selected',props,this.state.selected,state.selected);            

            let cmap=cmaps[selected];
            let ids=Object.keys(cmap);
          
            let cMin = cmap[ids[0]][0];
            let cMax = cmap[ids[0]][0];
            for (let i=0; i<ids.length;i++){
              for (let j=0; j<cmap[ids[i]].length; j++)
              {
                cMin=Math.min(cMin,cmap[ids[i]][j]);
                cMax=Math.max(cMax,cmap[ids[i]][j]);  
              }
            }
            let colours=[];
            for (let i = 0; i<=cMax;i++){
              colours.push(randomColor());
            }
            if (this.state.loaded){
              for (let layer of geometries){
                if (selected===layer.name){
                  if (this.map.getSource('s_'+layer.year)===undefined){
                    console.log('add source',layer.year);
                    this.map.addSource('s_'+layer.year, {
                      type: 'vector',
                      url: 'mapbox://'+layer.url,
                      });  
                  }
                  if (this.map.getLayer('l_'+layer.year)===undefined){
                    console.log('add layer',layer.year);
                    this.map.addLayer({
                      id: 'l_'+layer.year,
                      type: 'fill',
                      source: 's_'+layer.year,
                      "source-layer" : layer.source,
                      'paint':{
                        'fill-opacity': 0.9,
                      }
                    }, 'bridge-motorway-2'); //'country-label-lg');   
                  }
                }
                else{
                  if (this.map.getLayer('l_'+layer.year)!==undefined){
                    this.map.removeLayer('l_'+layer.year);
                  }
                  if (this.map.getSource('s_'+layer.year)!==undefined){
                    this.map.removeSource('s_'+layer.year);
                  }
                }
              }
              this.setFill(colours);  
            }
          }
      
        }      
      }

  }

  componentDidMount() {
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      zoom: 5,
      style: 'mapbox://styles/mapbox/light-v9'
    });

    this.map.on('load', () => {
      this.setState({loaded:true})
      let geomControl = new GeomControl(this.props.geometries,
        (d)=>{
          this.setState({selected:d.target.value});
        }
        );
      this.map.addControl(geomControl);
    });
    this.map.on('moveend',()=>{
      if (this.props.bboxCallback!==undefined){
        this.props.bboxCallback(this.map.getBounds());
      }
    });    
  }

  setFill(colours){
    console.log('set fill')
    let exp=['case',
              [
                'has',
                ['to-string', ['get', this.props.paintProp]],
                ['literal', this.props.cmap[this.state.selected]]
              ],
              ['to-color', 
                ["at", 
                  ['at', 
                    ['var','detail'],
                    ['get',
                      ['to-string', ['get', this.props.paintProp]],
                      ['literal', this.props.cmap[this.state.selected]]
                    ],
                  ],  
                  ['literal', colours]
                ]
              ],
              "rgba(255, 255, 255, 0)"
            ];

    if (colours!==undefined){
      for (let layer of this.props.geometries){
        if (this.map.getLayer('l_'+layer.year)!==undefined){
          this.map.setPaintProperty('l_'+layer.year, 
          'fill-color', 
              ['let', 'detail', 0, exp]
          );
          // This may work or not, but runs out of memory...
          // this.map.setPaintProperty('l_'+layer.year, 
          // 'fill-color', 
          //   ["step",
          //     ["zoom"],
          //     ['let', 'detail', 0, exp],
          //     8, ['let', 'detail', 1, exp],
          //     12, ['let', 'detail', 2, exp],
          //     16, ['let', 'detail', 3, exp]
          //   ]
          // );
        }
      }
    }    
  }


  render() {
    return (
      <div ref={el => this.mapContainer = el} 
        className={(this.props.className!==undefined)?
          this.props.className
          :"absolute top right left bottom"}
      />
    );
  }
}


export default MapboxMap;
