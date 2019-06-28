import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import './tempEvo.css';
import ParallelCoordinates from './parcor';
import { LabelSeries} from 'react-vis';
import { actionCreators, requestClustering } from './reducers';



const mapStateToProps = (state) => ({
    selectedClusters: state.selectedClusters,
  });


class TempEvo extends Component {
    constructor(props){
        super(props);
        this.state={tooltip:undefined, width: window.innerWidth,};
    }
    componentWillMount() {
        window.addEventListener('resize', this.handleWindowSizeChange);
      }
      
      // make sure to remove the listener
      // when the component is not mounted anymore
      componentWillUnmount() {
        window.removeEventListener('resize', this.handleWindowSizeChange);
      }
      
      handleWindowSizeChange = () => {
        this.setState({ width: window.innerWidth });
      };
    
    render() {
        let retJSX=[];
        let {dispatch}=this.props;
        if ((this.props.data!==undefined)&&(this.props.colours!==undefined)){
            let {aspects,evolution}=this.props.data;
            evolution=evolution.map((d)=>{
                return({...d,color:this.props.colours[d.id]})
            });
            let domains=aspects.filter((d)=>{
                return(d.visible);
            }).map((d)=>{
                return({ ...d,
                         name:d.id, 
                         label: d.name, 
                         cols: d.cols,
                         descr: d.descr,
                         domain:[0,1], 
                         getValue: (e)=> e[d.id]});
            }).sort((a,b)=>{
                return(b.order-a.order);
            });
            let highcb=(sel)=>{
                dispatch(actionCreators.SelectClusters(sel));
            }
            console.log('tempEvo',evolution);
            let W=this.state.width;
            retJSX.push(<div>
                <ParallelCoordinates
                    data={evolution}
                    domains={domains}
                    height={Math.max(domains.length*40,800)}
                    width={(W<600)?W:W*0.5}
                    highlightCallback={highcb}
                    margin={{left: 20, right: W/12, top: 20, bottom: 20}}
                    showMarks={true}
                    tickFormat={(d)=>{}}
                    brushing={true}
                    colorType={'literal'}
                    style={{
                        deselectedLineStyle:{
                            strokeOpacity:0.25,
                        },
                        lines:{
                            strokeOpacity:0.9,
                        },
                        // labels: {
                        //     fontSize: 10,
                        //     style: {
                        //         // transform: 'rotate(-20deg)',
                        //         // transformBox: 'fill-box',
                        //         visibility:'hidden'
                        //     }
                        // },
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
