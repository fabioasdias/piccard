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

import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {scaleLinear} from 'd3-scale';
import {format} from 'd3-format';
import './parcor.css';

import {DISCRETE_COLOR_RANGE} from 'react-vis/dist/theme';
import {
  MarginPropType,
  getInnerDimensions,
  DEFAULT_MARGINS
} from 'react-vis/dist/utils/chart-utils';
import {XYPlot, LineSeries, LineMarkSeries, LabelSeries, DecorativeAxis,Highlight} from 'react-vis';

const predefinedClassName = 'rv-parallel-coordinates-chart';
const DEFAULT_FORMAT = format('.2r');
/**
 * Generate axes for each of the domains
 * @param {Object} props
 - props.animation {Boolean}
 - props.domains {Array} array of object specifying the way each axis is to be plotted
 - props.style {object} style object for the whole chart
 - props.tickFormat {Function} formatting function for axes
 * @return {Array} the plotted axis components
 */
function getAxes(props) {
  const {animation, domains, style, tickFormat} = props;
  return domains.map((domain, index) => {
    const sortedDomain = domain.domain;

    const domainTickFormat = t => {
      return domain.tickFormat ? domain.tickFormat(t) : tickFormat(t);
    };

    return (
      <DecorativeAxis
        animation={animation}
        key={`${index}-axis`}
        axisStart={{y: domain.name, x: 0}}
        axisEnd={{y: domain.name, x: 1}}
        axisDomain={sortedDomain}
        numberOfTicks={domain.cols.length}
        tickValue={domainTickFormat}
      />
    );
  });
}

/**
 * Generate labels for the ends of the axes
 * @param {Object} props
 - props.domains {Array} array of object specifying the way each axis is to be plotted
 - props.style {object} style object for just the labels
 * @return {Array} the prepped data for the labelSeries
 */
function getLabels(props) {
  const {domains, style} = props;
  let ret=[];
  for (let i=0;i<domains.length;i++){
    let domain=domains[i];
    ret.push({
      y: domain.name,
      x: 1.05,
      label: domain.label,
      yOffset: -10,
      // rotation: -20,
      style:{...style, textAnchor:'end', dominantBaseline: 'text-after-edge'}
    });
    ret.push({
      y: domain.name,
      x: 1.05,
      label: domain.year.toString(),
      yOffset: +10,
      style:{...style, textAnchor:'end', dominantBaseline: 'text-after-edge', fontSize:12}
    });

  }
  return(ret);
}

/**
 * Generate "sub" labels for the ends of the axes
 * @param {Object} props
 - props.domains {Array} array of object specifying the way each axis is to be plotted
 - props.style {object} style object for just the labels
 * @return {Array} the prepped data for the labelSeries
 */
function getSubLabels(props) {
  const {domains, style, width} = props;
  let ret=[];
  for (let i=0;i<domains.length;i++){
    let N = domains[i].cols.length;
    if (N*50 < width){
      for (let j=0;j<N;j++){
        ret.push({
          x: (j+0.5)/N,
          y: domains[i].name,
          label: domains[i].descr[domains[i].cols[j]].slice(0,20),
          style:{...style, 
                 fill: 'black',
                 stroke:'white',
                 strokeWidth:0.1,
                 textAnchor:'middle', 
                 fontSize:8,
                 dominantBaseline: (j%2===0)?'text-after-edge':'text-before-edge'}
                 
        });
      }  
    }
  }
  return(ret);
}


/**
 * Generate the actual lines to be plotted
 * @param {Object} props
 - props.animation {Boolean}
 - props.data {Array} array of object specifying what values are to be plotted
 - props.domains {Array} array of object specifying the way each axis is to be plotted
 - props.style {object} style object for the whole chart
 - props.showMarks {Bool} whether or not to use the line mark series
 * @return {Array} the plotted axis components
 */
function getLines(props) {
  const {
    animation,
    brushFilters,
    colorRange,
    domains,
    data,
    style,
    showMarks
  } = props;
  const scales = domains.reduce((acc, {domain, name}) => {
    acc[name] = scaleLinear()
      .domain(domain)
      .range([0, 1]);
    return acc;
  }, {});
  // const

  return data.map((row, rowIndex) => {
    let withinFilteredRange = true;
    const mappedData = domains.filter((domain)=>{
        const {getValue, name, visible} = domain;
        let xVal = scales[name](getValue ? getValue(row) : row[name]);
        if ((brushFilters.hasOwnProperty(name))&&(brushFilters[name]!==null)&&(xVal<0)){
          withinFilteredRange=false;
        }
        return((visible)&&(xVal>=0));
      }).map((domain, index) => {
        const {getValue, name} = domain;

        // xVal after being scale is in [0, 1] range
        const xVal = scales[name](getValue ? getValue(row) : row[name]);
        const filter = brushFilters[name];
        // filter value after being scale back from pixel space is also in [0, 1]
        if (filter && (xVal < filter.min || xVal > filter.max)) {
          withinFilteredRange = false;
        }
        return {y: name, x: xVal};
      });
    const selectedName = `${predefinedClassName}-line`;
    const unselectedName = `${selectedName} ${predefinedClassName}-line-unselected`;
    const lineProps = {
      animation,
      className: withinFilteredRange ? selectedName : unselectedName,
      key: `${rowIndex}-polygon`,
      data: mappedData,
      color: row.color || colorRange[rowIndex % colorRange.length],
      style: {...style.lines, ...(row.style || {})}
    };
    if (!withinFilteredRange) {
      lineProps.style = {
        ...lineProps.style,
        ...style.deselectedLineStyle
      };
    }
    return (showMarks&&withinFilteredRange) ? (
      <LineMarkSeries {...lineProps} />
    ) : (
      <LineSeries {...lineProps} />
    );
  });
}

