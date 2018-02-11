import React, { Component } from 'react';
import {MainToaster} from '../MainToaster.js'
import {Intent} from "@blueprintjs/core";

export default class BoundaryTool extends Component {

  constructor(props) {
    super(props);
    this.state = {
      firstClass: null,
      secondClass: null
    };
  }
  generate() {
    if (this.state.firstClass == null || this.state.secondClass == null) {
      MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "You have not chosen two classes."})
      return;
    }
  }
  render(){
    return (
    <div className="toolArea" style={{float: "left"}}>
    <button type="button" className="pt-button pt-intent-primary" onClick={() => this.generate()}>Generate</button>
    </div>
    )
  }
}
