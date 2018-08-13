import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './transMat.css'
import { actionCreators, getColour, toInt } from './reducers';
// import MappleToolTip from 'reactjs-mappletooltip';

const mapStateToProps = (state) => ({
    years: state.years,
    tID: state.tID,
    traj: state.traj,
    colours: state.colours,
  });

class TransMat extends Component {
    constructor(props){
        super(props);
        this.state={cYear:0};
    }

    render(){
        let retJSX=[];
        let tJSX=[];
        let {traj,colours,years,dispatch,tID}=this.props;
        let mat={};
        let bolds={};
        let selectTIDsSingle=(d)=>{
            let C=toInt(d.target.getAttribute('data-clusterid'));
            let tids=[];

                for (let i=0;i<traj.length;i++){
                    for (let j=0;j<traj[i].chain.length;j++){
                        if (traj[i].chain[j]===C){
                            tids.push(traj[i].tid);
                            break
                        }
                    }
                }
            dispatch(actionCreators.SetTID(tids));
        }


        let selectTIDs=(d)=>{
            let l1=toInt(d.target.getAttribute('data-from'));
            let l2=toInt(d.target.getAttribute('data-to'));
            let y=toInt(this.state.cYear);
            let indY;
            let tids=[];

            if (y>0){
                indY=years.indexOf(y);
                let y2=years[indY+1];
                for (let i=0;i<traj.length;i++){
                    let j1=traj[i].years.indexOf(y);
                    let j2=traj[i].years.indexOf(y2);
                    if ((j1>=0)&&(j2>=0)){
                        if ((traj[i].chain[j1]===l1)&&(traj[i].chain[j2]===l2)){
                            tids.push(traj[i].tid);
                        }
                    }
                }
            }else{
                for (let i=0;i<traj.length;i++){
                    for (let j=0;j<(traj[i].chain.length-1);j++){
                        if (y===-1){
                            if ((traj[i].chain.length===years.length)&&(traj[i].chain[0]===l1)&&(traj[i].chain[years.length-1]===l2)){
                                tids.push(traj[i].tid);
                                break;
                            }    
                        }else{
                            if ((traj[i].chain[j]===l1)&&(traj[i].chain[j+1]===l2)){
                                tids.push(traj[i].tid);
                            }    
                        }
                    }
                }
            }    
            dispatch(actionCreators.SetTID(tids));
        }


        if (traj!==undefined){
            for (let i=0;i<traj.length;i++){
                let l1;
                let l2;
                for (let j=0;j<(traj[i].chain.length-1);j++){
                    if ((this.state.cYear>0)&&(traj[i].years[j]!==this.state.cYear)){
                        continue;
                    }    

                    if (((this.state.cYear===-1)&&(traj[i].chain.length!==years.length)) ||
                        ((this.state.cYear===-1)&&(j!==0))){
                        break
                    }

                    l1=traj[i].chain[j];
                    if (this.state.cYear===-1){
                        l2=traj[i].chain[years.length-1];
                    }else{
                        l2=traj[i].chain[j+1];
                    }
                    
                    if (!mat.hasOwnProperty(l1)){
                        mat[l1]={};
                        bolds[l1]={};
                    }
                    if (!mat[l1].hasOwnProperty(l2)){
                        mat[l1][l2]=0.0;
                        bolds[l1][l2]=false;
                    }
                    mat[l1][l2]+=traj[i].pop[traj[i].years[j]];
                    if (tID.includes(traj[i].tid)){
                        bolds[l1][l2]=true;
                    }                          
                }
            }

            let allL=[];
            for (let i in mat){
                let s=0;
                for (let j in mat[i]){
                    s+=mat[i][j];
                    if (!allL.includes(j)){
                        allL.push(j);
                    }
                }
                for (let j in mat[i]){
                    mat[i][j]=mat[i][j]/s;
                }
                
            }

            let maxN=allL.length;
            tJSX=[];
            tJSX.push(<option 
                value={0} 
                key={'all'} 
                selected={true}
                > 
                    Any
                </option>);
            for (let i=0;i<years.length-1;i++){
                tJSX.push(<option 
                    value={years[i]} 
                    key={i} 
                    selected={false}
                    > 
                       {years[i]} to {years[i+1]}
                    </option>);
            }
            tJSX.push(<option
                        value={-1}
                        key={'startEnd'}
                        selected={false}
                        >
                          {years[0]} to {years[years.length-1]}
                       </option>);
            retJSX.push(
                <div key={'changeTitle'} style={{width:'fit-content',height:'fit-content',display:'flex',margin:'auto'}}>
                <p style={{paddingRight:'20px'}}>Cluster changes</p>
                <select key={'selYear'}
                    style={{height: '2em', margin:'auto'}}
                    className="dropboxes" 
                    onChange={(e)=>{
                    let curVal=toInt(e.target.value);
                    this.setState({cYear:curVal});
                }} >
                {tJSX}
            </select></div> );
            

            tJSX=[];
            maxN+=1;
            let W=380/maxN+'px';
            let H=225/maxN+'px';
            let rightOrder=allL.sort((a,b)=>{
                if ((mat[a]===undefined)||(mat[a][a]===undefined)){
                    return(true);
                }
                if ((mat[b]===undefined)||(mat[b][b]===undefined)){
                    return(false);
                }
                return(mat[a][a]<mat[b][b]);
            })

            tJSX.push(<div key={'fromto'} style={{width:W,height:H,margin:'0',display:'flex'}}>
                        <p style={{margin:0,fontSize:'x-small',textAlign:'left',alignSelf:'flex-end'}}>From</p>
                        <p style={{margin:'0 0 auto auto',fontSize:'x-small',textAlign:'right'}}>To</p>
                        
                      </div>);
            for (let i of rightOrder){
                tJSX.push(<div key={'Ycolour'+i}
                                style={{backgroundColor:getColour(colours,i),width:W,height:H,margin:'0'}}
                                data-clusterid={i}
                                onClick={selectTIDsSingle}
                                >
                            </div>);
            }
            retJSX.push(<div key={'transColourBar'} style={{width:380, display:'flex'}}>{tJSX}</div>);
            
            for (let i of rightOrder){
                tJSX=[];
                tJSX.push(<div  key={'Xcolour'+i}
                    style={{backgroundColor:getColour(colours,i),width:W,height:H,margin:'0'}}
                    data-clusterid={i}
                    onClick={selectTIDsSingle}
                    >
                </div>);

                for (let j of rightOrder){
                    let tStyle={width:'fit-content',height:'fit-content',margin:'auto',fontWeight:'normal'};
                    if ((bolds[i]!==undefined)&&(bolds[i][j]!==undefined)&&(bolds[i][j])){
                        tStyle.fontWeight='bold';
                    }                    
                    tJSX.push(<div key={'vals'+i+'_'+j}
                        style={{width:W,height:H,margin:'auto',cursor:'pointer',textDecoration: 'underline',display:'flex'}} 
                        data-from={i} 
                        data-to={j} 
                        onClick={selectTIDs}>
                        {((mat[i]!==undefined)&&(mat[i][j]!==undefined))?(<p data-from={i} data-to={j} style={tStyle}>{Math.ceil(100*mat[i][j])/1}%</p>):null}
                    </div>);
                }
                retJSX.push(<div key={'row'+i} style={{width:380, display:'flex'}}>{tJSX}</div>);
            }

        }//traj!=undef    
        return(<div className='TransMat'>{retJSX}</div>);
    }
}


export default connect(mapStateToProps)(TransMat);
