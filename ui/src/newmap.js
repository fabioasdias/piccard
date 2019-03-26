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
          aspects:[ ['198264d5-307d-499d-9732-f1ff8153f268',],
                    ['1dcb4801-4ef5-4cdc-a15b-4cc4b4c3f0c1',],
                    ['3a619ce0-bd26-440d-afca-c14a3ff842ed',],
                    ['2efeaa77-9fef-4c5b-9a79-3575f624abf1',],
                    ['507c76db-20e5-40d8-8775-e2771393f58e',]
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