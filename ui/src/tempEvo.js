import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './tempEvo.css';
import ParallelCoordinates from './parcor';
import { LabelSeries} from 'react-vis';
import { actionCreators, requestClustering } from './reducers';



const mapStateToProps = (state) => ({
  });


class TempEvo extends Component {
    constructor(props){
        super(props);
        this.state={tooltip:undefined};
    }

    render() {
        let retJSX=[];
        // let {dispatch}=this.props;
        if (this.props.data!==undefined){
            let {aspects,evolution}=this.props.data;
            evolution=evolution.slice(0,200);
            let domains=aspects.filter((d)=>{
                return(d.visible);
            }).map((d)=>{
                return({'name':d.id, domain:[0,1], getValue: (e)=> e[d.id]});
            }).sort((a,b)=>{
                return(a.order-b.order);
            });
            retJSX.push(<div>
                <ParallelCoordinates
                    data={evolution}
                    domains={domains}
                    height={400}
                    width={1600}
                    margin={{left: 40, right: 10, top: 20, bottom: 20}}
                    showMarks={false}
                    tickFormat={(d)=>{}}
                    brushing={true}
                    colorType={'literal'}
                    style={{
                        deselectedLineStyle:{
                            strokeOpacity:0,
                            color:'gray'
                        },
                        line:{
                            strokeOpacity:0.9,
                        },
                        axes: {
                            line: {},
                            ticks: {},
                            text: {}
                        },
                        labels: {
                        //     fontSize: 10,
                        //     style: {
                        //         // transform: 'rotate(-20deg)',
                        //         // transformBox: 'fill-box',
                                visibility:'hidden'
                        //     }
                        },
                    }}
                />
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
