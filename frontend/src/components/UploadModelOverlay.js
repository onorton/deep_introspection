import React, { Component } from 'react';
import { Overlay, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'

const blobSize = 5242880

export default class UploadModelOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      isOpen: true,
      validArchitecture: true,
      architecture: null,
      validModel: true,
      model: null,
      validLabels: true,
      labels: null
    };
  }
  isValidFile(filename, type) {
    var parts = filename.split('.');
    const ext = parts[parts.length - 1];
    return ext.toLowerCase() == type
  }

  addArchitecture(file) {
    this.setState({validArchitecture: this.isValidFile(file.name,'prototxt')})
    if (this.state.validArchitecture) {
      this.setState({architecture: file})
    }
  }

  addModel(file) {
    this.setState({validModel: this.isValidFile(file.name,'caffemodel')})
    if (this.state.validModel) {
      this.setState({model: file})
    }
  }
  addLabels(file) {
    this.setState({validLabels: this.isValidFile(file.name,'txt')})
    if (this.state.validLabels) {
      this.setState({labels: file})
    }
  }

  upload() {

      if (this.state.architecture == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No architecture file uploaded." });
        return
      }
      if (this.state.model == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No weights file uploaded." });
        return
      }
      let overlay = this

      // Send request to backend
      let numBlobs = Math.floor(this.state.model.size/blobSize)+1
      for (var i = 0; i < numBlobs; i++) {
        (function(file, i) {
        var reader = new FileReader();
        reader.readAsDataURL(overlay.state.model.slice(i*blobSize,(i+1)*blobSize));
        reader.onload = function () {
        // If successfully read file, save on file system
        fetch('http://127.0.0.1:8000/uploadModel/', {
          method: 'POST',
          body: JSON.stringify({name: overlay.state.model.name, part: reader.result, blobNum: i, blobMax: numBlobs-1}),
          headers: {
              "Content-Type": "application/json"
          }
        }).then(function(response) {
          return response.json();
        }).catch(function(error) {
          console.log('There has been a problem with your fetch operation: ' + error.message);
        });
        };
      reader.onerror = function (error) {
       console.log('Error: ', error);
      };
    })(this.state.model.slice(i*blobSize,(i+1)*blobSize), i)
      }

  }

  render(){
    return (
          <Overlay isOpen={this.state.isOpen} canEscapeKeyClose={true} onClose={() => this.setState({isOpen:false})}>
          <div className="pt-card pt-elevation-0" style={{width:500}}>
            <h3>Add Model</h3>
              <p>Before using Deep Introspection, you need to upload a caffe model to analyse.</p>
              <label class="pt-label">
              <h5>Architecture File</h5>
              <p>This is the *.prototxt file that defines the architecture of the network.</p>
              {(this.state.validArchitecture) ? <div/>: <p style={{color:'#DB3737'}}>Must be a prototxt file.</p>}
              <label class="pt-file-upload">
              <input type="file" accept=".prototxt" onChange={(event) => this.addArchitecture(event.target.files[0])}/>
              <span class="pt-file-upload-input">{(this.state.architecture != null) ? this.state.architecture.name : 'Choose file...'}</span>
              </label>
            </label>
            <label class="pt-label">
            <h5>Weights File</h5>
            <p>This is the file containing the weights and biases of the network.</p>
            {(this.state.validModel) ? <div/>: <p style={{color:'#DB3737'}}>Must be a caffemodel file.</p>}
            <label class="pt-file-upload">
            <input type="file" accept=".caffemodel" onChange={(event) => this.addModel(event.target.files[0])}/>
            <span class="pt-file-upload-input">{(this.state.model != null) ? this.state.model.name : 'Choose file...'}</span>
            </label>

          </label>
          <label class="pt-label">
          <h5>Class Labels </h5>
          <p>Class labels for the network. Though not required, it makes it easy to see what class the network recognises. This should be a file with a line for each class name.</p>
          {(this.state.validLabels) ? <div/> : <p style={{color:'#DB3737'}}>Must be a text file.</p>}
          <label class="pt-file-upload">
          <input type="file" accept=".txt" onChange={(event) => this.addLabels(event.target.files[0])}/>
          <span class="pt-file-upload-input">{(this.state.labels != null) ? this.state.labels.name : 'Choose file...'}</span>
          </label>
        </label>
        <button type="button" className="pt-button pt-icon-add" onClick={() => this.upload()}>Upload Model</button>
              </div>
          </Overlay>
    );
  }
}
