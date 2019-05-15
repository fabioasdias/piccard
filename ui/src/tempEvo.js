import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './tempEvo.css';
import {XYPlot, MarkSeries, XAxis, YAxis, Hint} from 'react-vis';
import { actionCreators, requestClustering } from './reducers';



const mapStateToProps = (state) => ({
    aspects: state.aspects,
  });


class TempEvo extends Component {
    constructor(props){
        super(props);
        this.state={tooltip:undefined};
    }

    render() {
        let retJSX=[];
        let {similarity}=this.props;
        let {dispatch}=this.props;
        if (similarity!==undefined){
            retJSX.push(<div>
                <XYPlot
                    width={380}
                    height={500}
                    xDomain={[0,1]}
                    >
                    <XAxis
                        // hideTicks
                    />
                    <YAxis
                        tickFormat={v => String(v)}
                    />
                    <MarkSeries
                        // color="darkgray"
                        stroke="lightgray"
                        data={similarity}
                        onValueMouseOver={(datapoint, event)=>{
                            this.setState({tooltip:datapoint});
                          }}
                        onValueMouseOut={(event)=>{
                            this.setState({tooltip:undefined})
                        }}
                        onValueClick={(datapoint, e)=>{
                            console.log('updating click', datapoint);
                            if (e.event.shiftKey){
                                dispatch(requestClustering([datapoint.id,]))
                            }
                            dispatch(actionCreators.SelectGeometry(datapoint.geometry));
                        }}
                    />
                    {(this.state.tooltip!==undefined)?
                        <Hint value={this.state.tooltip}>
                            <div style={{background: 'black'}}>
                                <p>{this.state.tooltip.name}</p>
                        </div>                    
                    </Hint>:null}
                </XYPlot>
            </div>)
        }
        return(
            <div className="TempEvo">
                {retJSX}
            </div>
        )
    }
}    
export default connect(mapStateToProps)(TempEvo);
