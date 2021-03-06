import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import styles from '../node_modules/@blueprintjs/core/dist/blueprint.css';

import ImageCollection from './components/ImageCollection'
import ModelCollection from './components/ModelCollection'

import UploadModelOverlay from './components/UploadModelOverlay'
import LoginOverlay from './components/LoginOverlay'
import FeedbackOverlay from './components/FeedbackOverlay'

import ToolCollection from './components/ToolCollection'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      testImage: null,
      testModel: null,
      feedback: false,
      user: null,
      username: null
    };
  }

  onTestModelChanged(model) {
    this.setState({testModel:model})
  }

  onTestImageChanged(img) {
    this.setState({testImage:img})
  }

  logout() {
    const app = this
    fetch('/accounts/logout', {
      method: 'POST',
      headers: {
          "Content-Type": "application/json"
      },
      credentials: "same-origin",

    }).then(function(response) {
      if (response.status == 200) {
        app.setState({user:null,testImage:null,testModel:null})
      }
    }).catch(function(error) {
      console.log('There has been a problem with your fetch operation: ' + error.message);
    });
  }

  render() {
    console.log(this.state.user)
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title" style={{color:'#FFFFFF'}}>Deep Introspection</h1>

        <div style={{color:'#FFFFFF',float:'right'}}>Hello, {this.state.username != null ? this.state.username:'guest'}<label style={{marginLeft:5}} className="pt-file-upload pt-button pt-icon-log-out pt-intent-primary " onClick={() => {this.logout()}}>Logout</label></div>
        </header>
        <LoginOverlay isOpen={this.state.user == null} callbackParent={(user) => this.setState({user:user.id,username:user.username})}/>
        <div className="main-content" style={{position:"absolute", paddingLeft: 260, top: 125, width:"100%" }}>
          {(this.state.testImage != null && this.state.testModel != null) ? <ToolCollection testImage={this.state.testImage} testModel={this.state.testModel}/> : <div/>}
        </div>
        <label style={{position:'absolute', top:'50%', right:-25, transform:'rotate(-90deg)'}}className="pt-button pt-intent-primary pt-large" onClick={() => {this.setState({feedback:true})}}>Feedback</label>
        <FeedbackOverlay isOpen={this.state.feedback} image={this.state.testImage} model={this.state.testModel} onClose={() => this.setState({feedback:false})}/>
        <ModelCollection user={this.state.user} callbackParent={(model) => this.onTestModelChanged(model)} scrollHeight={100} style={{position:'absolute', top:80, left:250, width:200}}/>
        <ImageCollection user={this.state.user} callbackParent={(img) => this.onTestImageChanged(img)} style={{width:250, height:750}}/>
      </div>

    );
  }
}

export default App;
