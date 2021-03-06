import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'

const blobSize = 5242880

export default class UploadCaffe extends Component {

  constructor(props) {
    super(props);
    this.state = {
      validArchitecture: true,
      architecture: null,
      validModel: true,
      model: null,
      validLabels: true,
      labels: null
    };
  }

  componentDidMount() {
    this.props.onRef(this)
  }
  componentWillUnmount() {
    this.props.onRef(undefined)
  }

  componentWillReceiveProps(nextProps) {
    this.setState({isOpen:nextProps.isOpen})
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

  uploadWeights() {
    // Send request to backend
    this.props.updateProgress(5)
    let overlay = this;
    let modelName =  overlay.state.architecture.name.split('.')[0]
    let numBlobs = Math.floor(this.state.model.size/blobSize)+1
    var count = numBlobs;
    for (var i = 0; i < numBlobs; i++) {
      (function(file, i) {
      var reader = new FileReader();
      reader.readAsDataURL(overlay.state.model.slice(i*blobSize,(i+1)*blobSize));
      reader.onload = function () {
      // If successfully read file, save on file system
      fetch('/uploadModel/caffe/weights/', {
        method: 'POST',
        body: JSON.stringify({name: modelName, filename: overlay.state.model.name, part: reader.result, blobNum: i}),
        headers: {
            "Content-Type": "application/json"
        },
        credentials: 'same-origin'
      }).then(function(response) {
        count--;
        overlay.props.updateProgress(100*(numBlobs-count)/numBlobs)
        // send message to server letting it know all the data has been sent.
        if (count == 0) {
          fetch('/uploadModel/caffe/weights/', {
            method: 'POST',
            body: JSON.stringify({name: modelName,  filename: overlay.state.model.name, blobNum: -1}),
            headers: {
                "Content-Type": "application/json"
            },
            credentials: 'same-origin'
          }).then(function(response){
            if (response.status == 200) {
              MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "Weights file uploaded." });
              response.json().then(function(data) {
                overlay.props.callbackParent({name: modelName, id: data.id})
                overlay.reset()
              })

            }
          }).catch(function(error) {
            console.log('Problem assembling file: ' + error.message);
          });
        }
        return response.json();
      }).catch(function(error) {
        console.log('There has been a problem with your fetch operation: ' + error.message);
      })
    }

    reader.onerror = function (error) {
     console.log('Error: ', error);
    };
  })
  (this.state.model.slice(i*blobSize,(i+1)*blobSize), i)
    }
  }

  upload() {
      let overlay = this

      if (this.state.architecture == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No architecture file submitted." });
        return
      }
      if (this.state.model == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No weights file submitted." });
        return
      }

      let modelName =  overlay.state.architecture.name.split('.')[0]
      var architectureReader = new FileReader();
      architectureReader.readAsDataURL(overlay.state.architecture);
      architectureReader.onload = function () {
      // If successfully read file, save on file system
      fetch('/uploadModel/caffe/architecture/', {
        method: 'POST',
        body: JSON.stringify({name: modelName, filename: overlay.state.architecture.name, file: architectureReader.result}),
        headers: {
            "Content-Type": "application/json"
        },
        credentials: 'same-origin'
      }).then(function(response) {
        if (response.status == 200) {
          MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "Architecture file submitted." });
          if (overlay.state.labels != null) {
            var labelsReader = new FileReader();
            labelsReader.readAsDataURL(overlay.state.labels);
            labelsReader.onload = function () {
          // If successfully read file, save on file system
          fetch('/uploadModel/caffe/labels/', {
            method: 'POST',
            body: JSON.stringify({name: modelName, filename:  overlay.state.labels.name, file: labelsReader.result}),
            headers: {
                "Content-Type": "application/json"
            },
            credentials: 'same-origin'
          }).then(function(response) {
            if (response.status == 200) {
              MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "Class labels file submitted." });
            }
            return response.json();
          }).catch(function(error) {
            console.log('There has been a problem with your fetch operation: ' + error.message);
          });
          };
        labelsReader.onerror = function (error) {
         console.log('Error: ', error);
        };
      }
        overlay.uploadWeights()
      } else if (response.status == 409) {
        MainToaster.show({ timeout:5000, intent: Intent.WARNING, message: "You have already uploaded this model." });
      }
        return response.json();
      }).catch(function(error) {
        console.log('There has been a problem with your fetch operation: ' + error.message);
      });
      };
    architectureReader.onerror = function (error) {
     console.log('Error: ', error);
    };
  }

  reset() {
    const initialState = {
      validArchitecture: true,
      architecture: null,
      validModel: true,
      model: null,
      validLabels: true,
      labels: null
    };
    this.setState(initialState)
  }

  render(){


    return (
      <div>
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
        </div>

    );
  }
}
