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
    getData(getURL.CityOptions(), function(data) {

      dispatch(actionCreators.SetCityOptions(data))
      dispatch(actionCreators.SetCity(0));
      getData(getURL.GeoJSON(0),(gj)=>{
        dispatch(actionCreators.SetGeoJson(gj));
      });

      dispatch(actionCreators.ShowLoading(true));

      getData(getURL.Segmentation(0),function(data) {    
        // console.log(data);
          dispatch(actionCreators.UpdateMap(data));                                
          if (data.levelCorr.length>5)
              dispatch(actionCreators.SetLevel(data.levelCorr.length-5));      
          else
              dispatch(actionCreators.SetLevel(data.levelCorr.length-2));          
        dispatch(actionCreators.ShowLoading(false));
      });
    });
  }  
}

export default  connect(mapStateToProps)(App);
