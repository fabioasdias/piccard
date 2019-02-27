import React, { Component } from 'react';
import './aspects.css';
import {sendData,getData,getURL} from './urls';

class Aspects extends Component {
    constructor(props){
        super(props);
        this.state={files:[],aspects:[],availableCountries:this.props.availableCountries};
    }
    render(){
        let retJSX=[];
        
        if (this.props.availableCountries!==undefined){                
            retJSX.push(
                <div style={{display:'flex'}}>
                    <button 
                    onClick={()=>{
                        getData(getURL.getUploadedData(),(data)=>{
                            console.log(data);
                            let asp=[];
                            for (let i=0;i<data.length;i++){
                                console.log(data[i].aspects);
                                for (let j=0;j<data[i].aspects.length;j++){
                                    asp.push({
                                            enabled:true,
                                            country:data[i].country,
                                            year:data[i].year,
                                            geomYear:data[i].geomYear,
                                            name:data[i].aspects[j][0].slice(0,3),
                                            normalized:false,
                                            fileID:data[i].id,
                                            columns:data[i].aspects[j]});
                                    }
                            }
                            this.setState({files:data,aspects:asp});
                        });                
                    }}>
                    Refresh available data
                    </button>
                    <button onClick={()=>{
                        sendData(getURL.createAspects(),this.state.aspects,(d)=>{
                            console.log('data sent', d)
                        })
                    }}>
                        Save aspects                    
                    </button>
                </div>);



            let {files,aspects}=this.state;
            let onChange = (e)=>{
                let which=e.target.getAttribute('data-which');
                let k=parseInt(e.target.getAttribute('data-k'),10);
                let tarray=this.state.aspects.slice();
                if (which==='year'){
                    tarray[k][which]=parseInt(e.target.value,10);
                }else{
                    if ((which==='enabled')||(which==='normalized')){
                        tarray[k][which]=e.target.checked;
                    }
                    else{
                        tarray[k][which]=e.target.value;
                    }
                }
                this.setState({aspects:tarray.slice()})
            }

            for (let i=0;i<aspects.length;i++){
                let columnsJSX=[];
                let curFile=files.filter((f)=>{
                    return(aspects[i].id===f.fileID);
                })[0];
                let curCols=curFile.columns;

                columnsJSX.push(<div style={{'display':'flex','fontWeight': 'bold'}}>
                    <div style={{'paddingRight':'15px'}}>Column</div>
                    <div style={{'marginLeft':'auto'}}>Sample</div>
                    </div>)

                for(let j=0; j<aspects[i].columns.length;j++){
                    columnsJSX.push(<div style={{'display':'flex'}}>
                        <div style={{'paddingRight':'15px'}}>{curCols[aspects[i].columns[j]]}</div>
                        <div style={{'marginLeft':'auto'}}>{curFile.samples[aspects[i].columns[j]]}</div>
                        </div>)
                }
                console.log(aspects[i])
                retJSX.push(<div className="aspects">
                    <div>
                        <input 
                            type="checkbox" 
                            onChange={onChange}
                            data-k={i}
                            data-which={'enabled'}
                            checked={this.state.aspects[i].enabled}/>                        
                    </div>

                    <div> Name: 
                        <input 
                            type="text" 
                            onChange={onChange}
                            data-k={i}
                            data-which={'name'}
                            defaultValue={this.state.aspects[i].name}/>                        
                    </div>

                    <div> Normalized:
                        <input 
                            type="checkbox" 
                            onChange={onChange}
                            data-k={i}
                            data-which={'normalized'}
                            checked={this.state.aspects[i].normalized}/>                        
                    </div>


                    <div> Country: 
                        <select 
                            onChange={onChange}
                            data-k={i}
                            defaultValue={aspects[i].country}
                            data-which={'country'}>

                        {this.props.availableCountries.map((d)=>{
                            return(<option
                                    value={d.kind}
                                >
                                {d.name}
                            </option>)})}
                        </select>
                    </div>
                        
                    <div> Year: 
                        <input
                            type="text"
                            onChange={onChange}
                            data-k={i}
                            data-which={'year'}
                            defaultValue={aspects[i].year}/>
                    </div>

                    <div> Geometry: 
                        <select 
                            onChange={onChange}
                            data-k={i}
                            data-which={'geomYear'}
                            defaultValue={aspects[i].geomYear}>
                        {this.props.availableCountries.filter((e)=>{
                            return(e.kind===aspects[i].country);
                          })[0].years.map((d)=>{
                            return(<option
                                    value={d}
                                >
                                {d}
                            </option>)})}
                        </select>
                    </div>

                    <div>
                        {columnsJSX}
                    </div>

                </div>);
            }
        }
        return(
            <div className="aspects">
                {retJSX}
            </div>
        );
    }
}

export default Aspects;
            