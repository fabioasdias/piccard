import React, {Component } from 'react';
import './App.css';
import TempEvo from './sankey';
import Overview from './overview';
import Detail from './detail';
import { connect } from 'react-redux';
import { actionCreators, getURL, getData, selModes } from './reducers';
import ConfigPanel from './configPanel';
import FileUploadProgress  from 'react-fileupload-progress';
// import NewMap from './newmap';
import TrajDet from './trajectoryDetails';
import CurConf from './curConf';
import Upload from './upload';
// import TransMat from './transMat';

const mapStateToProps = (state) => ({
  showLoading: state.showLoading,
  traj: state.traj
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
  render() {
    let retJSX=[];
    let {showLoading}=this.props;
    retJSX.push(<ConfigPanel key='cop' />);

    if (showLoading===true){
      retJSX.push(<div key="loading" className="loading">Loading, please wait...</div>);
    }else{
      retJSX.push(<Upload key='upp'/>);
      retJSX.push(<CurConf key='cc'/>);
      retJSX.push(<TempEvo key='tp'/>);
      retJSX.push(<Overview key='op'/>);
      // retJSX.push(<TrajDet key='tj'/>);
      retJSX.push(<Detail key='dp'/>);  
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
      dispatch(actionCreators.ShowLoading(true));
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
        dispatch(actionCreators.ShowLoading(false));
      // });
    }

    getData(getURL.CountryOptions(), function(data) {
      console.log(data);
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
