export const types={
    SELECT_GEOMETRY: 'SelectGeometry',
    SELECT_ASPECTS: 'SelectAspects'
};
// Helper functions to dispatch actions, optionally with payloads
export const actionCreators = {
    SelectGeometry: (geom) => {
        return({type: types.SELECT_GEOMETRY, payload:geom});
    },
    SelectAspects: (aspects) => {
        return({type: types.SELECT_ASPECTS, payload:aspects});
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
        default:
            return(state);
    }
}
