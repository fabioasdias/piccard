import clone from '@turf/clone';

const baseURL=()=>{
    return('http://localhost:8080/');
    // return('http://142.1.190.14/ct/');// clr
}

export const selModes={
    SET:'Set',
    ADD:'Add',
    REMOVE: 'Remove'
}

export const types={
    UPDATE_MAP:'UpdateMap',
    UPDATE_DETAILS: 'UpdateDetails',
    SET_GEOJSON:'SetGeoJson',
    SET_SELMODE: 'SetSelectionMode',    
    SET_COUNTRY_OPTIONS: 'SetCountryOptions',
    SET_LEVEL: 'SetLevel',
    SET_REGION: 'SetRegion',
    SET_COUNTRY: 'SetCountry',
    SHOW_CONFIG: 'ShowConfig',
    SHOW_LOADING: 'ShowLoading',
    SHOW_DETAILS: 'ShowDetails',
    SET_TID: 'SetTID',
    CLEAR_TID: 'ClearTID',
    SET_PATH: 'SetPath',
    SET_COLOUR_OPT: 'SetColourOption'
};
// Helper functions to dispatch actions, optionally with payloads
export const actionCreators = {
    SetColourOption: opt =>{
        return {type: types.SET_COLOUR_OPT, payload: opt};
    },
    UpdateMap: segData => {
      return { type: types.UPDATE_MAP, payload: segData };
    },
    SetPath: path => {
      return { type: types.SET_PATH, payload: path};
    },
    SetTID: tID =>{
      return { type: types.SET_TID, payload: tID};
    },
    ClearTID: () =>{
        return { type: types.CLEAR_TID, payload: {}};
    },
    UpdateDetails: details => {
        return {type: types.UPDATE_DETAILS, payload: details};
    },
    SetGeoJson: gj => {
      return { type: types.SET_GEOJSON, payload: gj };
    },
    SetCountry: countryID => {
        return {type: types.SET_COUNTRY, payload: countryID};
    },
    SetLevel: level => {
        return {type: types.SET_LEVEL, payload:level};
    },
    SetRegion: rid => {
        return {type: types.SET_REGION, payload: rid};
    },
    SetCountryOptions: data => {
        return {type: types.SET_COUNTRY_OPTIONS, payload: data}
    },
    SetSelectionMode: (mode) => {
        return {type: types.SET_SELMODE, payload:mode}
    },
    ShowConfig: (show) => {
        return {type: types.SHOW_CONFIG, payload:show}
    },
    ShowLoading: (show) => {
        return {type: types.SHOW_LOADING, payload:show}
    },    
    ShowDetails: (show) => {
        return {type: types.SHOW_DETAILS, payload:show}
    },
    HideDetails: () => {
        return {type: types.HIDE_DETAILS, payload:{}}
    }
    
  };
function findTraj(colours, traj, chain, usedYears, val){
    for (let i=0; (i<traj.length); i++){
        let allEq=traj[i].chain.length===chain.length;
        for (let j=0;((allEq) &&(j<chain.length));j++){
            if ((traj[i].chain[j]!==chain[j])||(traj[i].years[j]!==usedYears[j]))
                allEq=false;
        }
        if (allEq) {            
            if (traj[i].colour===undefined){
                traj[i]={...traj[i],value:val,normal:'blue', faded:'lightgrey'};            
            }else{
                traj[i].value+=val;
            }
            return(i);
        }
    }
    return(undefined);
};

