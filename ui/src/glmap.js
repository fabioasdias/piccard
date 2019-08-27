import React from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './glmap.css';
import chroma from 'chroma-js';
import { connect } from 'react-redux';
import {requestClustering, requestData } from './reducers';


const mapStateToProps = (state) => ({  
  aspects: state.aspects,  
});


mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pqc243cW9wNDN6NTNxcm1jYW1jajY2NyJ9.2C0deXZ03NJyH2f51ui4Jg';

class GeomControl {
  constructor(clustering, callback){
    this.callbackfcn=callback;
    this.options=[];
    let years=Object.keys(clustering);
    for (let iy=0;iy<years.length;iy++){
      let curGeoms=Object.keys(clustering[years[iy]]);
      for (let ig=0;ig<curGeoms.length;ig++){
        this.options.push({id:this.options.length,name:years[iy]+'-'+curGeoms[ig],year:years[iy],geom:curGeoms[ig]});
      }
    }

  }
  onAdd(map){
    this.map = map;

    this.container = document.createElement('div');
    this.container.className = 'mapboxgl-ctrl';


    var sel = document.createElement("SELECT");
    sel.setAttribute("id", "mySelect");
    sel.onchange=this.callbackfcn;
    // document.body.appendChild(x);

    for (let i=0;i<this.options.length;i++){
      var op = document.createElement("option");
      op.setAttribute("value", this.options[i].id);
      var text = document.createTextNode(this.options[i].name);
      op.appendChild(text);
      sel.appendChild(op);  
    }
    this.container.appendChild(sel);
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

class UpdateButton {
  constructor(cb){
    this.cb=cb;
  }
  onAdd(map){
    // Update
    this.map = map;

    this.container = document.createElement('div');
    // this.container.className = 'geom-control';
    this.container.className = 'mapboxgl-ctrl';


    var btn = document.createElement("BUTTON");
    btn.setAttribute("id", "myButton");
    btn.innerHTML="Update";
    btn.onclick=this.cb;
    this.container.appendChild(btn)
    this.container.onclick = this.cb;
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
    this.state={loaded:false, selected:undefined, bbox:undefined};
  }
  
  componentDidUpdate(props,state) {
    let {geometries}=this.props;
    let cmaps = this.props.cmap;
    let {selected}=this.state;
    let {dispatch}=this.props;
    
    if ((cmaps!==undefined)&&(geometries!==undefined)&&(geometries.length>0)){
      if (this.menu!==undefined){
        this.map.removeControl(this.menu);
      }
      let ygControl = new GeomControl(cmaps, //this.props.geometries,
          (d)=>{
            this.setState({selected:{year:this.menu.options[d.target.value].year, geom:this.menu.options[d.target.value].geom}});
          }
        );
      this.menu=ygControl;
      this.map.addControl(ygControl);    
      

      
      if (selected===undefined){
        this.setState({selected:{year:this.menu.options[0].year, geom:this.menu.options[0].geom}});
      } else {
        console.log((cmaps[selected.year]).hasOwnProperty(selected.geom));
        if ((cmaps.hasOwnProperty(selected.year)) && ((cmaps[selected.year]).hasOwnProperty(selected.geom))){

          if (
              (state.selected===undefined)||
              (selected.year!==state.selected.year)||
              (selected.geom!==state.selected.geom)||
              (props.cmap===undefined)||
              (props.highlight.length!==this.props.highlight.length)||
              (Object.keys(cmaps[selected.year][selected.geom]).length!==Object.keys(props.cmap[selected.year][selected.geom]).length)
            ){

        
            let cmap=cmaps[selected.year][selected.geom];
            let ids=Object.keys(cmap);
          
            let cMin = cmap[ids[0]];
            let cMax = cmap[ids[0]];
            for (let i=0; i<ids.length;i++){
                cMin=Math.min(cMin,cmap[ids[i]]);
                cMax=Math.max(cMax,cmap[ids[i]]);  
            }
            if (this.state.loaded){
              for (let layer of geometries){
                if (selected.geom===layer.name){
                  if (this.map.getSource('s_'+layer.name)===undefined){
                    this.map.addSource('s_'+layer.name, {
                      type: 'vector',
                      url: 'mapbox://'+layer.url,
                      });  
                  }
                  if (this.map.getLayer('l_'+layer.name)===undefined){
                    this.map.addLayer({
                      id: 'l_'+layer.name,
                      type: 'fill',
                      source: 's_'+layer.name,
                      "source-layer" : layer.source,
                      'paint':{
                        'fill-opacity': 0.9,
                      }
                    }, 'bridge-motorway-2'); //'country-label-lg');   
                    this.map.on('click','l_'+layer.name,(d)=>{
                      dispatch(requestData(this.props.aspects, d.features[0].sourceLayer,d.features[0].properties));
                      console.log('mapclick',this.props.aspects, d.features[0].sourceLayer,d.features[0].properties);
                    });
                  }
                }
                else{
                  if (this.map.getLayer('l_'+layer.name)!==undefined){
                    this.map.removeLayer('l_'+layer.name);
                  }
                  if (this.map.getSource('s_'+layer.name)!==undefined){
                    this.map.removeSource('s_'+layer.name);
                  }
                }
              }
              if (this.props.highlight.length>0){
                let newColours=this.props.colours.slice().map((c)=>{
                  return(chroma(c).brighten(2).desaturate(2).hex());
                });
                //copies back the normal colours for the selected
                for (let i=0; i< this.props.highlight.length;i++){
                  newColours[this.props.highlight[i]]=this.props.colours[this.props.highlight[i]];
                }
                this.setFill(newColours);  

              }else{
                this.setFill(this.props.colours);  
              }
              
            }

            }
          }      
        }      
      }

  }

  componentDidMount() {
    let {dispatch}=this.props;
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      zoom: 5,
      style: 'mapbox://styles/mapbox/light-v9'
    });

    this.map.on('load', () => {
      this.setState({loaded:true});
      console.log('map loaded');
      let updbutton = new UpdateButton((d)=>{
        dispatch(requestClustering(this.props.aspects,this.state.bbox));
      });
      this.map.addControl(updbutton,'top-left');
    });
    this.map.on('moveend',()=>{
      this.setState({bbox:this.map.getBounds()})
    });    
  }

