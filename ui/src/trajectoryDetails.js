import React, { Component } from 'react';
import { connect } from 'react-redux';
import { toInt, requestPath} from './reducers';
import './style.css';
import './trajectoryDetails.css';
import { XYPlot, XAxis, YAxis, LineSeries, HorizontalGridLines, VerticalGridLines, AreaSeries  } from 'react-vis';
import MappleToolTip from 'reactjs-mappletooltip';

import SmMaps from './smmaps';

const mapStateToProps = (state) => ({
    level: state.level,
    years: state.years,
    colours: state.colours,
    basedata: state.basedata,
    nids: state.nids,
    gj: state.gj,
    path: state.path,
    globalPath: state.globalPath,
    population: state.population,
    patt: state.patt,
    cityID: state.cityID,
    traj: state.traj,
    dsconf: state.dsconf
  });

let objSameProps=(o1,o2)=>{
    let A1=Object.keys(o1);
    let A2=Object.keys(o2);
    if (A1.length!==A2.length){
        return(false);
    }
    for (let a of A1){
        if (!A2.includes(a)){
            return(false);
        }
    }
    return(true);
}

class TrajDet extends Component {
    constructor(props){
        super(props);
        this.state={extended:[],value:undefined};
    }
    
    componentWillUpdate(nextProps, nextState) {
        let {dispatch,cityID,traj,dsconf,nids}=nextProps;
        console.log('will')
        let k=Object.keys(nids);
        if ((k.length>0)&&(!objSameProps(this.props.nids,nids))){
            console.log('request')
            console.log(k)
            dispatch(requestPath(cityID,dsconf.vars,dsconf.fs,k));    
        }
    }

    
    render () {
        let {path}=this.props;
        let {nids}=this.props;
        let {years}=this.props;
        let {population}=this.props;
        let {basedata,globalPath}=this.props;
        let {gj}=this.props;
        let retJSX=[];
        let rowJSX=[];
        let tJSX=[];
        let imp={};
        let FW=1300;

        let RedExt=(e)=>{
            let c=toInt(e.target.getAttribute('data-cluster'));
            let cExtended=this.state.extended.slice();
            if (cExtended.includes(c)){
                cExtended.splice(cExtended.indexOf(c),1);
            }else{
                cExtended.push(c);
            }
            this.setState({extended:cExtended.slice()});
        }
        
        retJSX.push(<SmMaps key={'smallmaps'} gj={gj} nids={nids} years={years}/>);

        rowJSX=[];
        for (let y of years){
            let pop=y+': ';
            if (population[y]!==undefined){
                pop=pop+population[y].toLocaleString();
                if (population[y]!==basedata.population[y]){
                    pop=pop+' - '+(Math.round(1000*population[y]/basedata.population[y])/10).toLocaleString()+'%'
                }
            }
            rowJSX.push(<div key={'pop'+y} style={{width:'300px',height:'fit-content',margin:'auto',display:'flex'}}>
                            {y===years[0]?<p style={{width:'fit-content',height:'fit-content',margin:'auto 0',textAlign:'left'}}>Population</p>:null}
                            <p style={{margin:'auto',textAlign:'right',marginRight:'5px'}}>
                                {pop}
                            </p>
                        </div>);    
        }
        retJSX.push(<div key={'PanelPop'} className='varPanel'>{rowJSX}</div>)
    
    
        if (path!==undefined){
            // let cScale=chroma.scale(['black','darkred','red']).mode('lab').correctLightness().classes(5);            
        
            for (let i=0;i<path.length;i++){
                imp[i]=0;
                let divider=0;
                for (let j=0;j<path[i].ranges.length;j++){
                    for (let year in path[i].ranges[j].states){
                        let Q1=path[i].ranges[j].states[year][0].Q1;
                        let Q3=path[i].ranges[j].states[year][0].Q3;
                        let gQ1=basedata.paths[i].ranges[j].states[year][0].Q1
                        let gQ3=basedata.paths[i].ranges[j].states[year][0].Q3;
                        imp[i]+=Math.max(Q1,gQ1)-Math.min(Q3,gQ3);
                        divider+=1;
                        // imp[i]=Math.max(imp[i],
                        //     Math.max(Q1,gQ1)-Math.min(Q3,gQ3)
                        // );
                    }
                }
                imp[i]=imp[i]/(divider);
            }
            let rightOrder=[];
            for (let i=0;i<path.length;i++){
                rightOrder.push(i);
            }
            rightOrder.sort((a,b)=>{
                return(imp[a]<imp[b])
            });
            rowJSX=[];

            for (let i of rightOrder){
                tJSX=[];

                if (!this.state.extended.includes(i)){
                    let minSize=[];
                    let maxSize=[];
                    let tooltip=[];

                    for (let j=0;j<path[i].ranges.length;j++){
                        minSize.push(1);
                        maxSize.push(0);
                    }
                    for (let j=0;j<path[i].ranges.length;j++){
                        tooltip.push([]);
                        let ttdata=[];
                        let tgdata=[];
                        tooltip[j].push(<p key={'tooltip'+i+'_'+j} style={{margin:'auto'}}>{path[i].ranges[j].long}</p>);
                        for (let y of years){
                            if (path[i].ranges[j].states[y]!==undefined)
                            {
                                ttdata.push({x:y,y:path[i].ranges[j].states[y][0].med});
                                tgdata.push({x:y,y:basedata.paths[i].ranges[j].states[y][0].med});
                                minSize[j]=Math.min(minSize[j],path[i].ranges[j].states[y][0].med);
                                maxSize[j]=Math.max(maxSize[j],path[i].ranges[j].states[y][0].med);
                            }
                        }
                        tooltip[j].push(<XYPlot
                                xType={'ordinal'}
                                yType={"linear"}
                                yDomain={[0,1]}
                                // fillType={'literal'}
                                key={'tt'+i+'='+j}
                                width={200}
                                height={200}>      
                                <XAxis 
                                    tickLabelAngle={-20}
                                    style={{
                                        line: {stroke: 'darkgrey'},
                                        ticks: {stroke: 'darkgrey'},
                                        text: {stroke: 'none', fill: 'black', fontSize:'10px'}
                                    }}
                                />
                                <YAxis 
                                    tickFormat={v => `${100*v}%`}                            
                                    style={{
                                        line: {stroke: 'darkgrey'},
                                        ticks: {stroke: 'darkgrey'},
                                        text: {stroke: 'none', fill: 'black', fontSize:'10px'}
                                    }}                            
                                />      
                                <LineSeries
                                    data={ttdata}
                                    color={'black'}                                    
                                    key={j+'ttb'+i}
                                />                                    
                                {/* <LineSeries
                                    data={tgdata}
                                    color={'gray'}                                    
                                    key={j+'tgb'+i}
                                />                                     */}
                            </XYPlot>);    
                    }
                    let aSizes=[];
                    let sSum=0;
                    for (let j=0;j<path[i].ranges.length;j++){
                        aSizes.push((maxSize[j]+minSize[j]/2.0));
                        sSum+=aSizes[aSizes.length-1];
                    }
                    let aNames=[];
                    for (let j=0;j<aSizes.length;j++){
                        aSizes[j]=FW*(aSizes[j]/sSum);
                        if (aSizes[j]<10){
                            aNames.push('');
                        }
                        if ((aSizes[j]>=10)&&(aSizes[j]<=50)){
                            aNames.push(path[i].ranges[j].short[0]);
                        }
                        if ((aSizes[j]>=50)&&(aSizes[j]<=200)){
                            aNames.push(path[i].ranges[j].short);
                        }
                        if (aSizes[j]>200){
                            aNames.push(path[i].ranges[j].long);
                        }
                    }

                    for (let j=0;j<aSizes.length;j++){
                        tJSX.push( <MappleToolTip key={'tip'+j} style={{marginRight:"-1px"}} mappleType={'contra'}>
                                    <div className='ovPlotBlock' key={'innerTip'+j} style={{width:aSizes[j]}}><p style={{margin:'auto'}}>{aNames[j]}</p></div>
                                    <div>{tooltip[j]}</div> 
                                </MappleToolTip>);
                    }// className='ovPlotTooltip'
                }

                
                if (this.state.extended.includes(i)){
                    tJSX=[];
                        tJSX.push(
                        <div style={{display:'flex',margin:'auto', width:'fit-content'}}>
                            <div style={{display:'flex',border:'solid',borderWidth:'thin',borderColor:'lightgrey',padding:'2px'}}>
                                <div style={{width:'1em',height:'1em',backgroundColor:'darkgrey',margin:'auto'}}></div>
                                <p style={{paddingLeft:'10px',margin: '3px'}}>global</p>
                                {(this.state.value!==undefined)&&(this.state.value.variable===i)?<p style={{paddingLeft:'10px',margin: '3px'}}>{Math.round(100*this.state.value.global.Q1)}% - {Math.round(100*this.state.value.global.Q3)}%</p>:null}
                            </div>
                            {!globalPath?
                                <div  style={{display:'flex', marginLeft:'20px',border:'solid',borderWidth:'thin',borderColor:'lightgrey',padding:'2px'}}>
                                    <div style={{width:'1em',height:'1em',backgroundColor:'black',margin:'auto'}}></div>
                                    <p style={{paddingLeft:'10px',margin: '3px'}}>selection</p>
                                    {(this.state.value!==undefined)&&(this.state.value.variable===i)?<p style={{paddingLeft:'10px',margin: '3px'}}>{Math.round(100*this.state.value.sel.Q1)}% - {Math.round(100*this.state.value.sel.Q3)}%</p>:null}
                                </div>
                            :null}
                        </div>
                    );
                }



                retJSX.push(
                <div key={'panel'+i} className='varPanel' style={{height:'30px'}}>
                    <div style={{width:'250px',margin:'auto 2px'}}><p style={{margin:'auto 0'}}>{path[i].name}</p></div>
                    {tJSX}
                    <div style={{paddingLeft:'15px',paddingTop:'5px',marginRight:0,marginLeft:'10px',alignSelf:"right",}}>
                        <img 
                            src={this.state.extended.includes(i)?"chevron-top.svg":"chevron-bottom.svg"}
                            title={this.state.extended.includes(i)?"Collapse":"Expand"}
                            alt={this.state.extended.includes(i)?"Collapse":"Expand"}
                            height="16" 
                            width="16" 
                            data-cluster={i}                            
                            onClick={RedExt}                            
                            style={{verticalAlign:'middle',cursor:'pointer'}}>
                        </img>
                    </div>
                </div>);

                rowJSX=[];

                if (this.state.extended.includes(i)){
                    rowJSX=[];
                    let tdata=[];
                    for (let j=0;j<path[i].ranges.length;j++){
                        let plotJSX=[];
                        tdata=[];
                        for (let y in basedata.paths[i].ranges[j].states){
                            tdata.push({x:toInt(y),y:basedata.paths[i].ranges[j].states[y][0]['Q3'],y0:basedata.paths[i].ranges[j].states[y][0]['Q1']});
                        }
                        plotJSX.push(<AreaSeries
                                        opacity={0.9}
                                        color={'darkgrey'}
                                        onNearestX={(d,e)=>{
                                            let B=basedata.paths[i].ranges[j].states[years[e.index]][0];//,x:e.event.screenX,y:e.event.screenY
                                            this.setState({value:{...this.state.value,global:B,variable:i}});
                                        }}
                                        data={tdata}/>)
                        
                        
                        // rowJSX.push(<p style={{width:'222px',margin:'auto 0',fontSize:'small'}}>{path[i].ranges[j].long}</p>);
                        if (!globalPath){
                            let stats=['min','max'];
                            for (let k=0;k<stats.length;k++){
                                let v=stats[k];
                                tdata=[];
                                for (let y in path[i].ranges[j].states){
                                    tdata.push({x:toInt(y),y:path[i].ranges[j].states[y][0][v]});
                                }
                                plotJSX.push(<LineSeries
                                                color={'black'}
                                                strokeDasharray={'2,2'}
                                                data={tdata}/>)
                            }
                            tdata=[];
                            for (let y in path[i].ranges[j].states){
                                tdata.push({x:toInt(y),y:path[i].ranges[j].states[y][0]['Q3'],y0:path[i].ranges[j].states[y][0]['Q1']});
                            }
                            plotJSX.push(<AreaSeries
                                            opacity={0.65}
                                            color={'black'}
                                            onNearestX={(d,e)=>{
                                                let A=path[i].ranges[j].states[years[e.index]][0];
                                                let B=basedata.paths[i].ranges[j].states[years[e.index]][0];//,x:e.event.screenX,y:e.event.screenY
                                                this.setState({value:{sel:A,global:B,variable:i}});
                                            }}
                                            onMouseLeave={(d)=>{this.setState({value:undefined})}}
                                            data={tdata}/>)
                                        }                    
                        let thisMargin={ top: 20, left: 30, right: 5, bottom: 30 };
                        let thisW=Math.min(300,FW/path[i].ranges.length);
                        let thisH=thisW;
                        if (j===0) {
                            thisMargin.left=40;
                            thisW+=10;
                        }
                        if (j===(path[i].ranges.length-1)){
                            thisMargin.right=40;
                            thisW+=25;
                        }
                        rowJSX.push(<div><p style={{marginBottom:'-10px'}}>{path[i].ranges[j].long}</p>
                                    <XYPlot
                                        key={'p'+i+'_'+j}
                                        xType='linear'
                                        yType='linear'
                                        yDomain={[0,1]}
                                        margin={thisMargin}
                                        width={thisW}
                                        height={thisH}
                                        onMouseLeave={(d)=>{this.setState({value:undefined})}}
                                        >
                                        <XAxis
                                            tickValues={years}
                                            tickFormat={v => `${v}`}                            
                                            style={{text:{textAlign:'center'}}}
                                            tickLabelAngle={-30}
                                        />
                                        {((j===0)||(j===path[i].ranges.length-1))?<YAxis
                                        tickFormat={v => `${100*v}%`}                            
                                        orientation={(j===path[i].ranges.length-1)?'right':'left'}
                                        />:null}                                            
                                        
                                        <HorizontalGridLines 
                                            style={{stroke:'black',opacity:0.75}}
                                        />
                                        <VerticalGridLines 
                                            tickValues={years}
                                            style={{stroke:'black',opacity:0.75}}
                                            />
                                            {plotJSX}
                                    </XYPlot></div>);
                    }
                    retJSX.push(<div className='varRow'>{rowJSX}</div>)                    
                }                    
            }            
        }

        return(<div className="trajDet" key='trajDet'>
                {retJSX}
                </div>);
    }
}
  

export default connect(mapStateToProps)(TrajDet);

