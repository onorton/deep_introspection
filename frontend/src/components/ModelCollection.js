import React, { Component } from 'react';
import { Scrollbars } from 'react-custom-scrollbars';
import Cookies from 'js-cookie';
import { Position, Toaster, Intent } from "@blueprintjs/core";
import {MainToaster} from '../MainToaster'

export default class ModelCollection extends Component {

  constructor(props) {
    super(props);
    this.state = {
      models: [],
      selected: 0
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
    fetch('http://127.0.0.1:8000/uploadModel/', {
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
      }
    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });

  }

  select(index) {
    this.props.callbackParent(this.state.models[index])
    this.setState({selected:index})
  }
  //
  // saveModel(img) {
  //   const urls = this.state.models;
  //   const name = img.name;
  //   const collection = this;
  //   // Check that file has model extension, alert user if not
  //   if (!this.isModel(name)) {
  //     MainToaster.show({ timeout:5000, intent: Intent.DANGER, message: "This file is not an model!" });
  //     return;
  //   }
  //   // Send request to backend
  //   var reader = new FileReader();
  //   reader.readAsDataURL(img);
  //   reader.onload = function () {
  //     // If successfully read model, save on file system
  //
  //     fetch('http://127.0.0.1:8000/uploadModel/', {
  //       method: 'POST',
  //       body: JSON.stringify({name: name, model: reader.result}),
  //       headers: {
  //           "Content-Type": "application/json"
  //       },
  //       credentials:'same-origin'
  //
  //     }).then(function(response) {
  //
  //       if (response.status == 200) {
  //         response.json().then(function(data) {
  //           urls.push({id: data.id, url: 'http://127.0.0.1:8000/media/models/' + data.filename});
  //           collection.setState({models: urls})
  //           if(collection.state.models.length == 1) {
  //             collection.select(0);
  //           }
  //
  //         })
  //       } else if (response.status == 409) {
  //         MainToaster.show({ timeout:5000, intent: Intent.WARNING, message: "You have already uploaded this model." });
  //       }
  //
  //     }).catch(function(error) {
  //       console.log('There has been a problem with your fetch operation: ' + error.message);
  //     });
  //
  //
  //     };
  //   reader.onerror = function (error) {
  //    console.log('Error: ', error);
  //   };
  //
  // }

  render(){
    let collection = this;
    let selected = this.state.selected;
    let selectedStyle = { outlineColor: '#137CBD', outlineStyle: 'solid',  width: '90%'}
    let modelStyle = {width: '90%'}

    return (
      <div style={this.props.style}>
        <div style={{backgroundColor: '#BFCCD6'}}>
        <div className="pt-card" style={{backgroundColor: '#5C7080', borderStyle:'solid', borderWidth:'2px', borderColor:'#394B59'}}>
        <h2 style={{color:'#FFFFFF', paddingBottom:'5px'}}>Test Models</h2>
        <label style={{width: '115px'}} className="pt-file-upload pt-button pt-icon-add ">Add Model</label>
        </div>
        {this.state.models.length == 0 ? (

        <div class="pt-non-ideal-state" style={{height:150, paddingTop:20}}>
        <div class="pt-non-ideal-state-visual pt-non-ideal-state-icon">
        <span class="pt-icon pt-icon-media"></span>
        </div>
        <h4 class="pt-non-ideal-state-title">There are no test models</h4>
        <div class="pt-non-ideal-state-description">
          Add a new model to get started.
          </div>
        </div>) : <div></div>}
        <Scrollbars style={this.props.style}>
          <ul style={{listStyleType: 'none', padding: 0, margin: 0}}>
           {
             this.state.models.map(function(model, index){
           return <li style={{padding: '5px 0px 5px 0px'}}><label onClick={() => collection.select(index)} style={(index == selected) ? selectedStyle : modelStyle} className="pt-file-upload pt-button">{model.name}</label></li>;
                   })}
           </ul>
        </Scrollbars>
      </div>
      </div>
    );
  }
}
