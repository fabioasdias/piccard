import React from 'react';
// import PropTypes from 'prop-types'

import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css';
import './glmap.css'


mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pzbmNqd2c3MGIxZDQ0bjVpa2RsZXU1YSJ9.udvxholRALOFEV4ciCh-Lg';


let Map = class Map extends React.Component {
  map;
    

  // static propTypes = {
  //   data: PropTypes.object.isRequired,
  // };

  // componentDidUpdate() {
  //   this.setFill();
  // }

  // componentWillUpdate(nextProps, nextState) {
  //   let bounds;
  //   if ((this.moving!==undefined)&&(this.moving)){
  //     return;
  //   }
  //   let objSameProps=(a1,a2)=>{
  //     let a=Object.keys(a1);
  //     let b=Object.keys(a2);
  //     if ((a===undefined)&&(b===undefined)){
  //       return(true);
  //     }
  //     if ((a===undefined)||(b===undefined)){
  //       return(false);
  //     }
  //     if (a.length!==b.length){
  //       return(false)
  //     }
  //     for (let i=0;i<a.length;i++){
  //       if (!a2.hasOwnProperty(b[i])){
  //         return(false);
  //       }
  //     }
  //     return(true);
  //   }
  //   if (!objSameProps(this.props.nids,nextProps.nids)){
  //     if ((nextProps.nids!==undefined)&&(Object.keys(nextProps.nids).length>0)){
  //       let tempGJ={type:'FeatureCollection',features:[]}
  //       for (let feat of nextProps.data.features){
  //         if (nextProps.nids.hasOwnProperty(feat.properties.nid)){
  //           tempGJ.features.push(feat);
  //         }
  //       }
  //       if (tempGJ.features.length>0){
  //         bounds=bbox(tempGJ);
  //         this.map.fitBounds([[bounds[0],bounds[1]],
  //           [bounds[2],bounds[3]]]);         
  //         this.moving=true;
  //       }
  //     }else{
  //       if (Object.keys(nextProps.nids).length===0){
  //         bounds=bbox(this.props.data);
  //         this.map.fitBounds([[bounds[0],bounds[1]],
  //                             [bounds[2],bounds[3]]]);         
  //         this.moving=true;
  //       }
  //     }  
  //     if (nextProps.boundsCallback!==undefined){
  //       nextProps.boundsCallback(undefined);
  //     }
  //   }  
  //   else{
  //       if (nextProps.bbox!==undefined){
  //         this.map.fitBounds(nextProps.bbox);
  //         this.moving=true;
  //       }  
  //     }

  //   if (this.props.level!==nextProps.level){
  //     if (nextState!==null){
  //       const { map} = nextState;
  //       if (map) {
  //         map.getSource('gj').setData(nextProps.data);
  //         if (nextProps.onClick!==undefined){
  //           map.on('click', 'gjlayer', nextProps.onClick);
  //           map.on('click', 'faded', nextProps.onClick);
  //         }  
  //       }  
  //     }  
  //   }
  // }


  componentDidMount() {
    // let bounds;
    // if (this.props.bbox===undefined){
    //   bounds=bbox(this.props.data);
    //   bounds=[[bounds[0],bounds[1]],
    //           [bounds[2],bounds[3]]];         
    // }
    // else{
    //   bounds=this.props.bbox;
    // }    
    console.log(this.props)
    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      style: 'mapbox://styles/mapbox/light-v9'
    });

    // let BoundsChange=(d)=>{
    //     if (d.originalEvent!==undefined){
    //       if (this.props.boundsCallback!==undefined){
    //         this.props.boundsCallback(this.map.getBounds());
    //       }
    //   }
    // }

    // this.map.on('dragend',BoundsChange);
    // this.map.on('zoomend',BoundsChange);    
    // this.map.on('movestart',()=>{this.moving=true;});
    // this.map.on('moveend',()=>{this.moving=false;});

    this.map.on('load', () => {
      for (let layer of this.props.geometries){
        console.log(layer,'adding source',layer.year);
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
          paint:{'fill-color':'blue'},
        }, 'country-label-lg'); 

      }

      // this.map.addLayer({
      //   id: 'faded',
      //   type: 'fill',
      //   source: 'gj',
      //   paint: {'fill-opacity':0.3, 
      //           'fill-outline-color':'rgba(0,0,0,0)'},
      //   filter: ["==", "tID", -1]
      // }, 'country-label-lg');


      // if (this.props.onClick!==undefined){
      //   this.map.on('click', 'gjlayer', this.props.onClick);
      //   this.map.on('click', 'faded', this.props.onClick);
      // }

      // this.map.on('mouseenter', 'gjlayer', ()=> {
      //   this.map.getCanvas().style.cursor = 'pointer';
      // });
      // this.map.on('mouseleave', 'gjlayer', ()=> {
      //     this.map.getCanvas().style.cursor = '';
      // });
      // this.map.on('mouseenter', 'faded', ()=> {
      //   this.map.getCanvas().style.cursor = 'pointer';
      // });
      // this.map.on('mouseleave', 'faded', ()=> {
      //     this.map.getCanvas().style.cursor = '';
      // });
      // this.map.on('mouseover', 'gjlayer', ()=> {
      //   this.map.getCanvas().style.cursor = 'pointer';
      // });

      // this.setFill();

      // this.map.fitBounds(bounds);
      this.setState({'map':this.map});
    });
  }

  // setFill() {
  //   this.map.setPaintProperty('gjlayer', 'fill-color', ['get', this.props.paintProp]);    
  //   this.map.setPaintProperty('faded', 'fill-color', ['get', this.props.paintProp]);   

  //   if (Object.keys(this.props.nids).length>0){
  //     this.map.setFilter('faded',['!', ["has", ["to-string", ['get', "nid"]], ['literal', this.props.nids]]]);
  //     this.map.setFilter('gjlayer',["has", ["to-string", ['get', "nid"]], ['literal', this.props.nids]]);
  //   } else {
  //     this.map.setFilter('faded',["==", "nid", -1]);
  //     this.map.setFilter('gjlayer',["!=", "nid", -1]);    
  //   }
  // }

  render() {
    return (
      <div ref={el => this.mapContainer = el} 
      className={(this.props.className!==undefined)?this.props.className:"absolute top right left bottom"}/>
    );
  }
}


export default Map;
