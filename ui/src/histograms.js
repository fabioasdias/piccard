import React, {Component} from 'react';
import './histograms.css';
import {XYPlot,HorizontalBarSeries, XAxis, LineSeries} from 'react-vis';

class OnePlot extends Component{
    render(){
        let {dataDetail,dataGlobal,title,colourDetail,colourGlobal}=this.props;
        let delta=0;
        for (let i=0;i<dataDetail.length;i++){
            delta=delta+Math.abs(dataDetail[i]-dataGlobal[i]);
        }
        console.log(delta,dataDetail,dataGlobal);
        return(
            <div className="onePlot">
                <p style={{margin:'auto', width:'fit-content'}}>{title}</p>
                <XYPlot
                    width={400}
                    height={400}
                    xDomain={[0,1]}
                    >
                    <XAxis
                        tickFormat={(v)=>{return((100*v).toFixed(0)+'%');}}
                    />
                    <HorizontalBarSeries
                        colorType="literal"
                        data={dataDetail.map((v,i)=>{
                            return({x:v,y:i,color:colourDetail})
                        })}
                    />
                    <LineSeries
                        colorType="literal"
                        curve={'curveBasis'}
                        data={dataGlobal.map((v,i)=>{
                            return({x:v,y:i, color:colourGlobal})
                        })}
                    />

                </XYPlot>
                
            </div>
        )
    }
}

class Histograms extends Component {
    constructor(props){
        super(props);
        this.state={ext:{}}
    }
    render(){
        console.log('hist render',this.props,this.state);
        let retJSX=[];
        let {aspect_hist, path_hist, aspects, colours, selectedPaths}=this.props;
        let ExtendedCallback=(e)=>{
            let a=e.target.getAttribute('data-aspect');
            let newVal=this.state.ext.hasOwnProperty(a)?!this.state.ext[a]:true;
            let newExt=Object.assign({},this.state.ext);
            newExt[a]=newVal;
            this.setState({ext:newExt});
        }

        if ((aspect_hist!==undefined)&&(path_hist!==undefined)&&(aspects!==undefined)&&(colours!==undefined)){
            //TODO match tempEvo's order
            aspects=aspects.sort((a,b)=>{
                return(a.order-b.order);
            });
            console.log(aspects)
            for (let i=0;i<aspects.length;i++){
                let aspJSX=[];
                let a=aspects[i].id;
                let AspectExtended=(this.state.ext.hasOwnProperty(a)&&(this.state.ext[a]));
                if (AspectExtended){
                    for (let j=0;j<aspect_hist[a].length;j++){
                        aspJSX.push(<OnePlot
                                        title={aspects[i].descr[aspects[i].cols[j]]}
                                        dataDetail={(selectedPaths.length>0)?path_hist[a][selectedPaths[0]][j]:aspect_hist[a][j]} //TODO show all paths
                                        colourDetail={(selectedPaths.length>0)?colours[selectedPaths[0]]:'darkblue'} //TODO show all paths
                                        dataGlobal={aspect_hist[a][j]}
                                        colourGlobal={'darkblue'}
                                    />)   
                    }
                }
                
                retJSX.push(<div className="oneAspect">
                    <div style={{display:'block'}}>
                        <p style={{margin:'auto', width:'fit-content'}}>{aspects[i].name}</p>
                        <img 
                            src={AspectExtended?'chevron-top.svg':'chevron-bottom.svg'}
                            title={AspectExtended?"Collapse":"Expand"}
                            alt={AspectExtended?"Collapse":"Expand"}
                            height="18" 
                            width="18" 
                            data-aspect={aspects[i].id}                            
                            onClick={ExtendedCallback}                            
                            style={{paddingLeft: '2px', paddingTop:'2px', verticalAlign:'middle',cursor:'pointer'}}>                            
                        </img>
                    </div>                        
                    {aspJSX}
                </div>)
            }

        }
        return(
            <div className="histograms">
                <div style={{display:'block'}}>
                    {/* {(selectedPaths.length>0)?<div style={{minWidth:'100px',width:'80%',height:'20px',backgroundColor:colours[selectedPaths[0]]}}></div>:null}                         */}
                    {retJSX}
                </div>
            </div>
        )
    }
}
export default Histograms;