import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './tempEvo.css';
import {XYPlot, MarkSeries, XAxis, YAxis} from 'react-vis';
import {  sendData, getURL } from './urls';


const mapStateToProps = (state) => ({
  });


class TempEvo extends Component {
    constructor(props){
        super(props);
        this.state={projection:undefined};
    }

    componentDidMount(){
        sendData(getURL.GetAspectProjection(), 
            {countryID:'US', aspects:[]},
            (data)=>{
                console.log('projection',data);
                this.setState({projection:data});
            }
        );
    }

    render() {
        let retJSX=[];
        let {projection}=this.state;
        if (projection!==undefined){
            retJSX.push(<div>
                <XYPlot
                    width={300}
                    height={300}
                    yType='categorical'
                    xType='literal'
                >
                    <XAxis/>
                    <YAxis/>
                    <MarkSeries
                        getX={d => 280*d.x+10}
                        getY={d => d.y}
                        data={this.state.data}
                    />
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
