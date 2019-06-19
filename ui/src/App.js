import React, {Component } from 'react';
import './App.css';
import TempEvo from './tempEvo';
import { connect } from 'react-redux';
import {getURL, getData, sendData} from './urls';
import MapboxMap from './glmap';
import Upload from './upload';
import Aspects from './aspects';
import { actionCreators, requestClustering } from './reducers';
// import {arrayEQ} from './util';

const mapStateToProps = (state) => ({  
  aspects: state.aspects,  
  geometry: state.geometry,
  clustering: state.clustering,
  temporal: state.temporal
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
    this.state={showLoading:true, 
                showUploadPanel:false,
                availableAspects:[],
                availableGeometries:[]}
  }

  render() {
    let retJSX=[];
    let {showLoading,showUploadPanel,availableGeometries}=this.state;
    
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
                        data={this.props.temporal}
                        key='tp'
                      />
                      {/* <MapboxMap 
                        geometries={availableGeometries}
                        paintProp={'GISJOIN'}
                        cmap={this.props.clustering}
                        detail={(this.props.aspects.length===1)?1:0}
                      /> */}
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
      getData(getURL.AvailableAspects(), (data)=> {
        // console.log('aspects received', data);
        this.setState({availableAspects:data});                
        dispatch(requestClustering(data));
      });
    this.setState({showLoading:false})
  }   
}

export default  connect(mapStateToProps)(App);
