import React, { Component } from 'react';
import './aspects.css';
import {sendData,getData,getURL} from './urls';

class Aspects extends Component {
    constructor(props){
        super(props);
        this.state={files:[],aspects:[]};
    }
    render(){
        let retJSX=[];
        
        if (this.props.availableGeometries!==undefined){                
            retJSX.push(
                <div style={{display:'flex'}}>
                    <button 
                    onClick={()=>{
                        getData(getURL.GetUploadedData(),(data)=>{
                            console.log('answer',data);
                            data = data.sort((a,b)=>{
                                return(a.year-b.year);
                            });
                            let asp=[];
                            for (let i=0;i<data.length;i++){
                                console.log('data[i].aspects',data[i].aspects);
                                for (let j=0;j<data[i].aspects.length;j++){
                                    asp.push({
                                            enabled:false,
                                            year:data[i].year,
                                            geometry:data[i].geometry.name,
                                            name:data[i].aspects[j][0].slice(0,3),
                                            fileID:data[i].id,
                                            index:data[i].index,
                                            columns:data[i].aspects[j]});
                                    }
                            }
                            console.log(data,asp);
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
                    if (which==='enabled'){
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
                    // console.log(i,f.id,aspects[i].fileID);
                    return(aspects[i].fileID===f.id);
                })[0];
                // console.log(i,curFile);
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
                            data-which={'geometry'}
                            defaultValue={aspects[i].geometry}>
                        {this.props.availableGeometries.map((d)=>{
                            return(<option
                                    value={d.name}
                                >
                                {d.name}
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
            