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
    nids: state.nids,
    gj: state.gj,
    // path: state.path,
    // population: state.population,
    // patt: state.patt,
    // traj: state.traj
  });


class SmMaps extends Component {
    constructor(props){
        super(props);
        this.state={bounds:undefined};
    }

    render(){
        let {gj,nids,years,dispatch,level}=this.props;
        let rowJSX=[];
        let RegionClick = (d) =>{
            console.log('click',d.features["0"].properties);
            // dispatch(actionCreators.ShowDetails(true));
            // dispatch(actionCreators.SetRegion(d.features["0"].properties.display_id))      
        };
        for (let y of years){
            if ((gj!==undefined)&&(gj[y]!==undefined)) {
                if (gj[y].features.length>0){
                    console.log(y,gj[y]);
                    rowJSX.push(
                        <Map 
                            key={'sm'+y}
                            className={'mapSM'}
                            data={gj[y]}
                            bbox={this.state.bounds}
                            boundsCallback={(bb)=>{this.setState({bounds:bb});}}
                            nids={nids}
                            level={level}
                            paintProp={'colour'}
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