export const reducer = (state={
                                tID:[],
                                nids:{},
                                showLoading:true,
                                selMode:selModes.SET,
                                globalPath: true,
                            }, action)=>{
    const { type, payload } = action;
    console.log(state,type,payload);
    let tid;
    // console.log(payload);
    switch (type){
        case types.SET_GEOJSON:
            return({...state, gj:payload,origGJ:payload});

        case types.SET_COLOUR_OPT:
            return({...state, simpleColours:payload});

        case types.SET_PATH:
            return({...state, path: payload.paths, population:payload.population, globalPath:false});

        case types.CLEAR_TID:
            return({...state, globalPath:true, path: state.segData.basepath.paths, population:state.segData.basepath.population, tID:[], nids:{}});

        case types.SET_TID:            
            tid=state.tID.slice();
            let par=(Array.isArray(payload)?payload.slice():[payload,]);
            if (state.selMode===selModes.SET){
                tid=par;
            }
            if (state.selMode===selModes.ADD){
                tid=tid.concat(par);
            }
            if (state.selMode===selModes.REMOVE){
                tid=tid.filter((d)=>{return(!par.includes(d))});
            }
            let nids={};
            for (let i=0;i<tid.length;i++){
                for (let j=0;j<state.traj[tid[i]].nodes.length;j++){
                    nids[state.traj[tid[i]].nodes[j]]=true;
                }
            }

            return({...state, tID:tid,nids:nids});    

        case types.UPDATE_MAP:
            return({...state, nLevels:payload.levelCorr.length, segData:payload, tID:[], nids:{}, dsconf:payload.dsconf, basedata: payload.basepath, path:payload.basepath.paths, population:payload.basepath.population, conf:payload.conf, centroid:payload.centroid});

        case types.UPDATE_DETAILS:
            return({...state, details:payload});

        case types.SET_SELMODE:
            return({...state, selMode:payload});

        case types.SET_LEVEL:
            let colours;
            // console.log('set level',payload);
            if (state.segData.colours!==undefined){
                colours=state.segData.colours[payload];
            }

            let labels={};
            for (let y in state.segData.labels)
            {
                if (!labels.hasOwnProperty(y)){
                    labels[y]={};
                }
                for (let CTID in state.segData.labels[y]){
                    labels[y][CTID]=state.segData.levelCorr[payload][state.segData.labels[y][CTID]];
                }
            }

            let years;
            if (state.segData.years!==undefined){
                years=state.segData.years.map((d)=>{return(toInt(d));});
            }

            let gj={};
            for (let y in state.origGJ){
                console.log('redo map',y,)
                gj[y]=clone(state.origGJ[y]);
                for (let i=0; i< gj[y].features.length;i++){
                    let f=gj[y].features[i];
                    let c=getColour(colours,labels[y][f.properties.CT_ID])
                    if ((c===undefined)||(c===null)){
                        f.properties.colour='white';
                    }else{
                        f.properties.colour=c;
                    }
                    
                }
            }
            // let gj=clone(state.origGJ);
            let tchain;
            let traj=state.segData.traj[payload].slice();
            let usedYears;            
            let patt=state.segData.patt.filter( d=> (colours.hasOwnProperty(d.id)) );
            return({...state, 
                    colours: colours, 
                    patt: patt,
                    years:years,
                    labels: labels,
                    path:state.segData.basepath.paths,
                    pop:state.segData.basepath.population,
                    traj: traj,
                    gj: gj,
                    tID: [],
                    nids:{},
                    level: payload
                });
    

        case types.SET_REGION:
            return({...state, region:payload});

        case types.SET_COUNTRY_OPTIONS:
            return({...state, COUNTRYOptions: payload});

        case types.SET_COUNTRY:
            return({...state, countryID:payload});
            
        case types.SHOW_CONFIG:
            return({...state, showConfig:payload});
        case types.SHOW_DETAILS:
            return({...state, showDetails:payload});
        case types.SHOW_LOADING:
            return({...state, showLoading:payload});
        default:
            return(state);
    }
}


export const requestType ={
    SEGMENTATION : 'Segmentation',
    COUNTRY_OPTIONS : 'COUNTRYOptions',
    PATH         : 'Path',
    REGION_DETAILS : 'RegionDetails',
    GEO_JSON       : 'GeoJSON',
};

export function toInt(d){
    return(parseInt(d,10));
}

export const getURL  = {
    CountryOptions: () => {
        return(baseURL()+'availableCountries');
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
    },
    GeoJSON: (countryID) => {
        return(baseURL()+'getGJ?countryID='+countryID);
    }
};

export const getData = (url,actionThen) => {
    fetch(url)
    .then((response) => {
      if (response.status >= 400) {throw new Error("Bad response from server");}
      return response.json();
    })
    .then(actionThen);
}
export const getColour =(colours, id) => { //color brewer ftw
    return(getC(colours[id]));
  };
export const getC=(i)=>{
    ///let c8=['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffd651','#743b1b','#f781bf'];
    let c8=['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#e6ab02','#a6761d','#666666'];
    // let c8=['rgba(228, 26, 28, 200)', 'rgba(55, 126, 184, 200)', 'rgba(77, 175, 74, 200)', 'rgba(152, 78, 163, 200)',
    //   'rgba(255, 127, 0, 200)', 'rgba(255, 214, 81, 200)', 'rgba(116, 59, 27, 200)', 'rgba(247, 129, 191, 200)'];
    return(c8[i]);
}
export const getClass = (labels, year, did) => {
    try{
        return(labels[year][did]);
    }
    catch (e) {
        return(undefined);
    }
        
};

export function requestPath(country,vars,filters,nodes) {
    let args={};
    if (country!==undefined){
        args['countryID']=country;
    }
    if (vars!==undefined){
        args['variables']=vars;
    }
    if (filters!==undefined){

        args['filters']=filters;
    }
    if (nodes!==undefined){
        args['nodes']=nodes;
    }
    console.log('path',args)
    return function (dispatch) {
        return fetch(getURL.Path(), {
            body: JSON.stringify(args), // must match 'Content-Type' header
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
            path => {
                path.json().then((d)=> {//promise of a promise. really.
                    dispatch(actionCreators.SetPath(d));
                })
            },
            error => console.log('ERRORRRRR')
        );
    }
}