class ParallelCoordinates extends Component {
  state = {
    brushFilters: {},
  };

  render() {
    const {brushFilters} = this.state;
    const {
      animation,
      brushing,
      className,
      children,
      colorRange,
      data,
      domains,
      height,
      hideInnerMostValues,
      margin,
      onMouseLeave,
      onMouseEnter,
      showMarks,
      style,
      tickFormat,
      width
    } = this.props;

    const axes = getAxes({
      domains,
      animation,
      hideInnerMostValues,
      style,
      tickFormat
    });

    const lines = getLines({
      animation,
      brushFilters,
      colorRange,
      domains,
      data,
      showMarks,
      style
    });
    const labelSeries = (
      <LabelSeries
        animation
        key={className}
        className={`${predefinedClassName}-label`}
        data={getLabels({domains, style: style.labels})}
      />
    );
    const subLabelsSeries = (
      <LabelSeries
        animation
        key={'sub'+className}
        className={`${predefinedClassName}-sublabel`}
        data={getSubLabels({domains, style: style.labels, width})}
      />
    );

    const {marginTop, marginBottom} = getInnerDimensions(
      this.props,
      DEFAULT_MARGINS
    );
    return (
      <XYPlot
        height={height}
        width={width}
        margin={margin}
        dontCheckIfEmpty
        className={`${className} ${predefinedClassName}`}
        onMouseLeave={onMouseLeave}
        onMouseEnter={onMouseEnter}
        yType="ordinal"
        xDomain={[0, 1]}
      >
        {children}
        {axes.concat(lines).concat(labelSeries).concat(subLabelsSeries)}
        {brushing &&
          domains.map(d => {
            const trigger = (row) => {
              let filters={
                ...brushFilters,
                [d.name]: row ? {min: row.left, max: row.right} : null
              }
              if (this.props.highlightCallback!==undefined){
                let selected=this.props.data.slice();
                for (let k in filters){
                  if (filters[k]){
                    selected=selected.filter((e)=>{
                      return((e[k]>=filters[k].min)&&(e[k]<=filters[k].max));
                    });  
                  }
                }
                this.props.highlightCallback(selected.map((d) => d.id));
              }
              this.setState({
                brushFilters: filters
              });
            };
            return (
              <Highlight
                key={d.name}
                highlightY={d.name}
                onBrushEnd={trigger}
                onDragEnd={trigger}
                highlightHeight={
                  (height - marginTop - marginBottom) / domains.length
                }
                enableY={false}
              />
            );
          })}
      </XYPlot>
    );
  }
}

ParallelCoordinates.displayName = 'ParallelCoordinates';
ParallelCoordinates.propTypes = {
  brushing: PropTypes.bool,
  className: PropTypes.string,
  colorType: PropTypes.string,
  colorRange: PropTypes.arrayOf(PropTypes.string),
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
  domains: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      domain: PropTypes.arrayOf(PropTypes.number).isRequired,
      tickFormat: PropTypes.func
    })
  ).isRequired,
  height: PropTypes.number.isRequired,
  margin: MarginPropType,
  style: PropTypes.shape({
    axes: PropTypes.object,
    labels: PropTypes.object,
    lines: PropTypes.object
  }),
  showMarks: PropTypes.bool,
  tickFormat: PropTypes.func,
  width: PropTypes.number.isRequired
};
ParallelCoordinates.defaultProps = {
  className: '',
  colorType: 'category',
  colorRange: DISCRETE_COLOR_RANGE,
  style: {
    axes: {
      line: {stroke:'grey'},
      ticks: {},
      text: {}
    },
    labels: {
    },
    lines: {
      strokeWidth: 1,
      strokeOpacity: 1
    },
    deselectedLineStyle: {
      strokeOpacity: 0.1
    }
  },
  tickFormat: DEFAULT_FORMAT
};

export default ParallelCoordinates;
