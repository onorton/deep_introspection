import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';
import Cookies from 'js-cookie';
import { Position, Toaster, Intent , Collapse} from "@blueprintjs/core";
import {MainToaster} from '../MainToaster'

import UploadModelOverlay from './UploadModelOverlay'

export default class ModelCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
      models: [],
      selected: 0,
      add: false,
      open: true,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.user == null && nextProps.user != null) {
      this.fetchModels(nextProps.user)
    }

    if (nextProps.user == null) {
      this.setState({models: [], selected: 0})
    }
  }

  fetchModels(user) {
    const collection = this
    fetch('/uploadModel/', {
      method: 'GET',
      headers: {
          "Content-Type": "application/json"
      },
      credentials:'same-origin'
    }).then(function(response) {
      if (response.status == 200) {
        response.json().then(function(data) {
          collection.setState({models: data.models})
          collection.props.callbackParent(data.models[0])
        })
      } else if (response.status == 404) {
        collection.setState({add:true})
      }
    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });

  }

  select(index) {
    this.props.callbackParent(this.state.models[index])
    this.setState({selected:index})
  }

  onModelUploaded(model) {
    const models = this.state.models
    if (models.length == 0) {
      this.props.callbackParent(model)
    }

    models.push(model)
    this.setState({models: models, add:false})

  }

  render(){
    let collection = this;
    let selected = this.state.selected;
    let selectedStyle = { outlineColor: '#137CBD', outlineStyle: 'solid',  width: '90%'}
    let modelStyle = {width: '90%'}
    return (
      <div>
      <UploadModelOverlay isOpen={this.props.user != null && this.state.add} first={this.state.models.length == 0} reset={() => this.setState({add:false})} callbackParent={(model) => this.onModelUploaded(model)}/>
      <div style={this.props.style}>
        <div style={{backgroundColor: '#BFCCD6'}}>
        <div className="pt-card" style={{backgroundColor: '#5C7080', borderStyle:'solid', borderWidth:'2px', borderColor:'#394B59', height:40, padding:5, position:'relative'}}>
        <div className="clickable" onClick={() => this.setState({open:!this.state.open})}><span  style={{color:'#FFFFFF', fontSize:'15pt'}}>Test Models</span></div>
        <span style={{float:'right', marginTop: -22, cursor:'pointer'}} className="pt-interactive pt-icon-add pt-icon-large" onClick={() => collection.setState({add: true})}></span>
        </div>

        <Collapse isOpen={this.state.open}>
        {this.state.models.length == 0 ? (
        <div class="pt-non-ideal-state" style={{height:80, paddingTop:90}}>
          <div class="pt-non-ideal-state-visual pt-non-ideal-state-icon">
            <span class="pt-icon pt-icon-media"></span>
          </div>
          <h4 class="pt-non-ideal-state-title">There are no test models</h4>
          <div class="pt-non-ideal-state-description">
            Add a new model to get started.
          </div>
        </div>) : <div/>}

        <Scrollbars style={{width: this.props.style.width, height:this.props.scrollHeight}}>
          <ul style={{listStyleType: 'none', padding: 0, position:'relative'}}>
           {
             this.state.models.map(function(model, index){
           return <li style={{padding: '2px 0px 2px 0px'}}><label onClick={() => collection.select(index)} style={(index == selected) ? selectedStyle : modelStyle} className="pt-button">{model.name}</label></li>;
                   })}
           </ul>
        </Scrollbars>
        </Collapse>

      </div>
      </div>
      </div>
    );
  }
}
