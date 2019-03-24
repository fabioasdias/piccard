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
  componentDidMount(){
    sendData(getURL.LearnPredictions(),
      {
          countryID:'US', 
          from:['37565672-939c-4f1b-9d97-b5c324d631af', //ed
                '59370c7f-edf6-4911-aa6f-404dd8249e6a'], //marit s
          to: ['450af207-7502-4902-a89d-0359efd2b40e', //ed
              'a4fabb78-aad5-4894-80f1-99ffba6a9d3b'//income
              ]
      },
      (d)=>{this.setState({cmap:d});}
    );
  }
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