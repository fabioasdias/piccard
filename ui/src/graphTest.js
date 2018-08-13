import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './sankey.css';
import { actionCreators, getColour, getClass,} from './reducers';
import chroma from 'chroma-js';
import {ForceGraph, ForceGraphNode, ForceGraphLink} from 'react-vis-force';


const mapStateToProps = (state) => ({
    graph: state.graph,
    colours: state.colours,
    years: state.years,
    GraphLabels: state.GraphLabels,
  });

class GraphTest extends Component {
    render() {
        let {graph}=this.props;
        let {colours}=this.props;
        let {GraphLabels}=this.props;
        let {years}=this.props;
        let fixID=(ID)=>{
            return(ID[0]+' '+ID[1]);
        }

        if ((GraphLabels===undefined)||(graph===undefined)||(colours===undefined)||(years===undefined)){
            return(null)
        }
        else {
            let retJSX=[]
            console.log(GraphLabels);
            for (let node of graph.nodes){
                let c=getColour(colours,GraphLabels[+node.id[0]][node.id[1]].id);
                let x=years.indexOf(node.year);
                retJSX.push(<ForceGraphNode node={{ id: fixID(node.id), x:{x}, fixed:true }} fill={c} />)
            }
            for (let link of graph.links){
                retJSX.push(<ForceGraphLink link={{ source: fixID(link.source), target: fixID(link.target) }} />)
            }
        return(<ForceGraph zoom simulationOptions={{ height: 1000, width: 1000 }}>            
                {retJSX}
               </ForceGraph>);

        }


    }
}

export default connect(mapStateToProps)(GraphTest);