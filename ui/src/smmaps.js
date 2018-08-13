import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators} from './reducers';
import './style.css';
import './trajectoryDetails.css';
import Map from './glmap';


const mapStateToProps = (state) => ({
    level: state.level,
    years: state.years,
    colours: state.colours,
    tID: state.tID,
    gj: state.gj,
    path: state.path,
    population: state.population,
    patt: state.patt,
    traj: state.traj
  });


class SmMaps extends Component {
    constructor(props){
        super(props);
        this.state={bounds:undefined};
    }

    render(){
        let {gj,tID,years,dispatch,level}=this.props;
        let rowJSX=[];
      let RegionClick = (d) =>{
          dispatch(actionCreators.ShowDetails(true));
          dispatch(actionCreators.SetRegion(d.features["0"].properties.display_id))      
        };
      
      for (let y of years){
          if (gj!==undefined){
              if (gj.features.length>0){
                  rowJSX.push(
                    <Map 
                        key={'sm'+y}
                        className={'mapSM'}
                        data={gj}
                        bbox={this.state.bounds}
                        boundsCallback={(bb)=>{this.setState({bounds:bb});}}
                        tids={tID}
                        level={level}
                        paintProp={y.toString()}
                        onClick={RegionClick}
                  />);
              }
              else{
                  rowJSX.push(<div className="mapSM"></div>)
              }
          }             
      }
      return(<div className='mapRow'>{rowJSX}</div>);
    }
    
}

export default connect(mapStateToProps)(SmMaps);

