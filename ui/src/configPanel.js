import React, { Component } from 'react';
import { connect } from 'react-redux';
import { actionCreators, getData, getURL, toInt } from './reducers';
import './configPanel.css';

const mapStateToProps = (state) => ({
    cityOptions: state.cityOptions,
    cityID: state.cityID,
    dsconf: state.dsconf,
    showConfig: state.showConfig,
  });

class ConfigPanel extends Component {
    constructor(props){
        super(props);
        this.state= { 
            k: 5,
            nextId: 0,
            conf : undefined,
        };
    }

    render() {
        let {showConfig}=this.props;
        let {cityOptions}=this.props;
        let {dispatch}=this.props;
        let {cityID}=this.props;
        let {dsconf}=this.props;
        let tarray;

        let defaultConf=(variables)=>{
            let conf=[];
            for (let i=0;i<variables.length;i++){
                conf.push({id:i,var:variables[i].id,fs:0,w:1,enabled:true});
            }
            return(conf);
        };

        if ((showConfig===undefined) || (!showConfig) || (cityOptions===undefined)){
            return(null);
        }
        else {
            if (this.state.conf===undefined){
                if (dsconf===undefined){
                    this.setState({nextId:cityOptions[cityID].variables.length,conf:defaultConf(cityOptions[cityID].variables)});
                }else{
                    let cconf=[];
                    for (let i=0;i<dsconf.vars.length;i++){
                        cconf.push({id:i,var:dsconf.vars[i],fs:0,w:dsconf.w[i],enabled:true});
                    }
                    this.setState({nextID:dsconf.vars.length, conf:cconf});
                }                
                return(null);
            }
                
            let retJSX=[]

            retJSX.push(<div key='city' className="oneVar">
                            <div className="aroundDiv" style={{border:'none'}}>Geographic region:</div>
                            <select 
                                className="dropboxes" 
                                onChange={(e)=>{
                                    let curVal=toInt(e.target.value);
                                    if (cityOptions[cityID].kind!==cityOptions[curVal].kind){
                                        this.setState({nextId:cityOptions[curVal].variables.length,conf:defaultConf(cityOptions[curVal].variables)});                                    }
                                    dispatch(actionCreators.SetCity(curVal));
                                }} >
                                {cityOptions.map( (e) => {
                                    return(<option 
                                            value={e.id} 
                                            key={e.id} 
                                            selected={e.id===cityID}
                                            > 
                                                {e.name}  
                                            </option>)
                                })}
                            </select> 
                        </div>);

            // retJSX.push(<div key='ok' className="oneVar" style={{display:'block',width:'300px'}}>
            //                 Content edge augmentation: {this.state.k}
            //                 <div key='k'  style={{ display:'flex', placeContent: 'space-around'}}>
            //                     <div className="aroundDiv">1</div> 
            //                     <input type="range" className="slider" min={1} max={10} defaultValue={this.state.k} onChange={(e)=>{
            //                         this.setState({k:e.target.value});
            //                     }}/>
            //                     <div className="aroundDiv">10</div>
            //                 </div>
            //             </div>);


            let enableChange = (e)=>{
                let k=toInt(e.target.getAttribute('data-k'));
                tarray=this.state.conf.slice();
                tarray[k].enabled=e.target.checked;
                this.setState({conf:tarray.slice()})    
            };
            let varChange = (e) => {
                let k=toInt(e.target.getAttribute('data-k'));
                tarray=this.state.conf.slice();
                tarray[k].var=toInt(e.target.value);    
                this.setState({conf:tarray.slice()})
            };
            // let fChange = (e)=>{
            //     let k=toInt(e.target.getAttribute('data-k'));
            //     tarray=this.state.conf.slice();
            //     tarray[k].fs=toInt(e.target.value);    
            //     this.setState({conf:tarray.slice()});
            // };
            let wChange = (e)=>{
                let k=toInt(e.target.getAttribute('data-k'));
                tarray=this.state.conf.slice();
                tarray[k].w=parseFloat(e.target.value,10);    
                this.setState({conf:tarray.slice()})
            }
            let removeVar=(e)=>{
                let id=toInt(e.target.getAttribute('data-id'));
                tarray=this.state.conf.slice();
                this.setState({conf:tarray.filter(X => (X.id!==id))});
            }

            let varJSX=[];

            for (let k=0;k<this.state.conf.length;k++){
                let tJSX=[];
                let V=this.state.conf[k];
                tJSX.push(<div className="aroundDiv" style={{padding:'5px'}}><input
                            name="varEnable"
                            type="checkbox"
                            checked={V.enabled}
                            key={'cEnable'+k}
                            onChange={enableChange} 
                            data-k={k}
                           /></div>);
                tJSX.push(<div className="aroundDiv"><select 
                            className="dropboxes" 
                            data-k={k}
                            key={'dVar'+k}
                            onChange={varChange} 
                            >
                            {cityOptions[cityID].variables.map( (e) => {
                                return(<option 
                                            value={e.id} 
                                            key={e.id}
                                            selected={e.id===V.var}
                                        > 
                                        {e.name} 
                                        </option>)
                            })}
                        </select></div>);
                // tJSX.push(<div className="aroundDiv">Filter: <select 
                //             className="dropboxes" 
                //             data-k={k}
                //             onChange={fChange}
                //           >
                //             {cityOptions[cityID].filters.map( (e) => {
                //                 return(<option 
                //                           value={e.id} 
                //                           key={e.id}
                //                           selected={e.id===V.filter}
                //                         > 
                //                           {e.name} 
                //                         </option>)
                //             })}
                //         </select></div>);


                tJSX.push(<div className="aroundDiv" key={'w'+k} >Weight: <input 
                            type="text" 
                            className="textWeight" 
                            defaultValue={this.state.conf[k].w}
                            data-k={k}
                            onBlur={wChange}
                          /></div>); 

                tJSX.push(<div className="aroundDiv" style={{padding:'5px'}}><button 
                            className="runButton" 
                            data-id={V.id}
                            disabled={this.state.conf.length>1?false:true}
                            onClick={removeVar}> 
                            <img src="x.svg" alt='Remove' data-id={V.id} height="16" width="16" style={{verticalAlign:'middle'}}></img>
                        </button></div>); 
 
                varJSX.push(<div className="oneVar" key={V.id}>
                            {tJSX}
                            </div>);

            }
            retJSX.push(<div><h3>Data sources</h3>{varJSX}</div>);

            retJSX.push(<div key='footer' className="Footer">
                    <button 
                        className="runButton" 
                        onClick={()=>{
                            tarray=this.state.conf.slice();
                            tarray.push({id : this.state.nextId, var: 0, fs : 0, w  : 1, enabled : true,
                            });
                            this.setState({conf:tarray.slice(),nextId:this.state.nextId+1})
                        }}> 
                        <img src="plus.svg" alt='Add' height="16" width="16" style={{verticalAlign:'middle'}}></img>
                    </button>
                
                    <button className="runButton" onClick={(e) => {
                        let selVars=[];
                        let selFilters=[];
                        let W=[];
                        for (let V of this.state.conf){
                            if (V.enabled){
                                selVars.push(V.var);
                                selFilters.push(V.fs);
                                W.push(V.w);
                            }
                        }
                        if ((selVars.length>0) && (selFilters.length>0) && (W.length >0))
                        {
                            dispatch(actionCreators.ShowConfig(false));       
                            dispatch(actionCreators.SetGeoJson(undefined));
                            

                            getData(getURL.GeoJSON(cityID),(gj)=>{
                                dispatch(actionCreators.SetGeoJson(gj));
                            })
                            dispatch(actionCreators.ShowLoading(true));
                            getData(getURL.Segmentation(cityID, selVars, selFilters, W, this.state.k),function(data) {    
                                // console.log(data);
                                dispatch(actionCreators.UpdateMap(data));                                
                                if (data.levelCorr.length>5)
                                    dispatch(actionCreators.SetLevel(data.levelCorr.length-5));      
                                else
                                    dispatch(actionCreators.SetLevel(data.levelCorr.length-2));
                                dispatch(actionCreators.ShowLoading(false));
                              });
                            }
                        }}>
                        <img src="media-play.svg" alt='Run' height="16" width="16" style={{verticalAlign:'middle'}}></img>
                    </button> 
                </div>);

            return(<div key='configPanel' className="ConfigPanel" onKeyPress={(d)=>{console.log(d)}}>         
                    <div style={{width:'95%',textAlign:'right'}}>
                        <button 
                            className="detButton" 
                            onClick={(e) => {
                                dispatch(actionCreators.ShowConfig(false));
                            }}> 
                            <img src="x.svg" alt='Close panel' height="16" width="16" style={{verticalAlign:'middle'}}></img>
                        </button>
                        <p style={{width:'80%',margin:'0 auto',textAlign:'center',marginTop:'-20px'}}> <h2>Clustering parameters</h2></p>                        
                    </div>        
                    {retJSX}
                   </div>);
        }
    }
}
export default connect(mapStateToProps)(ConfigPanel);
