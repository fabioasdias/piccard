import chroma from 'chroma-js';
import clone from '@turf/clone';

const baseURL=()=>{
    return('http://localhost:8080/');
    return('http://142.1.190.14/ct/');// clr
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
    SET_CITY_OPTIONS: 'SetCityOptions',
    SET_LEVEL: 'SetLevel',
    SET_REGION: 'SetRegion',
    SET_CITY: 'SetCity',
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
    SetCity: cityID => {
        return {type: types.SET_CITY, payload: cityID};
    },
    SetLevel: level => {
        return {type: types.SET_LEVEL, payload:level};
    },
    SetRegion: rid => {
        return {type: types.SET_REGION, payload: rid};
    },
    SetCityOptions: data => {
        return {type: types.SET_CITY_OPTIONS, payload: data}
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
                let c=mixColours(colours,chain);
                traj[i]={...traj[i],value:val,colour: c,normal:c, faded:'lightgrey',simplified:mixSimplified(colours,chain)};            
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
                                showLoading:true,
                                selMode:selModes.SET,
                                simpleColours:true,
                                globalPath: true,
                            }, action)=>{
    const { type, payload } = action;
    // console.log(state);
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
            return({...state, globalPath:true, path: state.segData.basepath.paths, population:state.segData.basepath.population, tID:[]});

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
            return({...state, tID:tid});    

        case types.UPDATE_MAP:
            return({...state, nLevels:payload.levelCorr.length, segData:payload, tID:[], dsconf:payload.dsconf, basedata: payload.basepath, path:payload.basepath.paths, population:payload.basepath.population, conf:payload.conf, centroid:payload.centroid});

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
            for (let d of state.segData.labels)
            {
                if (!labels.hasOwnProperty(d.year)){
                    labels[d.year]={};
                }
                labels[d.year][d.did]=state.segData.levelCorr[payload][d.id];
            }

            let years;
            if (state.segData.years!==undefined){
                years=state.segData.years.map((d)=>{return(toInt(d));});
            }
            
            let gj=clone(state.origGJ);
            let tchain;
            let traj=state.segData.traj[payload].slice();
            let usedYears;
            if ((years!==undefined) && (state.gj !== undefined)) {
                for (let feat of gj.features){
                    tchain=[];
                    usedYears=[];
                    for (let y of years){
                        let cClass=labels[y][feat.properties.display_id];
                        if (cClass!==undefined){
                            tchain.push(labels[y][feat.properties.display_id]);
                            usedYears.push(y);
                        }
                    }
                    feat.properties.chain=tchain;                              
                    tid=findTraj(colours,traj,tchain,usedYears,parseFloat(feat.properties.area));
                    feat.properties.tID=tid;
                    for (let y of years){
                        feat.properties[y.toString()]='rgba(0,0,0,0)';
                    }
                
                    if (tid!==undefined){
                        for (let i=0;i<tchain.length;i++){
                            feat.properties[usedYears[i]]=getColour(colours,tchain[i]);
                        }
                        feat.properties.colour=traj[tid].colour;
                        feat.properties.normal=traj[tid].colour;
                        feat.properties.faded=traj[tid].faded;    
                        feat.properties.simplified=traj[tid].simplified;
                    }
                    else{
                        feat.properties.colour='rgba(0,0,0,0)';
                        feat.properties.normal='rgba(0,0,0,0)';
                        feat.properties.faded='rgba(0,0,0,0)';
                        feat.properties.simplified='rgba(0,0,0,0)';
                    }
                }
            }
            
            let patt=state.segData.patt.filter( d=> (colours.hasOwnProperty(d.id)) );
            return({...state, 
                    colours: colours, 
                    patt: patt,
                    years:years,
                    labels: labels,
                    path:state.segData.basepath.paths,
                    pop:state.segData.basepath.population,
                    traj: traj,
                    NbyTID: state.segData.nodesByTID[payload],
                    gj: gj,
                    tID: [],
                    level: payload
                });
    

        case types.SET_REGION:
            return({...state, region:payload});

        case types.SET_CITY_OPTIONS:
            return({...state, cityOptions: payload});

        case types.SET_CITY:
            return({...state, cityID:payload});
            
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
    CITY_OPTIONS : 'CityOptions',
    PATH         : 'Path',
    REGION_DETAILS : 'RegionDetails',
    GEO_JSON       : 'GeoJSON',
};

export function toInt(d){
    return(parseInt(d,10));
}

export const getURL  = {
    CityOptions: () => {
        return(baseURL()+'availableCities');
    },
    RegionDetails: (cityID,displayID) => {
        return(baseURL()+'getRegionDetails?cityID='+cityID+'&displayID='+displayID);
    },
    Path: () => {
        return(baseURL()+'getPath');
    },
    Segmentation: (city,vars,filters,weights,k) => {
        let args=[];
        if (city!==undefined){
            args.push('cityID='+city);
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
        // if (k!==undefined){
        args.push('k=2');
        // }
        return(baseURL()+'getSegmentation?'+ args.join('&'));
    },
    GeoJSON: (cityID) => {
        return(baseURL()+'getGJ?cityID='+cityID);
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

export function requestPath(city,vars,filters,nodes) {
    let args={};
    if (city!==undefined){
        args['cityID']=city;
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



function mixSimplified(colours, ids){
    let unique = (arrArg) => arrArg.filter((elem, pos, arr) => arr.indexOf(elem) === pos);

    let c=ids.filter((d)=>{return(d!==undefined);});
    if (c.length<3){
        return('lightgrey');
    }

    let u=unique(c);
    if (u.length===1){
        return(getColour(colours,u[0]))
    }
    for (let cU of u){
        let count=0;
        for (let i=0;i<c.length;i++){
            count+=(c[i]===cU)
        }
        if (count>(c.length/2)){
            return(chroma(getColour(colours,cU)).saturate(2).brighten().hex());    
        }    
    }
    return('darkgrey');

}

function mixColours(colours, ids){
    let c=ids.filter((d)=>{return(d!==undefined);}).map((d)=>{return(getColour(colours,d))});
    if (c.length>0){
        let ret=chroma.average(c,'lab');
        return(ret.hex());
    }else{
        return('none');
    }
}
