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

export function dictEQ(a,b){
    if ((a===undefined)&&(b===undefined)){
        return(true);
    }
    if ((a===undefined)||(b===undefined)){
        return(false);
    }
    let ak=Object.keys(a);
    let bk=Object.keys(b);
    if (!arrayEQ(ak,bk)){
        return(false);
    }
    // for (let aa in ak){
    //     if (b[aa]!=a[aa]){
    //         return(false);
    //     }
    // }
    return(true);
}


export function toInt(d){
    return(parseInt(d,10));
}
