import React, { Component } from 'react';
import './upload.css';
import FileUploadProgress  from 'react-fileupload-progress';
//https://www.npmjs.com/package/react-fileupload-progress
import {getURL} from './reducers';
// import ConfigWeights from './configWeights';

class Upload extends Component {
    render(){
        return(
            <div className="upload">
                Upload a new data file:
                <FileUploadProgress key='fup' url={getURL.Upload()}
                    // onProgress={(e, request, progress) => {
                    //     console.log('progress', e, request, progress);
                    // }}
                    onLoad={ (e, request) => {
                        let data=JSON.parse(e.target.response);
                        console.log(data);

                        // let errorList='';
                        // for (let v in data.status){
                        //     if (parseInt(data.status[v],10)===-1){
                        //         if (errorList!==''){
                        //             errorList=errorList+','
                        //         }
                        //         errorList=errorList+' '+v;
                        //     }
                        // }
                        // if (errorList!==''){
                        //     alert('The following files could not be imported: '+errorList);
                        // }else{
                        //     this.setState({showPicker:false,id:data.id});                            
                        // }
                        // getData(getURL.TemporaryTables(data.id),(TT)=>{
                        //     this.setState({tables:TT});
                        // })                        
                    }}
                    onError={ (e, request) => {console.log('error', e, request);}}
                    onAbort={ (e, request) => {console.log('abort', e, request);}}
            />
        </div>
        );
    }
}

export default Upload;
            