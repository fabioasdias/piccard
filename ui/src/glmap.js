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

    // let colObj = {};
    // for (let i=1; i< ids.length;i++){
    //   colObj[ids[i]]=colours[props.cmap[ids[i]][index]];
    // }
    console.log('min',cMin,'max',cMax);
    this.setState({colours: colours});
  }

  componentDidMount() {
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      zoom: 5,
      style: 'mapbox://styles/mapbox/light-v9'
    });


    this.map.on('load', () => {
      for (let layer of this.props.geometries){
        // console.log(layer,'adding source',layer.year);
        this.map.addSource('s_'+layer.year, {
          type: 'vector',
          url: 'mapbox://'+layer.url,
          });

        this.map.addLayer({
          id: 'l_'+layer.year,
          type: 'fill',
          source: 's_'+layer.year,
          "source-layer" : layer.source,
          'layout': {
            'visibility': layer.visibility
            },
        }, 'country-label-lg'); 
      }

      this.setState({'map':this.map});
      this.setFill();
    });
  }

  setFill(){
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
        if (this.map.getLayoutProperty('l_'+layer.year,"visibility")==='visible'){
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



    // if (this.props.cmap!==undefined){
    //   // console.log(this.props.cmap);
    //   for (let layer of this.props.geometries){
    //     this.map.setPaintProperty('l_'+layer.year, 
    //     'fill-color', [
    //       'case',
    //       [
    //         'has',
    //         ['to-string', ['get', this.props.paintProp]],
    //         [
    //           'literal',
    //           this.props.cmap
    //         ]
    //       ],
    //         ['get',
    //           ['to-string', ['get', this.props.paintProp]],
    //           ['literal', this.state.colours]
    //         ] //G55002500127
    //       ],
    //       'white'
    //     ]);
    //   }  
    // }    


  render() {
    return (
      <div ref={el => this.mapContainer = el} 
      className={(this.props.className!==undefined)?this.props.className:"absolute top right left bottom"}/>
    );
  }
}


export default MapboxMap;
