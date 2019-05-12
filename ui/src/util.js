export function arrayEQ(a,b){
    if ((a===undefined)&&(b===undefined)){
        return(true);
    }
    if ((a===undefined)||(b===undefined)){
        return(false);
    }
    if (a.length!==b.length){
        return(false)
    }
    for (let aa of a){
        if (!b.includes(aa)){
        return(false);
        }
    }
    return(true);
}


export function toInt(d){
    return(parseInt(d,10));
}
