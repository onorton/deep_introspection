import React, { Component } from 'react';
import { Overlay, Tooltip, Position} from "@blueprintjs/core";

export default class UploadModelOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      isOpen: true,
      validArchitecture: true,
      validModel: true,
      validLabels: true,
    };
  }
  isValidFile(filename, type) {
    var parts = filename.split('.');
    const ext = parts[parts.length - 1];
    return ext.toLowerCase() == type
  }

  addArchitecture(file) {
    this.setState({validArchitecture: this.isValidFile(file.name,'prototxt')})
  }

  addModel(file) {
    this.setState({validModel: this.isValidFile(file.name,'caffemodel')})
  }
  addModel(file) {
    this.setState({validLabels: this.isValidFile(file.name,'txts')})
  }

  render(){
    return (
          <Overlay isOpen={this.state.isOpen} canEscapeKeyClose={true} onClose={() => this.setState({isOpen:false})}>
          <div className="pt-card pt-elevation-0" style={{width:500}}>
            <h3>Add Model</h3>
              <p>If this is the first time using Deep Introspection you need to upload a caffe model to analyse.</p>
              <label class="pt-label">
              <h5>Architecture File</h5>
              <p>This is the *.prototxt file that defines the architecture of the network.</p>
              {(this.state.validArchitecture) ? <div/>: <p style={{color:'#DB3737'}}>Must be a prototxt file.</p>}
              <label class="pt-file-upload">
              <input type="file" accept=".prototxt" onChange={(event) => this.addArchitecture(event.target.files[0])}/>
              <span class="pt-file-upload-input">Choose file...</span>
              </label>
            </label>
            <label class="pt-label">
            <h5>Weights File</h5>
            <p>This is the file containing the weights and biases of the network.</p>
            {(this.state.validModel) ? <div/>: <p style={{color:'#DB3737'}}>Must be a caffemodel file.</p>}
            <label class="pt-file-upload">
            <input type="file" accept=".caffemodel"/>
            <span class="pt-file-upload-input">Choose file...</span>
            </label>

          </label>
          <label class="pt-label">
          <h5>Class Labels </h5>
          <p>Class labels for the network. Though not required, it makes it easy to see what class the network recognises. This should be a file with a line for each class name.</p>
          {(this.state.validLabels) ? <div/>: <p style={{color:'#DB3737'}}>Must be a text file.</p>}
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
