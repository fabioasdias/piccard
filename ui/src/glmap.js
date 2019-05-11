import React from 'react';
// import PropTypes from 'prop-types'

import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './glmap.css';
import randomColor from 'randomcolor';


mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pzbmNqd2c3MGIxZDQ0bjVpa2RsZXU1YSJ9.udvxholRALOFEV4ciCh-Lg';


let MapboxMap = class MapboxMap extends React.Component {
  map;

  componentDidUpdate() {
    this.setFill();
  }
  componentWillReceiveProps(props){
    let ids=Object.keys(props.cmap);
  
    let cMin = props.cmap[ids[0]][0];
    let cMax = props.cmap[ids[0]][0];
    for (let i=0; i<ids.length;i++){
      for (let j=0; j<props.cmap[ids[i]].length; j++)
      {
        cMin=Math.min(cMin,props.cmap[ids[i]][j]);
        cMax=Math.max(cMax,props.cmap[ids[i]][j]);  
      }
    }
    let colours=[];
    for (let i = 0; i<=cMax;i++){
      colours.push(randomColor());
    }

    for (let layer of this.props.geometries){
      if (props.selected===layer.name){
        console.log('add',layer.year);
        this.map.addSource('s_'+layer.year, {
          type: 'vector',
          url: 'mapbox://'+layer.url,
          });
  
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
      else{
        console.log('else',layer.year);
        if (this.map.getLayer('l_'+layer.year)!==undefined){
          this.map.removeLayer('l_'+layer.year);
        }
        if (this.map.getSource('s_'+layer.year)!==undefined){
          this.map.removeSource('s_'+layer.year);
        }
      }
    }
    this.setFill();
    this.setState({colours: colours});
  }

  componentDidMount() {
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      zoom: 5,
      style: 'mapbox://styles/mapbox/light-v9'
    });

    // this.map.on('load', () => {
    //   this.setFill();
    // });
    this.setState({'map':this.map});    
  }

  setFill(){
    console.log('set fill')
    let exp=['case',
              [
                'has',
                ['to-string', ['get', this.props.paintProp]],
                ['literal', this.props.cmap]
              ],
              ['to-color', 
                ["at", 
                  ['at', 
                    ['var','detail'],
                    ['get',
                      ['to-string', ['get', this.props.paintProp]],
                      ['literal', this.props.cmap]
                    ],
                  ],  
                  ['literal', this.state.colours]
                ]
              ],
              "rgba(255, 255, 255, 0)"
            ];

    if ((this.state!==null)&&(this.state.colours!==undefined)){
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
