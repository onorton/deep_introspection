import React, { Component } from 'react';
import { Dialog, Tooltip, Position, Intent, Tabs2, Tab2} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster.js'
import UploadCaffe from './UploadCaffe'
import UploadTensorFlow from './UploadTensorFlow'

const blobSize = 5242880

export default class UploadModelOverlay extends Component {

  constructor(props) {
    super(props);
    this.state = {
      isOpen: props.isOpen,
      percentage: null,
      type: 'ca'
    };
  }

  componentWillReceiveProps(nextProps) {
    this.setState({isOpen:nextProps.isOpen})
  }

  changeTab(id) {
    this.setState({type:id})
    this.handleTabChange
  }

  upload() {
    switch(this.state.type) {
      case 'ca': this.caffe.upload(); break;
      case 'tf': this.tensorflow.upload(); break;
    }
  }

  reset() {
    const initialState = {
      isOpen: false,
      percentage: null,
      type: 'ca'
    };
    this.setState(initialState)
    this.props.reset()
  }


  render(){


    return (
          <Dialog isOpen={this.state.isOpen} title="Add Model"
            style={{backgroundColor:"#F5F8FA"}}
            canEscapeClose={this.state.percentage == null}
            canOutsideClickClose={this.state.percentage == null}
            isCloseButtonShown={this.state.percentage == null}
            onClose={evt => this.reset()}
            >
             {(this.props.first) ? <p style={{paddingLeft:15, paddingRight: 15, paddingTop: 15}}>Before using Deep Introspection, you need to upload a network model to analyse.</p> : <div/>}
             <div  style={{padding: 15}}>
             <Tabs2 id="typeTabs" onChange={(newId, prevId, evt) => this.changeTab(newId)}>
              <Tab2 id="ca" title={<h5>Caffe</h5>} panel={<UploadCaffe onRef={ref => (this.caffe = ref)} updateProgress={(percentage) => this.setState({percentage:percentage})} callbackParent={(model) => this.props.callbackParent(model)}/>} />
              <Tab2 id="tf" title={<h5>TensorFlow</h5>} panel={<UploadTensorFlow onRef={ref => (this.tensorflow = ref)} updateProgress={(percentage) => this.setState({percentage:percentage})} callbackParent={(model) => this.props.callbackParent(model)}/>}/>
            </Tabs2>
            </div>


        <div className="pt-dialog-footer" >
                    {(this.state.percentage != null) ?
                      <div class="pt-progress-bar pt-intent-primary" style={{width: "65%"}}>
                        <div class="pt-progress-meter" style={{width: this.state.percentage+"%"}}></div>
                      </div> : <div/>
                    }
                       <div className="pt-dialog-footer-actions">
                       <button type="button" className="pt-button pt-icon-add" onClick={() => this.upload()} style={{marginTop:-20}}>Upload Model</button>
                       </div>
                   </div>
          </Dialog>
    );
  }
}
