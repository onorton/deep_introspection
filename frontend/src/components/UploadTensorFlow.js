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
      console.log('sup')
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
    console.log(this.state.data)

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
          <p>This is checkpoint file for the network.</p>
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
