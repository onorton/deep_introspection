import React, { Component } from 'react';
import { Overlay, Tooltip, Position} from "@blueprintjs/core";

export default class UploadModelOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      isOpen: true,
      validArchitecture: false,
      validModel: true,
      validLabels: true,
    };
  }

  render(){
    return (
          <Overlay isOpen={this.state.isOpen} canEscapeKeyClose={true} onClose={() => this.setState({isOpen:false})}>
          <div className="pt-card pt-elevation-0" style={{width:500}}>
            <h3>Add Model</h3>
              <p>If this is the first time using Deep Introspection you need to upload a caffe model to analyse.</p>
              <label class="pt-label">
              <h5>Architecture File</h5>
              {(this.state.validArchitecture) ? <br/> : <div/>}
              <p>This is the *.prototxt file that defines the architecture of the network.</p>
              {(this.state.validArchitecture) ? <div/>: <p style={{color:'#DB3737'}}>Must be a prototxt file.</p>}
              <label class="pt-file-upload">
              <input type="file" accept=".prototxt"/>
              <span class="pt-file-upload-input">Choose file...</span>
              </label>
            </label>
            <label class="pt-label">
            <h5>Weights File</h5>
            <p>This is the file containing the weights and biases of the network.</p>
            <label class="pt-file-upload">
            <input type="file" accept=".caffemodel"/>
            <span class="pt-file-upload-input">Choose file...</span>
            </label>

          </label>
          <label class="pt-label">
          <h5>Class Labels </h5>
          <p>Class labels for the network. Though not required, it makes it easy to see what class the network recognises. This should be a file with a line for each class name.</p>
          <label class="pt-file-upload">
          <input type="file" accept=".txt"/>
          <span class="pt-file-upload-input">Choose file...</span>
          </label>
        </label>
        <button type="button" className="pt-button pt-icon-add">Upload Model</button>
              </div>
          </Overlay>
    );
  }
}
