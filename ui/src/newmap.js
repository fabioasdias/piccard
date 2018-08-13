import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, toInt} from './reducers';
import Map from './glmap';


const mapStateToProps = (state) => ({
  gj: state.gj,
  tID: state.tID,
  level: state.level,
  simpleColours: state.simpleColours,
});


class NewMap extends Component {
  render() {
    let {level,tID,simpleColours}=this.props;
    let {dispatch}=this.props;
    let {gj}=this.props;


    let doHighlight = (d) => {
      let dtid=toInt(d.features["0"].properties.tID);
      dispatch(actionCreators.SetTID(dtid));
    }

    

    if (gj!==undefined){
      return (
        <Map 
          data={gj}
          className='mainMap'
          level={level}
          paintProp={simpleColours?'simplified':'colour'}
          onClick={doHighlight}
          tids={tID}
        />
        //   <Control
        //     position="bottomleft">
        //     <div key='clearSels'>            
        //      <button 
        //         key={'clearBtn'}
        //         disabled={!(((selClassYear!==undefined)&&(selClassYear.length>0))||(selTID>=0))}
        //         onClick={(e) => {
        //             dispatch(actionCreators.SelectClassYear(undefined));
        //             dispatch(actionCreators.SetHighlightChain(-1));
        //         }}>                 
        //         Clear selection
        //      </button>
        //     </div>
        //   </Control>
      );
    }
    else
      return(null);
  }
}
export default connect(mapStateToProps)(NewMap);