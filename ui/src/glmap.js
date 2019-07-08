import React from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './glmap.css';
import chroma from 'chroma-js';
import { connect } from 'react-redux';
import {requestClustering } from './reducers';

const mapStateToProps = (state) => ({  
  aspects: state.aspects,  
});


mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pqc243cW9wNDN6NTNxcm1jYW1jajY2NyJ9.2C0deXZ03NJyH2f51ui4Jg';

class GeomControl {
  constructor(geoms,callback){
    this.callbackfcn=callback;
    this.geoms=geoms;
  }
  onAdd(map){
    this.map = map;

    this.container = document.createElement('div');
    // this.container.className = 'geom-control';
    this.container.className = 'mapboxgl-ctrl';


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
    this.state={loaded:false, selected:undefined, bbox:undefined}
  }
  
  componentDidUpdate(props,state) {
    let {geometries}=this.props;
    let cmaps = this.props.cmap;
    let {selected}=this.state;

    if ((cmaps!==undefined)&&(geometries!==undefined)&&(geometries.length>0)){
      
      if (this.state.selected===undefined){
        this.setState({selected:geometries[0].name})
      } else {
        if ((cmaps.hasOwnProperty(selected)) && 
            ((this.state.selected!==state.selected)||
             (props.cmap===undefined)||
             (props.highlight.length!==this.props.highlight.length)||
             (Object.keys(cmaps[selected]).length!==Object.keys(props.cmap[selected]).length)
             )){

            

            let cmap=cmaps[selected];
            let ids=Object.keys(cmap);
          
            let cMin = cmap[ids[0]];
            let cMax = cmap[ids[0]];
            for (let i=0; i<ids.length;i++){
                cMin=Math.min(cMin,cmap[ids[i]]);
                cMax=Math.max(cMax,cmap[ids[i]]);  
            }
            if (this.state.loaded){
              for (let layer of geometries){
                if (selected===layer.name){
                  if (this.map.getSource('s_'+layer.year)===undefined){
                    this.map.addSource('s_'+layer.year, {
                      type: 'vector',
                      url: 'mapbox://'+layer.url,
                      });  
                  }
                  if (this.map.getLayer('l_'+layer.year)===undefined){
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
              if (this.props.highlight.length>0){
                let newColours=this.props.colours.slice().map((c)=>{
                  return(chroma(c).brighten().desaturate(2).hex());
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

  componentDidMount() {
    let {dispatch}=this.props;
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      zoom: 5,
      style: 'mapbox://styles/mapbox/light-v9'
    });

    this.map.on('load', () => {
      this.setState({loaded:true})
      console.log('map loaded')
      let geomControl = new GeomControl(this.props.geometries,
        (d)=>{
          this.setState({selected:d.target.value});
        }
        );
      let updbutton = new UpdateButton((d)=>{
        dispatch(requestClustering(this.props.aspects,this.state.bbox));
      });
      this.map.addControl(geomControl);
      this.map.addControl(updbutton,'top-left');
    });
    this.map.on('moveend',()=>{
      this.setState({bbox:this.map.getBounds()})
    });    
  }

  setFill(colours){
    // let exp=['case',
    //           [
    //             'has',
    //             ['to-string', ['get', this.props.paintProp]],
    //             ['literal', this.props.cmap[this.state.selected]]
    //           ],
    //           ['to-color', 
    //             ["at", 
    //               ['get',
    //                 ['to-string', ['get', this.props.paintProp]],
    //                 ['literal', this.props.cmap[this.state.selected]]
    //               ],
    //               ['literal', colours]
    //             ]
    //           ],
    //           "rgba(255, 255, 255, 0)"
    //         ];
    let exp=[
      "interpolate",
      ["linear"],
      ['get',
        ['to-string', ['get', this.props.paintProp]],
        ['literal', this.props.cmap[this.state.selected]]
      ],
      0, "rgba(33,102,172,0)",
      0.2, "rgb(103,169,207)",
      0.4, "rgb(209,229,240)",
      0.6, "rgb(253,219,199)",
      0.8, "rgb(239,138,98)",
      1, "rgb(178,24,43)"
    ];

    if (colours!==undefined){
      for (let layer of this.props.geometries){
        if (this.map.getLayer('l_'+layer.year)!==undefined){
          this.map.setPaintProperty('l_'+layer.year, 
          'fill-color', exp
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

export default  connect(mapStateToProps)(MapboxMap);

