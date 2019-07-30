
//https://github.com/uber/react-vis/blob/master/showcase/examples/force-directed-graph/force-directed-graph.js


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
import PropTypes from 'prop-types';
import {forceSimulation, forceLink, forceManyBody, forceCenter, forceY, forceX} from 'd3-force';

import {XYPlot, MarkSeries, LineSeries} from 'react-vis';

/**
 * Create the list of nodes to render.
 * @returns {Array} Array of nodes.
 * @private
 */
function generateSimulation(props) {
  const {data, height, width, strength} = props;
  if (!data) {
    return {nodes: [], links: []};
  }
  // copy the data
  let nodes = data.nodes.map(d => ({...d}));//, 'x':d.ideal_x*width, 'y':d.ideal_y*height}));
  let links = data.links.map(d => ({...d})).filter(({source,target})=>{
    return((nodes[source].cc===nodes[target].cc)||(nodes[source].year===nodes[target].year));
  });
  let all_links = data.links.slice();
  console.log('copy links',links);
  let ticked= () => {
    for (let i=0;i<nodes.length;i++){
      nodes[i].y=nodes[i].ideal_y;
    }
  }

  // build the simulation
  const simulation = forceSimulation(nodes)
    .force('link', forceLink())
    .force('charge', forceManyBody())
    .force('yAxis', forceY(d=>(+d.ideal_y)*height))
    // .force('xAxis', forceX(d=>(+d.ideal_x)*width).strength(0.1))
    .force('center', forceCenter(width / 2, height / 2))
    .on('tick',ticked)
    .stop();


  const upperBound = Math.ceil(
    Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay())
  );
  
  simulation.force('link').links(links);
  simulation.tick(upperBound);
  ticked();
  all_links=all_links.sort((a,b)=>{
    return(a.weight-b.weight);
  });

  return({nodes, links, all_links});
}

class ForceDirectedGraph extends React.Component {
  static get defaultProps() {
    return {
      className: '',
      data: {nodes: [], links: []},
      strength:0.05
    };
  }

  static get propTypes() {
    return {
      className: PropTypes.string,
      data: PropTypes.object.isRequired,
      height: PropTypes.number.isRequired,
      width: PropTypes.number.isRequired,
    };
  }

  constructor(props) {
    super(props);
    this.state = {
      data: generateSimulation(props)
    };
  }

  componentWillReceiveProps(nextProps) {
    this.setState({
      data: generateSimulation(nextProps)
    });
  }

  render() {
    const {className, height, width} = this.props;
    let {nodes, links, all_links} = this.state.data;
    return (
      <XYPlot width={width} height={height} className={className}>
        {all_links.map(({source, target}, index) => {
          let linkData=[{'x':nodes[source].x, 'y':nodes[source].y}, 
                        {'x':nodes[target].x, 'y':nodes[target].y}];
          if (nodes[source].year!==nodes[target].year){
            return (
              <LineSeries
                colorType={'literal'}
                key={`link-${index}`}
                opacity={0.75}
                color={(nodes[source].cc===nodes[target].cc)?this.props.colours[nodes[source].cc]:'lightgray'}
                strokeWidth={5*all_links[index].weight}
                data={linkData}
              />
            );
          }else{
            console.log(source,target);
            return(null);
          }

        })}
        <MarkSeries
          data={nodes.map((d)=>{
            return({...d,color:this.props.colours[d.cc]});
          })}
          colorType={'literal'}
          stroke={'#ddd'}
          strokeWidth={2}
        />
      </XYPlot>
    );
  }
}

ForceDirectedGraph.displayName = 'ForceDirectedGraph';

export default ForceDirectedGraph;
