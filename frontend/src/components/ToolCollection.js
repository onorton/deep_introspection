import React, { Component } from 'react';
import { Tab2, Tabs2 } from "@blueprintjs/core";
import OcclusionTool from './OcclusionTool'
export default class ToolCollection extends Component {

  render(){
    return (
    <Tabs2 id="toolTabs" onChange={this.handleTabChange} style={this.props.style}>
   <Tab2 id="oc" title={<h5>Occlusion</h5>} panel={<OcclusionTool testImage={this.props.testImage}/>} />
   <Tab2 id="sy" title={<h5>Synthesis</h5>} panel={<p>Synthesis panel</p>}/>
   <Tabs2/>
</Tabs2>
    )
  }
}
