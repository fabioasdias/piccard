import React, {Component } from 'react';
import './App.css';
import TempEvo from './tempEvo';
import { connect } from 'react-redux';
import { actionCreators} from './reducers';
import {getURL, getData} from './urls';
import FileUploadProgress  from 'react-fileupload-progress';
import Map from './map';
import Upload from './upload';
import Aspects from './aspects';

const mapStateToProps = (state) => ({
  CountryOptions: state.CountryOptions
});

//https://dev.to/gaels/an-alternative-to-handle-global-state-in-react-the-url--3753
function getParams(location) {
  const searchParams = new URLSearchParams(location.search);
  return {
    country: searchParams.get('country') || '',
    nc: searchParams.get('nc') || '',
    cid: searchParams.get('cid') || '',
  };
}

import {sendData,getURL} from './urls';

class App extends Component {
  constructor(props){
    super(props);
    this.state={showLoading:true,showAdvancedConfig:false}
  }
  render() {
    let retJSX=[];
    let {showLoading,showAdvancedConfig}=this.state;
    
    if (showLoading===true){
      retJSX.push(<div key="loading" className="loading">Loading, please wait...</div>);
    }else{
      if (showAdvancedConfig===true){
        retJSX.push(<div>
            <button onClick={(e)=>{
              this.setState({showAdvancedConfig:false});
            }}>Hide Advanced</button>
          </div>);  
        console.log('pre',this.props.CountryOptions)
        retJSX.push(<Aspects 
                      availableCountries={this.props.CountryOptions}
                      key='asp'/>);
        retJSX.push(<Upload key='upp'/>);
      }else{
        retJSX.push(<div key="adv">
          <button onClick={(e)=>{
            this.setState({showAdvancedConfig:true});
          }}>Show Advanced</button>
          </div>)  
        retJSX.push(<div style={{display:'flex'}}>
                      <TempEvo key='tp'/>
                      <Map 
                        key='map'
                        geometries={CountryOptions.geometries}
                        geometry={'US_CT_2000'}
                        cmap={this.state.clustering}
                      />
                    </div>);
      }
    }
    return (
        <div key='base' className="App">    
          {retJSX}
        </div>
    );
  }


  componentDidMount() {    
      getData(getURL.AvailableGeometries(), function(data) {
        console.log('geometries received', data);
        dispatch(actionCreators.SetAvailableGeometries(data))
      });
      sendData(getURL.mapHierarchies(),
      {
          countryID:'US', 
      },
      (d)=>{
        console.log(d);
        this.setState({clustering:d});
      }
    );
    this.setState({showLoading:false})
  }   
}

export default  connect(mapStateToProps)(App);
