import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'

const blobSize = 5242880

export default class UploadTensorFlow extends Component {

  constructor(props) {
    super(props);
    this.state = {
      validMeta: true,
      meta: null,
      validData: true,
      data: null,
      validIndex: true,
      index: null,
      validCheckpoint: true,
      checkpoint: null,
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

  isValidData(filename) {
    var parts = filename.split('.');
    const ext = parts[parts.length - 1];
    return ext.toLowerCase().startsWith('data');
  }

  addMeta(file) {
    this.setState({validMeta: this.isValidFile(file.name,'meta')})
    if (this.state.validMeta) {
      this.setState({meta: file})
    }
  }

  addData(file) {
    this.setState({validData: this.isValidData(file.name)})
    if (this.state.validData) {
      this.setState({data: file})
    }
  }

  addCheckpoint(file) {
    this.setState({validCheckpoint: file.name.split('.').length == 1})
    if (this.state.validCheckpoint) {
      this.setState({checkpoint: file})
    }
  }

  addIndex(file) {
    this.setState({validIndex: this.isValidFile(file.name,'index')})
    if (this.state.validIndex) {
      this.setState({index: file})
    }
  }

  addLabels(file) {
    this.setState({validLabels: this.isValidFile(file.name,'txt')})
    if (this.state.validLabels) {
      this.setState({labels: file})
    }
  }

  uploadMeta() {
    // Send request to backend
    let overlay = this;
    let modelName =  overlay.state.meta.name.split('.')[0]
    let numBlobs = Math.floor(this.state.meta.size/blobSize)+1
    var count = numBlobs;
    for (var i = 0; i < numBlobs; i++) {
      (function(file, i) {
      var reader = new FileReader();
      reader.readAsDataURL(overlay.state.meta.slice(i*blobSize,(i+1)*blobSize));
      reader.onload = function () {
      // If successfully read file, save on file system
      fetch('http://127.0.0.1:8000/uploadModel/tensorflow/architecture/', {
        method: 'POST',
        body: JSON.stringify({name: modelName, filename: overlay.state.meta.name, part: reader.result, blobNum: i}),
        headers: {
            "Content-Type": "application/json"
        },
        credentials: 'same-origin'
      }).then(function(response) {
        count--;
        // send message to server letting it know all the meta has been sent.
        if (count == 0) {
          fetch('http://127.0.0.1:8000/uploadModel/tensorflow/architecture/', {
            method: 'POST',
            body: JSON.stringify({name: modelName,  filename: overlay.state.meta.name, blobNum: -1}),
            headers: {
                "Content-Type": "application/json"
            },
            credentials: 'same-origin'
          }).then(function(response){
            if (response.status == 200) {
              MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "MetaGraph file uploaded." });
              response.json().then(function(data) {
                overlay.uploadData()
              })

            }
          }).catch(function(error) {
            console.log('Problem assembling file: ' + error.message);
          });
        }
        return response.json();
      }).catch(function(error) {
        console.log('There has been a problem with uploading a part' + error.message);
      })
    }

    reader.onerror = function (error) {
     console.log('Error: ', error);
    };
  })
  (this.state.meta.slice(i*blobSize,(i+1)*blobSize), i)
    }
  }


