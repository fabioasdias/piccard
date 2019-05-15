import React, { Component } from 'react';
import MapboxMap from './glmap';
import {arrayEQ} from './util';
import {sendData, getURL} from './urls';

class Map extends Component {

  // updateClustering(aspects){
  //   console.log('getting',this.state.cmap)
  //   sendData(getURL.MapHierarchies(),
  //     {aspects:aspects},
  //     (d)=>{
  //       this.setState({cmap:d,key:this.state.key+1});
  //     });
  // }

  // componentDidUpdate(props){
  //   console.log('did')
  //   if (!arrayEQ(this.props.aspects, props.aspects)){
  //     console.log('did if')
  //     this.setState({cmap:undefined})
  //     this.updateClustering(this.props.aspects)
  //   }
  // }
  // componentDidMount(){
  //   this.updateClustering(this.props.aspects);
  // }
  render() {
    let {geometries, geometry, clustering}=this.props;
    // let {cmap}=this.state;
    if ((geometries!==undefined)&&(geometry!==undefined)){
      console.log(geometry,clustering)
      return (
        <MapboxMap 
          geometries={geometries}
          paintProp={'GISJOIN'}
          selected={geometry}
          cmap={clustering}
          detail={(this.props.aspects.length===1)?1:0}
        />
      );
    }
    else
      return(null);
  }
}
export default Map;