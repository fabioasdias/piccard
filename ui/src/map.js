import React, { Component } from 'react';
import MapboxMap from './glmap';
import {arrayEQ} from './util';
import {sendData, getURL} from './urls';

class Map extends Component {
  constructor(props){
    super(props)
    this.state={cmap:undefined}
  }

  updateClustering(aspects){
    console.log('calling update clustering', aspects)
    sendData(getURL.MapHierarchies(),
      {aspects:aspects},
      (d)=>{
        console.log('clustering',d);
        this.setState({cmap:d});
      });
  }

  componentDidUpdate(props){
    console.log('did update',this.props.aspects, props.aspects)
    if (!arrayEQ(this.props.aspects, props.aspects)){
      console.log('really update')
      this.updateClustering(this.props.aspects)
    }
  }
  componentDidMount(){
    console.log('mount')
    this.updateClustering(this.props.aspects);
  }
  render() {
    let {geometries, geometry}=this.props;
    let {cmap}=this.state;
    console.log('state',this.state)
    if ((geometries!==undefined)&&(geometry!==undefined)&&(cmap!==undefined)&&(cmap.hasOwnProperty(geometry))){
      console.log(geometries,geometry,cmap)
      return (
        <MapboxMap 
          geometries={geometries}
          paintProp={'GISJOIN'}
          selected={geometry}
          cmap={cmap[geometry]}
          detail={(this.props.aspects.length===1)?1:0}
        />
      );
    }
    else
      return(null);
  }
}
export default Map;