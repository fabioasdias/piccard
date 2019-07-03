import {getURL} from './urls';
import randomColor from 'randomcolor';


function makeColours(n){
    let colours=['#1b9e77','#d95f02','#7570b3','#e7298a','#66a61e','#e6ab02','#a6761d','#666666'];
    for (let i = colours.length; i<n;i++){
      colours.push(randomColor());
    }
    return(colours);

}

export const types={
    SELECT_GEOMETRY: 'SelectGeometry',
    SELECT_ASPECTS: 'SelectAspects',
    UPDATE_CLUSTERING: 'UpdateClustering',
    SELECT_PATHS: 'SelectPaths',
    START_LOADING: 'StartLoading',
};
// Helper functions to dispatch actions, optionally with payloads
export const actionCreators = {
    SelectGeometry: (geom) => {
        return({type: types.SELECT_GEOMETRY, payload:geom});
    },
    SelectAspects: (aspects) => {
        return({type: types.SELECT_ASPECTS, payload:aspects});
    },
    UpdateClustering: (clsim) => {
        return({type: types.UPDATE_CLUSTERING, payload:clsim})
    },
    SelectPaths: (selected) => {
        return({type: types.SELECT_PATHS, payload:selected})
    },
    StartLoading: ()=>{
        return({type: types.START_LOADING});
    }
  };

export const reducer = (state={aspects:[], selectedPaths:[], loading:true}, action)=>{
    const { type, payload } = action;
    console.log(state, type, payload);
    switch (type){
        case types.SELECT_ASPECTS:
            return({...state, aspects:payload});
        case types.SELECT_GEOMETRY:
            return({...state, geometry:payload});
        case types.START_LOADING:
            return({...state, loading:true});
        case types.UPDATE_CLUSTERING:
            return({...state, 
                    colours: makeColours(payload.nclusters),
                    temporal:{aspects:payload.aspects,evolution:payload.evolution}, 
                    aspect_info: payload.aspects,
                    clustering:payload.clustering,
                    aspect_hist:payload.aspect_hist,
                    path_hist:payload.path_hist,
                    loading:false})
        case types.SELECT_PATHS:
            return({...state, selectedPaths:payload});
        default:
            return(state);
    }
}

export function requestClustering(aspects,bbox) {
    let args={aspects:aspects,bbox:bbox};

    if (bbox!==undefined){
        args.bbox=bbox;
    }
    
    return function (dispatch) {
        // dispatch(actionCreators.StartLoading());
        return fetch(getURL.MapHierarchies(),  {
            // must match 'Content-Type' header
            body: JSON.stringify(args), 
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
            data => {
                data.json().then((d)=> {//promise of a promise. really.
                    console.log('hier full results',d);
                    dispatch(actionCreators.SelectAspects(aspects));
                    dispatch(actionCreators.UpdateClustering(d));
                })
            },
            error => console.log('ERRORRRRR')
        );
    }
}