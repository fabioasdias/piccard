import React, {Component } from 'react';
import './App.css';
import TempEvo from './tempEvo';
import { connect } from 'react-redux';
import {getURL, getData} from './urls';
import MapboxMap from './glmap';
import Upload from './upload';
import Aspects from './aspects';
import Histograms from './histograms';
import { actionCreators, requestClustering } from './reducers';
// import {arrayEQ} from './util';

const mapStateToProps = (state) => ({  
  aspects: state.aspects,  
  aspect_info: state.aspect_info,
  geometry: state.geometry,
  clustering: state.clustering,
  temporal: state.temporal,
  colours: state.colours,
  loading: state.loading,
  aspect_hist: state.aspect_hist,
  path_hist: state.path_hist,
  selectedPaths: state.selectedPaths
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
    this.state={showUploadPanel:false,
                availableAspects:[],
                width: window.innerWidth,
                availableGeometries:[]}

  }
  componentWillMount() {
    window.addEventListener('resize', this.handleWindowSizeChange);
  }
  
  // make sure to remove the listener
  // when the component is not mounted anymore
  componentWillUnmount() {
    window.removeEventListener('resize', this.handleWindowSizeChange);
  }
  
  handleWindowSizeChange = () => {
    this.setState({ width: window.innerWidth });
  };

  render() {
    let retJSX=[];
    let {showUploadPanel,availableGeometries}=this.state;
    let {loading}=this.props;
    if (loading){
      retJSX.push(<div key="loading" className="loading">Loading, please wait...</div>);
    }

    // retJSX.push(<MapboxMap 
    //                 geometries={availableGeometries}
    //                 paintProp={'GISJOIN'}
    //                 cmap={this.props.clustering}
    //                 colours={this.props.colours}
    //                 highlight={this.props.selectedPaths}
    //               />);
    retJSX.push(<TempEvo 
                    data={this.props.temporal}
                    colours={this.props.colours}
                    key='tp'
                  />);
    retJSX.push(<Histograms 
                    aspects={this.props.aspect_info}
                    aspect_hist={this.props.aspect_hist}
                    path_hist={this.props.path_hist}
                    colours={this.props.colours}
                    selectedPaths={this.props.selectedPaths}
                    key='hists'
                  />);

    retJSX.push(<div><button 
                    className="button" 
                    onClick={(e)=>{
                      console.log('upload data click')
                      this.setState({showUploadPanel:true});
                    }}>Upload data</button></div>);
      if (showUploadPanel===true){
        retJSX.push(
            <button onClick={(e)=>{
              this.setState({showUploadPanel:false});
            }}>Hide Advanced</button>
          );  
        retJSX.push(<Aspects 
                      availableGeometries={availableGeometries}
                      key='asp'/>);
        retJSX.push(<Upload 
                      key='upp'
                    />);
      }
    
    let disp='block';
    if (this.state.width<600){
      disp='block'
    }
    return (
        <div key='base' style={{display:disp, width:'95%', height: 'fit-content'}}>    
          {retJSX}
        </div>
    );
  }

  componentDidMount() {    
    let {dispatch}=this.props;
      getData(getURL.AvailableGeometries(), (data)=> {
        dispatch(actionCreators.SelectGeometry(data[0]['name']));
        this.setState({availableGeometries:data});                
      });
      getData(getURL.AvailableAspects(), (data)=> {
        // console.log('aspects received', data);
        this.setState({availableAspects:data});                
        dispatch(requestClustering(data));
      });
  }   
}

export default  connect(mapStateToProps)(App);
