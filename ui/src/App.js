import React, {Component } from 'react';
import './App.css';
import TempEvo from './sankey'
import Overview from './overview'
import Detail from './detail'
import { connect } from 'react-redux';
import { actionCreators, getURL, getData, selModes } from './reducers';
import ConfigPanel from './configPanel'
import NewMap from './newmap'
import TrajDet from './trajectoryDetails';
import TransMat from './transMat';

const mapStateToProps = (state) => ({
  showLoading: state.showLoading,
  traj: state.traj
});

//https://dev.to/gaels/an-alternative-to-handle-global-state-in-react-the-url--3753
function getParams(location) {
  const searchParams = new URLSearchParams(location.search);
  return {
    city: searchParams.get('city') || '',
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
      retJSX.push(<Overview key='op'/>);
      retJSX.push(<TempEvo key='tp'/>);
      retJSX.push(<TransMat key='tm'/>)
      retJSX.push(<NewMap key='nm'/>);
      retJSX.push(<TrajDet key='tj'/>);
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

    let doCity=(city_id, nc, cluster_IDs)=>{
      console.log("doing city ",city_id," nc ",nc, 'cid',cluster_IDs);
      dispatch(actionCreators.SetCity(city_id));
      getData(getURL.GeoJSON(city_id),(gj)=>{
        dispatch(actionCreators.SetGeoJson(gj));
      });

      dispatch(actionCreators.ShowLoading(true));

      getData(getURL.Segmentation(city_id),function(data) {    
        // console.log(data);
          dispatch(actionCreators.UpdateMap(data));                                
          if (data.levelCorr.length>=nc){
            dispatch(actionCreators.SetLevel(data.levelCorr.length-nc));      
          }
          else{
            dispatch(actionCreators.SetLevel(data.levelCorr.length-2));          
          }
        dispatch(actionCreators.SetSelectionMode(selModes.ADD));
        for (let i=0;i<cluster_IDs.length;i++){
          fromCIDtoTID(cluster_IDs[i]);
        }
        dispatch(actionCreators.SetSelectionMode(selModes.SET));
        dispatch(actionCreators.ShowLoading(false));
      });
    }
    getData(getURL.CityOptions(), function(data) {
      dispatch(actionCreators.SetCityOptions(data))
      let params=getParams(window.location);
      let city=0; //default city and number of clusters
      let nc=5;
      let cids='';
      if (params.city!==''){
        for(let i=0;i<data.length;i++){
          if (data[i].name===params.city){
            city=data[i].id;
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

      doCity(city,nc,cids);
      
    });
  }  
}

export default  connect(mapStateToProps)(App);
