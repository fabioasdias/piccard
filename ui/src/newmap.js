import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, toInt} from './reducers';
import Map from './glmap';


const mapStateToProps = (state) => ({
  tID: state.tID,
  level: state.level,
  curCountryOptions: state.curCountryOptions,
});


class NewMap extends Component {
  render() {
    let {level,tID,dispatch,curCountryOptions}=this.props;

    let doHighlight = (d) => {
      let dtid=toInt(d.features["0"].properties.tID);
      dispatch(actionCreators.SetTID(dtid));
    }

    
    if (curCountryOptions!==undefined){
      console.log(curCountryOptions)
      return (
        <Map 
          geometries={curCountryOptions.geometries}
          activeLayer={0}
          // className='mainMap'
          level={level}
          paintProp={'colour'}
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