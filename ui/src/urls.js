const baseURL=()=>{
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
    SEGMENTATION : 'Segmentation',
    COUNTRY_OPTIONS : 'CountryOptions',
    PATH         : 'Path',
    REGION_DETAILS : 'RegionDetails',
    CREATE_ASPECT : 'CreateAspects',
    GET_ASPECTS : 'GetAspects',
    COMPARE_ASPECTS: 'GetAspectComparison',
    LEARN_PREDICTIONS: 'LearnPredictions'
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
    CountryOptions: () => {
        return(baseURL()+'availableCountries');
    },
    LearnPredictions: () => {
        return(baseURL()+'learnPredictions')
    },
    GetAspectComparison: () => {
        return(baseURL()+'getAspectComparison');
    },
    GetAspects: () => {
        return(baseURL()+'getAspects');
    },
    RegionDetails: (countryID,displayID) => {
        return(baseURL()+'getRegionDetails?countryID='+countryID+'&displayID='+displayID);
    },
    Upload: () => {
        return(baseURL()+'upload');
    },
    Path: () => {
        return(baseURL()+'getPath');
    },
    getUploadedData: () => {
        return(baseURL()+'getUploadedData');
    },
    createAspects: () => {
        return(baseURL()+'createAspects');
    },
    Segmentation: (country,vars,filters,weights) => {
        let args=[];
        if (country!==undefined){
            args.push('countryID='+country);
        }
        if (vars!==undefined){
            args.push('variables='+vars);
        }
        if (weights!==undefined){
            args.push('weights='+weights);
        }
        if (filters!==undefined){
            args.push('filters='+filters);
        }
        return(baseURL()+'getSegmentation?'+ args.join('&'));
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
