import React from 'react';
// import PropTypes from 'prop-types'

import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './glmap.css';
import randomColor from 'randomcolor';


mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pzbmNqd2c3MGIxZDQ0bjVpa2RsZXU1YSJ9.udvxholRALOFEV4ciCh-Lg';


let MapboxMap = class MapboxMap extends React.Component {
  map;
  constructor(props){
    super(props);
    this.state={loaded:false}
  }
  
  componentDidUpdate(props) {
    let {geometries,selected}=this.props;
    let cmaps = this.props.cmap;
    if ((cmaps!==undefined)&&(cmaps.hasOwnProperty(selected))){
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
              console.log('removing',layer.year);
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

  componentDidMount() {
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      zoom: 5,
      style: 'mapbox://styles/mapbox/light-v9'
    });

    this.map.on('load', () => {
      this.setState({loaded:true})
    });
  }

  setFill(colours){
    console.log('set fill')
    let exp=['case',
              [
                'has',
                ['to-string', ['get', this.props.paintProp]],
                ['literal', this.props.cmap[this.props.selected]]
              ],
              ['to-color', 
                ["at", 
                  ['at', 
                    ['var','detail'],
                    ['get',
                      ['to-string', ['get', this.props.paintProp]],
                      ['literal', this.props.cmap[this.props.selected]]
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
          console.log('detail level',this.props.detail);
          this.map.setPaintProperty('l_'+layer.year, 
          'fill-color', 
              ['let', 'detail', this.props.detail, exp]
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
