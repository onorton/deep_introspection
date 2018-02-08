import React, { Component } from 'react';
import { Tab2, Tabs2 } from "@blueprintjs/core";
export default class ToolCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
    }
  }

  render(){
    return (
    <Tabs2 id="toolTabs" onChange={this.handleTabChange}>
   <Tab2 id="oc" title="Occlusion" panel={<p>Occlusion panel</p>} />
   <Tab2 id="sy" title="Synthesis" panel={<p>Synthesis panel</p>}/>
   <Tabs2/>
</Tabs2>
    )
  }
}
