import React, {Component } from 'react';
import './App.css';
import TempEvo from './sankey';
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
        // retJSX.push(<CurConf key='cc'/>);
        retJSX.push(<Map key='map'/>);
        // retJSX.push(<TempEvo key='tp'/>);
        // retJSX.push(<Overview key='op'/>);
        // retJSX.push(<TrajDet key='tj'/>);
        // retJSX.push(<Detail key='dp'/>);    
      }
    }
    return (
        <div key='base' className="App">    
          {retJSX}
        </div>
    );
  }


  componentDidMount = () => {    
    let {dispatch}=this.props;
    let fromCIDtoTID=(C)=>{
      let {traj}=this.props;
        let tids=[];
            for (let i=0;i<traj.length;i++){
                for (let j=0;j<traj[i].chain.length;j++){
                    if (traj[i].chain[j]===C){
                        tids.push(traj[i].tid);
                        break
                    }
                }
            }
        dispatch(actionCreators.SetTID(tids));
    };

    let doCountry=(country_id, nc, cluster_IDs)=>{
      this.setState({showLoading:true});
      // dispatch(actionCreators.ShowLoading(true));
      console.log("doing country ",country_id," nc ",nc, 'cid',cluster_IDs);
      dispatch(actionCreators.SetCountry(country_id));
      // getData(getURL.GeoJSON(country_id),(gj)=>{
      //   dispatch(actionCreators.SetGeoJson(gj));
      // });


      // getData(getURL.Segmentation(country_id),function(data) {    
      //   // console.log(data);
      //     dispatch(actionCreators.UpdateMap(data));                                
      //     if (data.levelCorr.length>=nc){
      //       dispatch(actionCreators.SetLevel(data.levelCorr.length-nc));      
      //     }
      //     else{
      //       dispatch(actionCreators.SetLevel(data.levelCorr.length-2));          
      //     }
      //   dispatch(actionCreators.SetSelectionMode(selModes.ADD));
      //   for (let i=0;i<cluster_IDs.length;i++){
      //     fromCIDtoTID(cluster_IDs[i]);
      //   }
      //   dispatch(actionCreators.SetSelectionMode(selModes.SET));
        // dispatch(actionCreators.ShowLoading(false));
      this.setState({showLoading:false})
      // });
    }

    getData(getURL.CountryOptions(), function(data) {
      console.log('country options received', data);
      dispatch(actionCreators.SetCountryOptions(data))
      let params=getParams(window.location);
      let country=0; //default country and number of clusters
      let nc=5;
      let cids='';
      if (params.country!==''){
        for(let i=0;i<data.length;i++){
          if (data[i].name===params.country){
            country=data[i].id;
          }
        }
      }
      if (params.nc!==''){
        nc=parseInt(params.nc,10);
      }
      if (params.cid!==''){
        if (params.cid.indexOf(',')>-1){
          cids=params.cid.split(',').map((d)=>parseInt(d,10));
        }
        else{
          cids=[parseInt(params.cid,10),];
        }
      }
      doCountry(country,nc,cids);
    });
  }  
}

export default  connect(mapStateToProps)(App);
