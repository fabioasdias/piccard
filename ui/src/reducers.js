import clone from '@turf/clone';

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
    ShowDetails: (show) => {
        return {type: types.SHOW_DETAILS, payload:show}
    },
    HideDetails: () => {
        return {type: types.HIDE_DETAILS, payload:{}}
    }
    
  };

export const reducer = (state={
                                tID:[],
                                nids:{},
                                selMode:selModes.SET,
                                globalPath: true,
                            }, action)=>{
    const { type, payload } = action;
    console.log(state,type,payload);
    let tid;
    // console.log(payload);
    switch (type){
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
            return({...state, CountryOptions: payload});

        case types.SET_COUNTRY:
            return({...state, countryID:payload, curCountryOptions:state.CountryOptions[payload]});
            
        case types.SHOW_CONFIG:
            return({...state, showConfig:payload});
        case types.SHOW_DETAILS:
            return({...state, showDetails:payload});
        default:
            return(state);
    }
}

export function toInt(d){
    return(parseInt(d,10));
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

