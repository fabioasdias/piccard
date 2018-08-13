// Copyright (c) 2016 - 2017 Uber Technologies, Inc.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

import React from 'react';

import {AbstractSeries} from 'react-vis';

const predefinedClassName = 'horbox';

class BoxplotSeries extends AbstractSeries {
  render() {
    const {className, data, marginLeft, marginTop, doMinMax, xDomain} = this.props;
    if (!data) {
      return null;
    }
    let doMM=(doMinMax===undefined)||(doMinMax===true);

    const xFunctor = this._getAttributeFunctor('x');
    const yFunctor = this._getAttributeFunctor('y');
    const strokeFunctor = this._getAttributeFunctor('stroke') ||
      this._getAttributeFunctor('color');
    const fillFunctor = this._getAttributeFunctor('fill') ||
      this._getAttributeFunctor('color');
    const opacityFunctor = this._getAttributeFunctor('opacity');

    let distance;
    if (data.length>1) {
      distance=Math.abs(xFunctor(data[1]) - xFunctor(data[0])) * 0.2;
    }else{
      distance=10;
    }

    let _X=(dx)=>{
      return(xFunctor({x:dx}));
    }

    return (
      <g className={`${predefinedClassName} ${className}`}
         ref="container"
         transform={`translate(${marginLeft},${marginTop})`}>
        {data.map((d, i) => {
          //const yTrans = yFunctor(d);
          const xMax = xFunctor({...d, x: d.max});
          const xQ3 = xFunctor({...d, x: d.Q3});
          const xQ1 = xFunctor({...d, x: d.Q1});
          const xMin = xFunctor({...d, x: d.min});
          let cstroke=strokeFunctor && strokeFunctor(d);

          const lineAttrs = {
            stroke: cstroke
          };

          let op=opacityFunctor ? opacityFunctor(d) : 1;
          let yWidth= distance * 1.5;
          if (op===1){
            yWidth = 0.75*yWidth;
          }
          
          return (
            <g
              transform={`translate(-13,0)`}
              opacity={op}
              key={i}
              stroke={'grey'}
              onClick={e => this._valueClickHandler(d, e)}
              onMouseOver={e => this._valueMouseOverHandler(d, e)}
              onMouseOut={e => this._valueMouseOutHandler(d, e)}>
              <line  x1={_X(xDomain[0])} x2={_X(xDomain[1])} y1={0} y2={0} stroke='darkgray' strokeDasharray="5,5" />
              <line  x1={_X(0)} x2={_X(0)} y1={-2*yWidth} y2={2*yWidth} stroke='darkgray' strokeDasharray="5,5" />
              <line  x1={_X(0.25)} x2={_X(0.25)} y1={-2*yWidth} y2={2*yWidth} stroke='darkgray' strokeDasharray="5,5" />
              <line  x1={_X(0.5)} x2={_X(0.5)} y1={-2*yWidth} y2={2*yWidth} stroke='darkgray' strokeDasharray="5,5" />
              <line  x1={_X(0.75)} x2={_X(0.75)} y1={-2*yWidth} y2={2*yWidth} stroke='darkgray' strokeDasharray="5,5" />
              <line  x1={_X(1)} x2={_X(1)} y1={-2*yWidth} y2={2*yWidth} stroke='darkgray' strokeDasharray="5,5" />

              {doMM?<line x1={xMax} x2={xMin} y1={0} y2={0} {...lineAttrs} />:null}
              <rect
                y={-yWidth}
                height={Math.max(yWidth * 2, 0)}
                x={xQ1}
                width={Math.abs(xQ3 - xQ1)}
                fill={fillFunctor && fillFunctor(d)} />
                {doMM?<line y1={-yWidth} y2={yWidth} x1={xMax} x2={xMax} {...lineAttrs} />:null}
                {doMM?<line y1={-yWidth} y2={yWidth} x1={xMin} x2={xMin} {...lineAttrs} />:null}
            </g>);
        })}
      </g>
    );
  }
}

BoxplotSeries.displayName = 'BoxplotSeries';

export default BoxplotSeries;