  setFill(colours){
    let exp=['case',
              [
                'has',
                ['to-string', ['get', this.props.paintProp]],
                ['literal', this.props.cmap[this.state.selected.year][this.state.selected.geom]]
              ],
              ['to-color', 
                ["at", 
                  ['get',
                    ['to-string', ['get', this.props.paintProp]],
                    ['literal', this.props.cmap[this.state.selected.year][this.state.selected.geom]]
                  ],
                  ['literal', colours]
                ]
              ],
              "rgba(255, 255, 255, 0)"
            ];
    // let exp=[
    //   "interpolate",
    //   ["linear"],
    //   ['get',
    //     ['to-string', ['get', this.props.paintProp]],
    //     ['literal', this.props.cmap[this.state.selected]]
    //   ],
    //   0, "rgba(33,102,172,0)",
    //   0.2, "rgb(103,169,207)",
    //   0.4, "rgb(209,229,240)",
    //   0.6, "rgb(253,219,199)",
    //   0.8, "rgb(239,138,98)",
    //   1, "rgb(178,24,43)"
    // ];

    if (colours!==undefined){
      for (let layer of this.props.geometries){
        if (this.map.getLayer('l_'+layer.name)!==undefined){
          this.map.setPaintProperty('l_'+layer.name, 
          'fill-color', exp
          );
          // This may work or not, but runs out of memory...
          // this.map.setPaintProperty('l_'+layer.name, 
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

export default  connect(mapStateToProps)(MapboxMap);

