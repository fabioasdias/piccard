import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, selModes } from './reducers';
import './style.css';
import './curConf.css';

const mapStateToProps = (state) => ({
    conf: state.conf,
    dsconf: state.dsconf,
    level: state.level,
    showConfig: state.showConfig,
    simpleColours: state.simpleColours,
    selMode: state.selMode,
    nLevels: state.nLevels
  });

//https://github.com/iconic/open-iconic
class CurConf extends Component {
    render() {
        let {dispatch,simpleColours}=this.props;
        let {conf,nLevels}=this.props;
        // let {dsconf}=this.props;
        let {selMode}=this.props;
        let {showConfig}=this.props;
        let {level}=this.props;
        let tJSX=[];
        tJSX.push(<p key="doc"><a href="doc.html" target="_blank">Documentation</a></p>)
//                         <li key={'k'}>Augmented edges: {dsconf.k}</li>
        
        if (conf!==undefined){
            tJSX.push(
                <div key='vconf' 
                     style={{lineHeight:'1em', textAlign:'left', width:'fit-content',margin:'auto',border:'solid',borderWidth:'thin',borderColor:'lightgray',padding:'10px'}}>
                     <p style={{fontWeight:'bold', width:'fit-content',height:'fit-content',margin:'auto 0',textAlign:'left'}}>Current configuration:</p> 
                     <ul 
                         style={{paddingLeft: '10px', margin:'auto'}}>
                         {conf.map((d)=>{
                             return(<li key={d.var}>{d.var} ({d.w})</li>);//: {d.filter} 
                         })}
                     </ul> 
                 </div>);
         }        
        let onChange= (d)=> {
            dispatch(actionCreators.SetLevel(8-parseInt(d.target.value,10)));
          };
        
        tJSX.push(<div style={{textAlign: 'center',border:'solid',borderWidth:'thin',borderColor:'lightgray',padding:'10px'}} key={'confB'}>
            <button 
                key={'cButton'}
                className="configButton" 
                onClick={(e) => {
                    dispatch(actionCreators.ShowConfig(!showConfig));
                }}> 
                <img src="cog.svg" alt='Configuration' height="24" width="24" style={{verticalAlign:'middle'}}></img>
            </button>
            <div>
                <div key={'simpleCheck'} style={{display:'flex',width:'fit-content',height:'fit-content',margin:'auto'}}>
                    <input name="varEnable"
                            type="checkbox"
                            checked={simpleColours}
                            key={'simpleColours'}
                            onChange={(e)=>{
                                dispatch(actionCreators.SetColourOption(e.target.checked));}} 
                    />
                    <p style={{margin:'auto'}}>
                        Simplified colours
                    </p>
                </div>
                {level!==undefined?<div key='ncslider' 
                    style={{width:'fit-content',margin:"auto",marginLeft:'2px',padding:'5px', textAlign:'center'}}>
                    <p style={{marginTop: '5px', marginBottom: '0'}}>
                        Number of clusters: {nLevels-level}
                    </p>
                    <input 
                        type="range" 
                        className="nCluster" 
                        min={2}
                        max={nLevels}
                        defaultValue={nLevels-level} 
                        onChange={onChange}
                    />
                    </div>:null}                
                </div>
        </div>);
        // console.log(nLevels)

        let selModeChange=(d)=>{
            dispatch(actionCreators.SetSelectionMode(d.target.value));
        }
        tJSX.push(
            <div key={'selectToolbox'} className='selectToolbox'>
                <div>
                    <p  style={{margin:'auto',textAlign:'left'}}>Selection  mode:</p>
                    <div>
                        <select 
                                className="dropboxes" 
                                onChange={selModeChange} >
                                <option 
                                    value={selModes.SET}
                                    key={selModes.SET} 
                                    selected={selMode===selModes.SET}
                                    > 
                                        Set  
                                </option>
                                <option 
                                    value={selModes.ADD}
                                    key={selModes.ADD} 
                                    selected={selMode===selModes.ADD}
                                    > 
                                        Add  
                                </option>
                                <option 
                                    value={selModes.REMOVE}
                                    key={selModes.REMOVE} 
                                    selected={selMode===selModes.REMOVE}
                                    > 
                                        Remove
                                </option>
                        </select>
                    
                        <button 
                                className="runButton" 
                                onClick={(d)=>{
                                    dispatch(actionCreators.ClearTID());
                                    dispatch(actionCreators.SetSelectionMode(selModes.SET));
                                }}
                                > 
                                <img src="x.svg" alt='Clear selection' height="16" width="16" style={{verticalAlign:'middle'}}></img>
                        </button>
                    </div>
                </div>
            </div>
        )
                
       return(<div className="curConf">
                {tJSX}
              </div>);
    }
}   
export default connect(mapStateToProps)(CurConf);
