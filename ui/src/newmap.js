import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, toInt} from './reducers';
import {sendData,getURL} from './urls';
import Map from './glmap';


const mapStateToProps = (state) => ({
  tID: state.tID,
  level: state.level,
  curCountryOptions: state.curCountryOptions,
});


class NewMap extends Component {
  constructor(props){
    super(props);
    this.state={cmap:undefined};
  }
  // componentDidMount(){
  //       sendData(getURL.GetAspectComparison(),
  //       {countryID:'US', aspects:['a99afd8c-1170-41cd-82cf-066bb4d0c396',
  //                                 'f1aac678-cd63-433f-9a0d-515275dec1bc']},
  //       (d)=>{
  //       this.setState({cmap:d});
  //   });
  // }
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
          paintProp={'GISJOIN'}
          // className='mainMap'
          // level={level}
          cmap={this.state.cmap}
          // onClick={doHighlight}
          // tids={tID}
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