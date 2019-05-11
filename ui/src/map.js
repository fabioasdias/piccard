import React, { Component } from 'react';
import MapboxMap from './glmap';


class Map extends Component {
  render() {
    let {geometries, geometry, cmaps}=this.props;
    if ((geometries!==undefined)&&(geometry!==undefined)&&(cmaps!==undefined)){
      return (
        <MapboxMap 
          geometries={geometries}
          paintProp={'GISJOIN'}
          selected={geometry}
          cmap={cmaps[geometry]}
        />
      );
    }
    else
      return(null);
  }
}
export default Map;