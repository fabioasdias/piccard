import React, { Component } from 'react';
import { connect } from 'react-redux';
import './style.css';
import { XYPlot, XAxis, YAxis, VerticalBarSeries} from 'react-vis';
import { actionCreators, getURL } from './reducers';
import './detail.css';

const mapStateToProps = (state) => ({
    showDetails: state.showDetails,
    region: state.region,
    years: state.years,
    cityID: state.cityID,
    details: state.details,
  });

 function requestDetails(cityID,region) {
    return function (dispatch) {
        return fetch(getURL.RegionDetails(cityID,region)).then(
            details => {
                details.json().then((d)=> {//promise of a promise. really.
                    dispatch(actionCreators.UpdateDetails(d));
                })
            },
            error => console.log('ERRORRRRR')
        );
    }
}

class Detail extends Component {
    componentWillReceiveProps(nextProps){
        let {region}=this.props;
        let {dispatch}=this.props;
        if (region!==nextProps.region)
            dispatch(actionCreators.UpdateDetails(undefined))
    }
    render() {
        let {region}=this.props;
        let {details}=this.props;
        let {showDetails}=this.props;
        let {years}=this.props;
        let {dispatch}=this.props;
        let {cityID}=this.props;
        let retJSX=[];

        if ((cityID!==undefined)&&(region!==undefined)&&(details===undefined))
        {
            dispatch(requestDetails(cityID,region))
            return(null);
        }
        if ((showDetails===undefined)||(showDetails===false)||
            (region===undefined)||(cityID===undefined)||(details===undefined)||
            ((details!==undefined)&&(details.length===0))){
            return(null);
        }        
        if ((details!==undefined)&&(years!==undefined))
        {
            for (let year of years){
                let tJSX=[];
                tJSX.push(<p>{year}</p>);

                if (details.hasOwnProperty(year)){
                    details[year].sort((a,b)=> {
                        if ((a.values.length===1)&&(b.values.length>1)){
                            return(-1);
                        }
                        else{
                            if ((a.values.length>1)&&(b.values.length===1)){
                                return(1);
                            }
                            else{
                                return(a.name>b.name);
                            }
                        }
                    });
                    for (let i=0;i<details[year].length;i++){
                        let d=details[year][i];
                        let cData=[];
                        let cAngle=0;
                        for (let j=0;j<d.short.length;j++)
                            cData.push({x:d.short[j],y:d.values[j]});
                        if (cData.length>2)
                            cAngle=-40;
                        if (cData.length===1){
                            tJSX.push(<div>{d.name} : {cData[0].y}</div>)
                        }
                        else{
                            tJSX.push(<p style={{marginBottom:'-5px'}}>{d.name}</p>);
                            tJSX.push(<XYPlot
                                            xType={'ordinal'}
                                            yType={"linear"}
                                            width={250}
                                            height={100}>      
                                            <VerticalBarSeries key={year+' v'+i} 
                                                data={cData}
                                            />
                                            <XAxis 
                                                tickLabelAngle={cAngle}
                                                style={{
                                                    line: {stroke: 'darkgrey'},
                                                    ticks: {stroke: 'darkgrey'},
                                                    text: {stroke: 'none', fill: 'black'}
                                                }}                            
                                            />
                                            <YAxis 
                                                style={{
                                                    line: {stroke: 'darkgrey'},
                                                    ticks: {stroke: 'darkgrey'},
                                                    text: {stroke: 'none', fill: 'black'}
                                                    }}                            
                                            />
                                        </XYPlot>);
                        }
                    }
                }
                retJSX.push(<div className="detColumn">{tJSX}</div>);
            }
            retJSX.push(<button 
                className="detButton" 
                onClick={(e) => {
                    dispatch(actionCreators.ShowDetails(false));
                }}> 
                <img src="x.svg" alt='Close panel' height="16" width="16" style={{verticalAlign:'middle'}}></img>
            </button>);
            return(<div className="Detail"> 
                    {retJSX}

                </div>);
        }
    }
}    
export default connect(mapStateToProps)(Detail);
