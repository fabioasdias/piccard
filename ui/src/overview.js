import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getColour, toInt,actionCreators} from './reducers';
import { XYPlot, XAxis, YAxis } from 'react-vis';
import './style.css';
import './overview.css';
import  BoxplotSeries  from './boxplot';
import chroma from 'chroma-js';

const mapStateToProps = (state) => ({
    colours: state.colours,
    level: state.level,
    patt: state.patt,    
    traj: state.traj,
  });

class Overview extends Component {
    constructor(props){
        super(props);
        this.state={'extended':[],'full':false};
    }
    render() {
        
        let {colours,dispatch}=this.props;
        let {patt,traj}=this.props;
        let {level}=this.props;
        let retJSX=[];
        let pattJSX=[];
        let tJSX=[];


        if (patt!==undefined){
            let cMax=[];
            pattJSX=[];
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


            for(let j=0;j<patt[0].variables.length;j++){
                let tMax=0.1;
                for(let i=0;i<patt.length;i++){
                    for (let k=0; k<patt[i].variables[j].length;k++){
                        tMax=Math.max(tMax,patt[i].variables[j][k].yMax);    
                    }
                }
                cMax.push(tMax);
            }
            let sumImportance=((a)=>{
                let s=0;
                let val;
                    for (let i=0;i<a.length;i++){
                        val=+(a[i].importance[level]);
                        s=(s>val)?s:val;
                }
                return(s);
            })
            let selectTIDs=(d)=>{
                console.log('selecting',d.target.getAttribute('data-clusterid'))
                let C=toInt(d.target.getAttribute('data-clusterid'));
                let tids=[];
    
                    for (let i=0;i<traj.length;i++){
                        for (let j=0;j<traj[i].chain.length;j++){
                            if (traj[i].chain[j]===C){
                                tids.push(traj[i].tid);
                                break;
                            }
                        }
                    }
                dispatch(actionCreators.SetTID(tids));
            }
        

            for(let i=0;i<patt.length;i++)
            {
                tJSX=[];                            
                tJSX.push(
                    <div key={'blockOut'} style={{display:'flex'}}>
                    <div key={String(i)+'block'}
                        onClick={selectTIDs}
                        data-clusterid={patt[i].id}
                        style={ {height:'20px', width:'190px', backgroundColor:getColour(colours,patt[i].id), margin:' 0 auto', marginTop:'1px' } }
                        >
                    </div>
                        {this.state.full?null:
                        <img 
                            src={this.state.extended.includes(i)?"chevron-left.svg":"chevron-right.svg"}
                            title={this.state.extended.includes(i)?"Collapse":"Expand"}
                            alt={this.state.extended.includes(i)?"Collapse":"Expand"}
                            height="18" 
                            width="18" 
                            data-cluster={i}                            
                            onClick={RedExt}                            
                            style={{paddingLeft: '2px', paddingTop:'2px', verticalAlign:'middle',cursor:'pointer'}}></img>}
                    </div>
                );
                let rightOrder=[];
                for (let vi=0;vi<patt[i].variables.length;vi++){
                    rightOrder.push(vi);
                }
                if (!this.state.full){
                    rightOrder=rightOrder.sort((a,b)=>{
                        return(sumImportance(patt[i].variables[b])-sumImportance(patt[i].variables[a]));
                    });
                }
                for (let vi of rightOrder)
                {            
                    let boxJSX=[];
                    let newData;
                    for (let A=0;A<patt.length;A++){
                        if (A!==i){
                            newData=patt[A].variables[vi].map((d)=>{
                                return({...d, 'fill':'black','stroke': 'black', 'opacity':0.25})
                            });
                            boxJSX.push(<BoxplotSeries
                                            data={newData}
                                            key={'b'+vi+A}
                                            doMinMax={false}
                                        />);                                    
                        }
                    }
                    newData=patt[i].variables[vi].map((d)=>{
                        let cimp=d.importance[level];
                        cimp=(cimp-0.35)/(0.65-0.35);
                        if (cimp<0){
                            cimp=0;
                        }
                        if (cimp>1){
                            cimp=1;
                        }
                        return({...d, 'stroke': 'grey', 'fill':'black'});
                    })
                    boxJSX.push(<BoxplotSeries
                                    data={newData}
                                    key={'o'+i+vi}
                                />);
                    tJSX.push(
                        <div key={'p'+i+' '+vi} style={{margin:'0px', marginBottom:'-5px'}}>
                            <p style={{fontSize: 'small', margin:'0px', marginBottom:'-5px'}} key={'name'+i+vi}>{patt[i].names[vi]}</p>
                            <XYPlot
                                xType={'ordinal'}
                                yType={"linear"}
                                yDomain={[0,cMax[vi]]}                           
                                fillType={'literal'}
                                key={'plot'+i+vi}
                                width={200}
                                height={90}>      
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
                                {boxJSX}                          
                            </XYPlot>
                        </div>
                    );
                    if ((!this.state.full)&&(!this.state.extended.includes(i))){
                        break
                    }    
                }
                let cName=(this.state.extended.includes(i))||(this.state.full)?'pattColExtended':'pattColReduced';
                let cStyle={}
                if (this.state.full){
                    cStyle.display='block';
                }
                pattJSX.push(
                    <div className={cName}
                            style={cStyle}
                            key={String(i)+'ds'}>         
                        {tJSX}
                    </div>);
            }
            if (!this.state.full){
                retJSX.push(<div key='patts' className="patts">
                                {pattJSX}
                            </div>);
            }else{
                pattJSX.push(<button key='pattclose' className="detButton" 
                    onClick={(e) => {this.setState({full:false,extended:[]});}}> 
                    <img src="x.svg" alt='Close panel' height="16" width="16" style={{verticalAlign:'middle'}}></img>
                </button>);
                retJSX.push(<div key='patts' className="fullDetails">{pattJSX}</div>);             
            }
            
        }
        return(
            <div className="Overview">
                {retJSX}
            </div>
        );           
    }
}    
export default connect(mapStateToProps)(Overview);

