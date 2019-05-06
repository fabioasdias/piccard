import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, toInt} from './reducers';
import {sendData,getURL} from './urls';
import Map from './glmap';


const mapStateToProps = (state) => ({
  tID: state.tID,
  level: state.level,
  curCountryOptions: state.curCountryOptions,
});


class NewMap extends Component {
  constructor(props){
    super(props);
    this.state={cmap:undefined};
  }
  componentDidMount(){
    sendData(getURL.mapHierarchies(),
      {
          countryID:'US', 
          aspects:[ ['198264d5-307d-499d-9732-f1ff8153f268',],
                    ['1dcb4801-4ef5-4cdc-a15b-4cc4b4c3f0c1',],
                    // ['3a619ce0-bd26-440d-afca-c14a3ff842ed',],
                    // ['2efeaa77-9fef-4c5b-9a79-3575f624abf1',],
                    // ['507c76db-20e5-40d8-8775-e2771393f58e',]
                  ]
      },
      (d)=>{this.setState({cmap:d["US_CT_1970"]});}
    );
  }
  render() {
    let {dispatch,curCountryOptions}=this.props;
    
    if (curCountryOptions!==undefined){
      console.log(curCountryOptions);
      console.log('-',this.state.cmap)
      return (
        <Map 
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
export default connect(mapStateToProps)(NewMap);