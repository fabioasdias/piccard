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

const predefinedClassName = 'rv-xy-plot__series rv-xy-plot__series--boxplot';

class BoxplotSeries extends AbstractSeries {
  render() {
    const {className, data, marginLeft, marginTop, doMinMax} = this.props;
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
      distance=15;
    }

    return (
      <g className={`${predefinedClassName} ${className}`}
         ref="container"
         transform={`translate(${marginLeft},${marginTop})`}>
        {data.map((d, i) => {
          const xTrans = xFunctor(d);
          const yMax = yFunctor({...d, y: d.yMax});
          const yQ3 = yFunctor({...d, y: d.yQ3});
          const yQ1 = yFunctor({...d, y: d.yQ1});
          const yMin = yFunctor({...d, y: d.yMin});
          let cstroke=strokeFunctor && strokeFunctor(d);

          const lineAttrs = {
            stroke: cstroke
          };

          let op=opacityFunctor ? opacityFunctor(d) : 1;
          let xWidth;
          if (op<1){
            xWidth = distance * 2;
          }else{
            xWidth = 0.75*(distance * 2);
          }

          
          return (
            <g
              transform={`translate(${xTrans})`}
              opacity={op}
              key={i}
              stroke={'grey'}
              onClick={e => this._valueClickHandler(d, e)}
              onMouseOver={e => this._valueMouseOverHandler(d, e)}
              onMouseOut={e => this._valueMouseOutHandler(d, e)}>
              {doMM?<line x1={0} x2={0} y1={yMax} y2={yMin} {...lineAttrs} />:null}
              <rect
                x={-xWidth}
                width={Math.max(xWidth * 2, 0)}
                y={yQ3}
                height={Math.abs(yQ3 - yQ1)}
                fill={fillFunctor && fillFunctor(d)} />
                {doMM?<line x1={-xWidth} x2={xWidth} y1={yMax} y2={yMax} {...lineAttrs} />:null}
                {doMM?<line x1={-xWidth} x2={xWidth} y1={yMin} y2={yMin} {...lineAttrs} />:null}
            </g>);
        })}
      </g>
    );
  }
}

BoxplotSeries.displayName = 'BoxplotSeries';

export default BoxplotSeries;
