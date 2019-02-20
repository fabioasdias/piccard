import React, { Component } from 'react';
import './aspects.css';
import {getData,getURL} from './reducers';

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
                                for (let j=0;j<data[i].aspects.length;j++){
                                    asp.push({country:data[i].country,
                                            year:data[i].year,
                                            name:data[i].aspects[j][0].slice(0,3),
                                            normalized:false,
                                            normalizingField:'',
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
                        let a=aspects.slice();
                        a.push({country:'',
                                name:'',
                                year:'', 
                                fileID:'',
                                normalized:false,
                                normalizingField:'',
                                columns:[]});
                        this.setState({aspects:a.slice()});
                    }}>
                    Add aspect
                    </button>
                </div>);



            let {files,aspects}=this.state;
            let onChange = (e)=>{
                console.log(e.target);
                let which=e.target.getAttribute('data-which');
                let k=parseInt(e.target.getAttribute('data-k'),10);
                console.log('change',which,k);
                let tarray=this.state.aspects.slice();
                if (which==='year'){
                    tarray[k][which]=parseInt(e.target.value,10);
                }else{
                    tarray[k][which]=e.target.value;
                }
                
                this.setState({aspects:tarray.slice()})
            }

            for (let i=0;i<aspects.length;i++){
                let columnsJSX=[];
                console.log(aspects);
                console.log(files.filter((f)=>{
                    return(aspects[i].id===f.fileID);
                })[0])

                for(let j=0; j<aspects[i].columns.length;j++){
                    // columnsJSX.push(<p>{files.filter((f)=>{
                        // return(aspects[i].id===f.fileID);
                    // })
                    // aspects[i].columns[j]}</p>)
                }

                retJSX.push(<div className="aspects">

                    <div> Name: 
                        <input 
                            type="text" 
                            onChange={onChange}
                            data-k={i}
                            data-which={'name'}
                            defaultValue={this.state.aspects[i].name}/>                        
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
                        <select 
                            onChange={onChange}
                            data-k={i}
                            data-which={'year'}>
                            defaultValue={aspects[i].year}
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
                        <p>Columns</p>
                        <div>
                            {columnsJSX}
                        </div>
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
            