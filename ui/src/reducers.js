import {getURL} from './urls';

export const types={
    SELECT_GEOMETRY: 'SelectGeometry',
    SELECT_ASPECTS: 'SelectAspects',
    UPDATE_CLUSTERING: 'UpdateClustering',
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
    }
  };

export const reducer = (state={aspects:[]}, action)=>{
    const { type, payload } = action;
    console.log(state, type, payload);
    switch (type){
        case types.SELECT_ASPECTS:
            return({...state, aspects:payload});
        case types.SELECT_GEOMETRY:
            return({...state, geometry:payload});
        case types.UPDATE_CLUSTERING:
            return({...state, similarity:payload.similarity, clustering:payload.clustering})
        default:
            return(state);
    }
}

export function requestClustering(aspects) {
    return function (dispatch) {
        return fetch(getURL.MapHierarchies(),  {
            body: JSON.stringify({aspects:aspects}), // must match 'Content-Type' header
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
                    dispatch(actionCreators.SelectAspects(aspects));
                    dispatch(actionCreators.UpdateClustering(d));
                })
            },
            error => console.log('ERRORRRRR')
        );
    }
}