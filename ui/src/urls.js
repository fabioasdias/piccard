

const baseURL=()=>{
    return('http://192.168.2.99:8080/');
    return('http://localhost:8080/');
    // return('http://142.1.190.14/ct/');// clr
}


export const sendData=(url,data,callBackFcn)=>{
    fetch(url, {
        body: JSON.stringify(data), // must match 'Content-Type' header
        cache: 'no-cache', // *default, cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *omit
        headers: {
            'user-agent': 'Mozilla/4.0 MDN Example',
            'content-type': 'application/json'
        },
        method: 'POST', // *GET, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *same-origin
        redirect: 'follow', // *manual, error
        referrer: 'no-referrer', // *client
      }).then(
        ret => {
            ret.json().then((d)=> {//promise of a promise. really.
                callBackFcn(d);
            })
            
        },
        error => console.log('Error in fetching post')
    );
}
export const requestType ={
    AVAILABLE_GEOMETRIES : 'AvailableGeometries',
    AVAILABLE_ASPECTS : 'AvailableAspects',
    CREATE_ASPECTS : 'CreateAspects',
    GET_ASPECTS : 'GetAspects',
    GET_DATA : 'GetUploadedData',
    GET_RAW_DATA : 'GetRawData',
    MAP_HIERARCHIES: 'MapHierarchies',
    UPLOAD :'Upload'
};
export const getData = (url,actionThen) => {
    fetch(url)
    .then((response) => {
      if (response.status >= 400) {throw new Error("Bad response from server");}
      return response.json();
    })
    .then(actionThen);
}

export const getURL  = {
    AvailableGeometries: () => {
        return(baseURL()+'availableGeometries');
    },
    AvailableAspects: () => {
        return(baseURL()+'availableAspects');
    },
    MapHierarchies: () => {
        return(baseURL()+'mapHierarchies')
    },
    GetAspects: () => {
        return(baseURL()+'getAspects');
    },
    Upload: () => {
        return(baseURL()+'upload');
    },
    GetUploadedData: () => {
        return(baseURL()+'getUploadedData');
    },
    createAspects: () => {
        return(baseURL()+'createAspects');
    },
    GetRawData: () => {
        return(baseURL()+'getRawData')
    }
};

// export function requestPath(country,vars,filters,nodes) {
//     let args={};
//     if (country!==undefined){
//         args['countryID']=country;
//     }
//     if (vars!==undefined){
//         args['variables']=vars;
//     }
//     if (filters!==undefined){

//         args['filters']=filters;
//     }
//     if (nodes!==undefined){
//         args['nodes']=nodes;
//     }
//     return function (dispatch) {
//         return fetch(getURL.Path(), {
//             body: JSON.stringify(args), // must match 'Content-Type' header
//             cache: 'no-cache', // *default, cache, reload, force-cache, only-if-cached
//             credentials: 'same-origin', // include, *omit
//             headers: {
//             'user-agent': 'Mozilla/4.0 MDN Example',
//             'content-type': 'application/json'
//             },
//             method: 'POST', // *GET, PUT, DELETE, etc.
//             mode: 'cors', // no-cors, *same-origin
//             redirect: 'follow', // *manual, error
//             referrer: 'no-referrer', // *client
//           }).then(
//             path => {
//                 path.json().then((d)=> {//promise of a promise. really.
//                     dispatch(actionCreators.SetPath(d));
//                 })
//             },
//             error => console.log('ERRORRRRR')
//         );
//     }
// }
