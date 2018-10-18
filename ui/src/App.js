import React, {Component } from 'react';
import './App.css';
import TempEvo from './sankey'
import Overview from './overview'
import Detail from './detail'
import { connect } from 'react-redux';
import { actionCreators, getURL, getData } from './reducers';
import ConfigPanel from './configPanel'
import NewMap from './newmap'
import TrajDet from './trajectoryDetails';
import TransMat from './transMat';

const mapStateToProps = (state) => ({
  showLoading: state.showLoading,

});

//https://dev.to/gaels/an-alternative-to-handle-global-state-in-react-the-url--3753
function getParams(location) {
  const searchParams = new URLSearchParams(location.search);
  return {
    city: searchParams.get('city') || '',
    nc: searchParams.get('nc') || '',
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
    let doCity=(city_id, nc)=>{
      console.log("doing city ",city_id," nc ",nc);
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
        dispatch(actionCreators.ShowLoading(false));
      });
    }
    getData(getURL.CityOptions(), function(data) {
      dispatch(actionCreators.SetCityOptions(data))
      let params=getParams(window.location);
      let city=0; //default city and number of clusters
      let nc=5;
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
      doCity(city,nc);
      
    });
  }  
}

export default  connect(mapStateToProps)(App);
