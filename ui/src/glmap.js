import React from 'react'
import PropTypes from 'prop-types'
import mapboxgl from 'mapbox-gl'
import bbox from '@turf/bbox';
import 'mapbox-gl/dist/mapbox-gl.css'
import './glmap.css'

mapboxgl.accessToken = 'pk.eyJ1IjoiZGlhc2YiLCJhIjoiY2pqc243cW9wNDN6NTNxcm1jYW1jajY2NyJ9.2C0deXZ03NJyH2f51ui4Jg';


let Map = class Map extends React.Component {
  map;
    

  static propTypes = {
    data: PropTypes.object.isRequired,
  };

  componentDidUpdate() {
    this.setFill();
  }

  componentWillUpdate(nextProps, nextState) {
    let bounds;
    if ((this.moving!==undefined)&&(this.moving)){
      return;
    }
    // console.log(this.props.tids,nextProps.tids);
    let arrayEQ=(a,b)=>{
      if ((a===undefined)&&(b===undefined)){
        return(true);
      }
      if ((a===undefined)||(b===undefined)){
        return(false);
      }
      if (a.length!==b.length){
        return(false)
      }
      for (let aa of a){
        if (!b.includes(aa)){
          return(false);
        }
      }
      return(true);
    }
    // console.log(this.props.tids,nextProps.tids,arrayEQ(this.props.tids,nextProps.tids));
    if (!arrayEQ(this.props.tids,nextProps.tids)){
      if ((nextProps.tids!==undefined)&&(nextProps.tids.length>0)){
        let nextTids={};
        let tempGJ={type:'FeatureCollection',features:[]}
        
        for (let i=0;i<nextProps.tids.length;i++){
          nextTids[nextProps.tids[i]]=0;
        } 
        for (let feat of nextProps.data.features){
          if (nextTids.hasOwnProperty(feat.properties.tID)){
            tempGJ.features.push(feat);
          }
        }
        bounds=bbox(tempGJ);
        this.map.fitBounds([[bounds[0],bounds[1]],
                            [bounds[2],bounds[3]]]);         
        this.moving=true;
      }else{
        if (nextProps.tids.length===0){
          bounds=bbox(this.props.data);
          this.map.fitBounds([[bounds[0],bounds[1]],
                              [bounds[2],bounds[3]]]);         
          this.moving=true;
        }
      }  
      if (nextProps.boundsCallback!==undefined){
        nextProps.boundsCallback(undefined);
      }
    }  
    else{
        if (nextProps.bbox!==undefined){
          this.map.fitBounds(nextProps.bbox);
          this.moving=true;
        }  
      }

    if (this.props.level!==nextProps.level){
      if (nextState!==null){
        const { map} = nextState;
        if (map) {
          map.getSource('gj').setData(nextProps.data);
          if (nextProps.onClick!==undefined){
            map.on('click', 'gjlayer', nextProps.onClick);
            map.on('click', 'faded', nextProps.onClick);
          }  
        }  
      }  
    }
  }


  componentDidMount() {

    let bounds;
    if (this.props.bbox===undefined){
      bounds=bbox(this.props.data);
      bounds=[[bounds[0],bounds[1]],
              [bounds[2],bounds[3]]];         
    }
    else{
      bounds=this.props.bbox;
    }

    

    this.map = new mapboxgl.Map({
      container: this.mapContainer,
      style: 'mapbox://styles/mapbox/light-v9',
    });

    let BoundsChange=(d)=>{
        if (d.originalEvent!==undefined){
          if (this.props.boundsCallback!==undefined){
            this.props.boundsCallback(this.map.getBounds());
          }
      }
    }

    this.map.on('dragend',BoundsChange);
    this.map.on('zoomend',BoundsChange);    
    this.map.on('movestart',()=>{this.moving=true;});
    this.map.on('moveend',()=>{this.moving=false;});
    // this.map.on('moveend',BoundsChange);    

    this.map.on('load', () => {
      this.map.addSource('gj', {
        type: 'geojson',
        data: this.props.data,
      });

      this.map.addLayer({
        id: 'gjlayer',
        type: 'fill',
        source: 'gj',
        paint: {'fill-opacity':0.8},
        filter: ["!=", "tID", -1]
      }, 'country-label-lg'); 

      this.map.addLayer({
        id: 'faded',
        type: 'fill',
        source: 'gj',
        paint: {'fill-opacity':0.3, 
                'fill-outline-color':'rgba(0,0,0,0)'},
        filter: ["==", "tID", -1]
      }, 'country-label-lg');


      if (this.props.onClick!==undefined){
        this.map.on('click', 'gjlayer', this.props.onClick);
        this.map.on('click', 'faded', this.props.onClick);
      }

      this.map.on('mouseenter', 'gjlayer', ()=> {
        this.map.getCanvas().style.cursor = 'pointer';
      });
      this.map.on('mouseleave', 'gjlayer', ()=> {
          this.map.getCanvas().style.cursor = '';
      });
      this.map.on('mouseenter', 'faded', ()=> {
        this.map.getCanvas().style.cursor = 'pointer';
      });
      this.map.on('mouseleave', 'faded', ()=> {
          this.map.getCanvas().style.cursor = '';
      });
      this.map.on('mouseover', 'gjlayer', ()=> {
        this.map.getCanvas().style.cursor = 'pointer';
      });

      this.setFill();

      this.map.fitBounds(bounds)
      this.setState({'map':this.map});
    });
  }

  setFill() {
    this.map.setPaintProperty('gjlayer', 'fill-color', ['get', this.props.paintProp]);    
    this.map.setPaintProperty('faded', 'fill-color', ['get', this.props.paintProp]);   
    let tids={};
    for (let i=0;i<this.props.tids.length;i++){
      tids[this.props.tids[i]]=0;
    }

    
    if (this.props.tids.length>0){
      this.map.setFilter('faded',['!', ["has", ["to-string", ['get', "tID"]], ['literal', tids]]]);
      this.map.setFilter('gjlayer',["has", ["to-string", ['get', "tID"]], ['literal', tids]]);
    } else {
      this.map.setFilter('faded',["==", "tID", -1]);
      this.map.setFilter('gjlayer',["!=", "tID", -1]);    
    }
}

  render() {
    return (
      <div ref={el => this.mapContainer = el} 
      className={(this.props.className!==undefined)?this.props.className:"absolute top right left bottom"}/>
    );
  }
}


export default Map;
