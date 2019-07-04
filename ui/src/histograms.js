import React, {Component} from 'react';
import './histograms.css';
import {XYPlot,HorizontalBarSeries, XAxis, YAxis,LineSeries} from 'react-vis';

class OnePlot extends Component{
    render(){
        let {dataDetail,dataGlobal,title,colourDetail,colourGlobal}=this.props;
        let doGlobal=true;
        let {minG,maxG,minP,maxP}=this.props.limits;
        
        if (dataDetail===null){
            dataDetail=dataGlobal;
            colourDetail=colourGlobal;
            doGlobal=false;
            minP=minG;
            maxP=maxG;
        }
        let N=dataDetail.length;
        console.log(minP,maxP)
        return(
            <div className="onePlot">
                <p className='titles'>{title}</p>
                <XYPlot
                    width={400}
                    height={400}
                    margin={{left:40,right:20,top:50,bottom:50}}
                    xDomain={[0,1]}
                    >
                    {(doGlobal)?<XAxis
                        orientation={'top'}
                        tickTotal={4}
                        title={'global'}
                        tickFormat={v => `${Math.round((maxG-minG)*v)}`}                            
                        style={{
                            line: {stroke: colourGlobal},
                            text: {stroke: 'none', fill: 'black', fontSize:'10px'}
                        }}                  
                    />:null}
                    <XAxis
                        title={'Number of regions'}
                        tickFormat={v => `${Math.round((maxP-minP)*v)}`}                            
                        style={{
                            text: {stroke: 'none', fill: 'black', fontSize:'10px'}
                        }}                  

                    />
                    <YAxis 
                        // tickLabelAngle={-30} 
                        tickTotal={5}
                        tickFormat={v => `${Math.round(100*(v/N))}%`}
                    />      
                    <HorizontalBarSeries
                        colorType="literal"
                        color={colourDetail}
                        data={dataDetail.map((v,i)=>{
                            return({y:i,x:(v-minP)/(maxP-minP)})
                        })}
                    />
                    {(doGlobal)?<LineSeries
                        colorType="literal"
                        stroke={colourGlobal}
                        curve={'curveBasis'}
                        data={dataGlobal.map((v,i)=>{
                            return({y:i,x:(v-minG)/(maxG-minG)})
                        })}
                    />:null}

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
        let {aspects, colours, selectedPaths}=this.props;

        let ExtendedCallback=(e)=>{
            let a=e.target.getAttribute('data-aspect');
            let newVal=this.state.ext.hasOwnProperty(a)?!this.state.ext[a]:true;
            let newExt=Object.assign({},this.state.ext);
            newExt[a]=newVal;
            this.setState({ext:newExt});
        }

        if ((this.props.data!==undefined)&&(aspects!==undefined)&&(colours!==undefined)){
            let aspect_hist=this.props.data.aspect;
            let path_hist=this.props.data.path;


            //TODO match tempEvo's order
            aspects=aspects.sort((a,b)=>{
                return(a.order-b.order);
            });
            console.log(aspects)
            let curPath=undefined;
            if (selectedPaths.length>0){
                curPath=selectedPaths[0]
            }
            for (let i=0;i<aspects.length;i++){
                let aspJSX=[];
                let a=aspects[i].id;
                let AspectExtended=(this.state.ext.hasOwnProperty(a)&&(this.state.ext[a]));
                if (AspectExtended){
                    let minG=Math.min(...aspect_hist[a][0])
                    let maxG=Math.max(...aspect_hist[a][0])
                    let minP=0;
                    let maxP=0;
                    console.log(minP,maxP,minG,maxG);
                    for (let j=1;j<aspect_hist[a].length;j++){
                        minG=Math.min(minG,...aspect_hist[a][j]);
                        maxG=Math.max(maxG,...aspect_hist[a][j]);
                        if (curPath!==undefined){
                            minP=Math.min(minP,...path_hist[a][curPath][j]);
                            maxP=Math.max(maxP,...path_hist[a][curPath][j]);    
                        }
                    }
                    console.log('+',minP,maxP,minG,maxG);
                    for (let j=0;j<aspect_hist[a].length;j++){
                        aspJSX.push(<OnePlot
                                        title={aspects[i].descr[aspects[i].cols[j]]}
                                        dataDetail={(curPath!==undefined)?path_hist[a][curPath][j]:null} //TODO show all paths
                                        limits={{minG:minG,maxG:maxG,minP:minP,maxP:maxP}}
                                        colourDetail={(curPath!==undefined)?colours[curPath]:''} //TODO show all paths
                                        dataGlobal={aspect_hist[a][j]}
                                        colourGlobal={'darkblue'}
                                    />)   
                    }
                }
                
                retJSX.push(<div className="oneAspect">
                    <div className="titles">
                        <p >{aspects[i].name}</p>
                        <img 
                            src={AspectExtended?'chevron-top.svg':'chevron-bottom.svg'}
                            title={AspectExtended?"Collapse":"Expand"}
                            alt={AspectExtended?"Collapse":"Expand"}
                            height="18" 
                            width="18" 
                            data-aspect={aspects[i].id}                            
                            onClick={ExtendedCallback}                            
                            style={{ paddingLeft: '2px', paddingTop:'2px', verticalAlign:'middle',cursor:'pointer'}}>                            
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