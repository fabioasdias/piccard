import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, toInt} from './reducers';
import {sendData,getURL} from './urls';
import MapboxMap from './glmap';


const mapStateToProps = (state) => ({
  tID: state.tID,
  level: state.level,
  curCountryOptions: state.curCountryOptions,
});


class Map extends Component {
  constructor(props){
    super(props);
    this.state={cmap:undefined};
  }
  componentDidMount(){
    sendData(getURL.mapHierarchies(),
      {
          countryID:'US', 
          // aspects:[ ['38502f50-3d9f-409f-aad1-a67b2b58cdfb',],
                    // ['4556dd88-5790-4dc6-9577-b1608ce81995',],
                    // ['1dcb4801-4ef5-4cdc-a15b-4cc4b4c3f0c1',],
                    // ['3a619ce0-bd26-440d-afca-c14a3ff842ed',],
                    // ['2efeaa77-9fef-4c5b-9a79-3575f624abf1',],
                    // ['507c76db-20e5-40d8-8775-e2771393f58e',]
                  // ]
      },
      (d)=>{this.setState({cmap:d["US_CT_1980"]});}
    );
  }
  render() {
    let {dispatch,curCountryOptions}=this.props;
    
    if (curCountryOptions!==undefined){
      console.log(curCountryOptions);
      console.log('-',this.state.cmap)
      return (
        <MapboxMap 
          geometries={curCountryOptions.geometries}
          paintProp={'GISJOIN'}
          cmap={this.state.cmap}
        />
      );
    }
    else
      return(null);
  }
}
export default connect(mapStateToProps)(Map);