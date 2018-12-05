import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import { Sankey} from 'react-vis';
import './sankey.css';
import {  actionCreators, getColour } from './reducers';


const mapStateToProps = (state) => ({
    gj: state.gj,
    years: state.years,
    tID: state.tID,
    traj: state.traj,
    colours: state.colours,
    labels: state.labels,
  });


class TempEvo extends Component {
    constructor(props) {
        super(props);
        this.state = {
           min: 0, 
           max: 100,
        };
      }

    render() {
        let {colours}=this.props;
        let {dispatch}=this.props;
        let {years}=this.props;
        let {labels}=this.props;
        let {traj}=this.props;
        let selTID=this.props.tID;
        
        let {gj}=this.props;
        let retJSX=[]
        let nodes=[];
        let links=[];

        const insertGetInd = (k) => {
            let ind=nodes.findIndex((element)=>{
                return((element.key.year===k.year) && (element.key.id===k.id));
            });
            if (ind<0)
            {
                ind=nodes.length;
                nodes.push({name:'', key:{...k,ind:ind,tID:[k.tID,]}, class:k.id, opacity: 1, color:getColour(colours,k.id)});
            }else{
                if (!nodes[ind].key.tID.includes(k.tID)){
                    nodes[ind].key.tID.push(k.tID);
                }
                
            }
            return(ind);
        };
        const addLinkVal = (L,s,t,v,tID) =>{
            let tColour;
            if ((selTID.length>0) && (! selTID.includes(tID))){
                tColour='lightgray';
            }
            else{
                tColour='darkgray';
            }
            L.push({source:s,target:t,value:v, tID:tID, chain: traj[tID].chain, years: traj[tID].years, color: tColour});
            return(L);
        };

        if ((labels!==undefined)&&(gj!==undefined) && (years!==undefined) && (colours!==undefined))
        {        
            for (let i=0;i<traj.length;i++){
                for (let j=0;j<(traj[i].chain.length-1);j++){
                    let y0=traj[i].years[j];
                    let y1=traj[i].years[j+1]
                    let cNode=insertGetInd({year:y0,id:traj[i].chain[j],tID:traj[i].tid});
                    let cPop=traj[i].numNodes[y0];
                    let nNode=insertGetInd({year:y1,id:traj[i].chain[j+1],tID:traj[i].tid});
                    let nPop=traj[i].numNodes[y1];
                    links=addLinkVal(links,cNode,nNode,Math.min(cPop,nPop),i);    
                }
            }
            let tJSX=[]
            for (let y of years){
                    tJSX.push(<div key={'year'+y}>{y}</div>)
            }

            retJSX.push(<div key='titlesankey' style={{width:'fit-content',height:'fit-content',margin:'auto',paddingTop:'5px'}}>Trajectories</div>);

            retJSX.push(<div key='yearsbar' className='yearsBar'>{tJSX}</div>);
            let onLink=(d)=>{
                dispatch(actionCreators.SetTID(d.tID));
            };
            let onValClick=(d)=>{
                let ctids=d.key.tID;
                dispatch(actionCreators.SetTID(ctids));
            };
            retJSX.push(
                  <Sankey    
                    key='sankey'            
                    style={{margin:'auto', zIndex:-10}}
                    height={320}
                    width={500}
                    nodes={nodes}
                    links={links}
                    onLinkClick={onLink}
                    onValueClick={onValClick}
                  />)
        }
        return(
            <div className="TempEvo">
                {retJSX}
            </div>
        )
    }
}    
export default connect(mapStateToProps)(TempEvo);
