import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './tempEvo.css';
import {XYPlot, MarkSeries, XAxis, YAxis, Hint} from 'react-vis';
import { sendData, getURL } from './urls';
import { actionCreators } from './reducers'
import {arrayEQ} from './util';


const mapStateToProps = (state) => ({
    aspects: state.aspects,
  });


class TempEvo extends Component {
    constructor(props){
        super(props);
        this.state={projection:undefined, tooltip:undefined};
    }

    updateData(aspects){
        sendData(getURL.GetAspectProjection(), 
        {aspects:aspects},
        (data)=>{
            this.setState({projection:data});
        });
    }

    componentWillReceiveProps(props){
        if (!arrayEQ(this.props.aspects, props.aspects)){
            this.updateData(props.aspects);
        }
    }
    componentDidMount(){
        this.updateData(this.props.aspects);
    }

    render() {
        let retJSX=[];
        let {projection}=this.state;
        let {dispatch}=this.props;
        if (projection!==undefined){
            retJSX.push(<div>
                <XYPlot
                    width={380}
                    height={800}
                    >
                    <XAxis
                        hideTicks
                    />
                    <YAxis
                        tickFormat={v => String(v)}
                    />
                    <MarkSeries
                        // color="darkgray"
                        stroke="lightgray"
                        data={projection}
                        onValueMouseOver={(datapoint, event)=>{
                            this.setState({tooltip:datapoint});
                          }}
                        onValueMouseOut={(event)=>{
                            this.setState({tooltip:undefined})
                        }}
                        onValueClick={(datapoint, event)=>{
                            console.log('updating click', datapoint)
                            dispatch(actionCreators.SelectGeometry(datapoint.geometry));
                            dispatch(actionCreators.SelectAspects([datapoint.id,]));
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