  uploadData() {
    // Send request to backend
    this.props.updateProgress(5)
    let overlay = this;
    let modelName =  overlay.state.meta.name.split('.')[0]
    let numBlobs = Math.floor(this.state.data.size/blobSize)+1
    var count = numBlobs;
    for (var i = 0; i < numBlobs; i++) {
      (function(file, i) {
      var reader = new FileReader();
      reader.readAsDataURL(overlay.state.data.slice(i*blobSize,(i+1)*blobSize));
      reader.onload = function () {
      // If successfully read file, save on file system
      fetch('http://127.0.0.1:8000/uploadModel/tensorflow/data/', {
        method: 'POST',
        body: JSON.stringify({name: modelName, filename: overlay.state.data.name, part: reader.result, blobNum: i}),
        headers: {
            "Content-Type": "application/json"
        },
        credentials: 'same-origin'
      }).then(function(response) {
        count--;
        overlay.props.updateProgress(100*(numBlobs-count)/numBlobs)
        // send message to server letting it know all the data has been sent.
        if (count == 0) {
          fetch('http://127.0.0.1:8000/uploadModel/tensorflow/data/', {
            method: 'POST',
            body: JSON.stringify({name: modelName,  filename: overlay.state.data.name, blobNum: -1}),
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
  (this.state.data.slice(i*blobSize,(i+1)*blobSize), i)
    }
  }

  upload() {
      let overlay = this

      if (this.state.meta == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No MetaGraph file submitted." });
        return
      }
      if (this.state.data == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No data file submitted." });
        return
      }
      if (this.state.checkpoint == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No checkpoint file submitted." });
        return
      }
      if (this.state.index == null) {
        MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "No index file submitted." });
        return
      }

      let modelName =  overlay.state.meta.name.split('.')[0]
      this.uploadMeta()

      // Submit Index and Checkpoint files

      var indexReader = new FileReader();
      indexReader.readAsDataURL(overlay.state.index);
      indexReader.onload = function () {

        var checkpointReader = new FileReader();
        checkpointReader.readAsDataURL(overlay.state.checkpoint);
        checkpointReader.onload = function () {
          // If successfully read file, save on file system
        fetch('http://127.0.0.1:8000/uploadModel/tensorflow/rest/', {
          method: 'POST',
          body: JSON.stringify({name: modelName, checkpoint_filename:overlay.state.checkpoint.name, index_filename: overlay.state.index.name, checkpoint: checkpointReader.result, index_file: indexReader.result}),
          headers: {
              "Content-Type": "application/json"
          },
          credentials: 'same-origin'
        }).then(function(response) {
          if (response.status == 200) {
            MainToaster.show({ timeout:5000, intent: Intent.SUCCESS, message: "Index and checkpoint files submitted." });
          }
          return response.json();
        }).catch(function(error) {
          console.log('There has been a problem with your fetch operation: ' + error.message);
        });

        }

        checkpointReader.onerror = function (error) {
         console.log('Error: ', error);
        };

    };
  indexReader.onerror = function (error) {
   console.log('Error: ', error);
  };

      // Submit labels file
      if (overlay.state.labels != null) {
        var labelsReader = new FileReader();
        labelsReader.readAsDataURL(overlay.state.labels);
        labelsReader.onload = function () {
      // If successfully read file, save on file system
      fetch('http://127.0.0.1:8000/uploadModel/tensorflow/labels/', {
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
}
  reset() {
    const initialState = {
      validMeta: true,
      meta: null,
      validData: true,
      data: null,
      validIndex: true,
      index: null,
      validCheckpoint: true,
      checkpoint: null,
      validLabels: true,
      labels: null
    };
    this.setState(initialState)
  }

  render(){
    return (
      <div>
              <label class="pt-label">
              <h5>MetaGraph File</h5>
              <p>This is the *.meta file that defines the MetaGraph of the network.</p>
              {(this.state.validMeta) ? <div/>: <p style={{color:'#DB3737'}}>Must be a MetaGraph file.</p>}
              <label class="pt-file-upload">
              <input type="file" accept=".meta" onChange={(event) => this.addMeta(event.target.files[0])}/>
              <span class="pt-file-upload-input">{(this.state.meta != null) ? this.state.meta.name : 'Choose file...'}</span>
              </label>
            </label>

            <label class="pt-label">
            <h5>Data File</h5>
            <p>This is the file containing the data of the network.</p>
            {(this.state.validData) ? <div/>: <p style={{color:'#DB3737'}}>Must be a TensorFlow data file.</p>}
            <label class="pt-file-upload">
            <input type="file" onChange={(event) => this.addData(event.target.files[0])}/>
            <span class="pt-file-upload-input">{(this.state.data != null) ? this.state.data.name : 'Choose file...'}</span>
            </label>
          </label>

          <label class="pt-label">
          <h5>Index File</h5>
          <p>This is the index file of the tensors for the network.</p>
          {(this.state.validIndex) ? <div/>: <p style={{color:'#DB3737'}}>Must be a TensorFlow index file.</p>}
          <label class="pt-file-upload">
          <input type="file" accept=".index" onChange={(event) => this.addIndex(event.target.files[0])}/>
          <span class="pt-file-upload-input">{(this.state.index != null) ? this.state.index.name : 'Choose file...'}</span>
          </label>
          </label>


          <label class="pt-label">
          <h5>Checkpoint File</h5>
          <p>This is the checkpoint file for the network.</p>
          {(this.state.validCheckpoint) ? <div/>: <p style={{color:'#DB3737'}}>Must be a valid checkpoint file.</p>}
          <label class="pt-file-upload">
          <input type="file" onChange={(event) => this.addCheckpoint(event.target.files[0])}/>
          <span class="pt-file-upload-input">{(this.state.checkpoint != null) ? this.state.checkpoint.name : 'Choose file...'}</span>
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
