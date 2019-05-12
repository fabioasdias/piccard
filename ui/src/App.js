import React, {Component } from 'react';
import './App.css';
import TempEvo from './tempEvo';
import { connect } from 'react-redux';
// import { actionCreators} from './reducers';
import {getURL, getData} from './urls';//sendData
import Map from './map';
import Upload from './upload';
import Aspects from './aspects';
import { actionCreators } from './reducers';

const mapStateToProps = (state) => ({  
  aspects: state.aspects,  
  geometry: state.geometry,
});

// //https://dev.to/gaels/an-alternative-to-handle-global-state-in-react-the-url--3753
// function getParams(location) {
//   const searchParams = new URLSearchParams(location.search);
//   return {
//     country: searchParams.get('country') || '',
//     nc: searchParams.get('nc') || '',
//     cid: searchParams.get('cid') || '',
//   };
// }


class App extends Component {
  constructor(props){
    super(props);
    this.state={showLoading:true, showUploadPanel:false}
  }

  render() {
    let retJSX=[];
    let {showLoading,showUploadPanel,availableGeometries}=this.state;
    let {aspects, geometry}=this.props;
    
    if (showLoading===true){
      retJSX.push(<div key="loading" className="loading">Loading, please wait...</div>);
    }else{
      if (showUploadPanel===true){
        retJSX.push(<div>
            <button onClick={(e)=>{
              this.setState({showUploadPanel:false});
            }}>Hide Advanced</button>
          </div>);  
        retJSX.push(<Aspects 
                      availableGeometries={availableGeometries}
                      key='asp'/>);
        retJSX.push(<Upload 
                      key='upp'
                    />);
      }else{
        retJSX.push(<div key="adv">
          <button onClick={(e)=>{
            this.setState({showUploadPanel:true});
          }}>Upload data</button>
          </div>);  
        retJSX.push(<div style={{display:'flex'}}>
                      <TempEvo 
                        key='tp'
                      />
                      <Map 
                        key='map'
                        geometries={availableGeometries}
                        geometry={geometry}
                        aspects={aspects}
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
    let {dispatch}=this.props;
      getData(getURL.AvailableGeometries(), (data)=> {
        console.log('geometries received', data, data[0]['name']);
        dispatch(actionCreators.SelectGeometry(data[0]['name']));
        this.setState({availableGeometries:data});        
      });
    this.setState({showLoading:false})
  }   
}

export default  connect(mapStateToProps)(App);
